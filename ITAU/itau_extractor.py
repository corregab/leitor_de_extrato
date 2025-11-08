#!/usr/bin/env python3
"""
Extrator de créditos de extratos do Itaú.
Este script é especializado em extrair valores de crédito (entradas positivas) de extratos do Itaú,
identificando especificamente os valores que aparecem em verde no extrato original.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any
from decimal import Decimal, ROUND_DOWN, InvalidOperation

import pdfplumber


@dataclass
class CreditEntry:
    """Representa uma entrada de crédito no extrato."""
    date: str
    description: str
    amount: Decimal
    transaction_type: str
    raw_line: str
    page: int

    def to_dict(self) -> Dict[str, Any]:
        """Converte a entrada para um dicionário."""
        return {
            'date': self.date,
            'description': self.description,
            'amount': str(self.amount.quantize(Decimal('.01'), rounding=ROUND_DOWN)),
            'transaction_type': self.transaction_type,
            'raw_line': self.raw_line,
            'page': self.page
        }


class ItauExtractParser:
    """Parser especializado para extratos do Itaú."""
    
    # Padrões de expressões regulares para extração
    # Aceita datas nos formatos dd/mm/aaaa e dd/mm/aa (alguns PDFs variam)
    # Prioriza ano com 4 dígitos; aceita também com 2 dígitos
    DATE_PATTERN = re.compile(r'(\d{2}/\d{2}/(?:\d{4}|\d{2}))')
    AMOUNT_PATTERN = re.compile(r'(\d{1,3}(?:\.\d{3})*,\d{2})')
    
    # Tipos de transação que representam créditos
    CREDIT_TYPES = {
        'PIX QRS': 'PIX',
        'PIX TRANSF': 'PIX',
        'PIX RECEBIDO': 'PIX',
        'TED RECEBIDA': 'TED',
        'DOC RECEBIDO': 'DOC',
        'DEPOSITO': 'DEPÓSITO'
    }
    # Color detection thresholds (tweakable)
    COLOR_MIN = 0.25      # componente mínimo para considerar cor predominante (0..1)
    COLOR_DIFF = 0.03     # diferença mínima entre componente predominante e os outros

    @staticmethod
    def is_credit_line(line: str) -> bool:
        """
        Verifica se uma linha contém uma transação de crédito.
        No Itaú, créditos são valores positivos (sem sinal de menos).
        """
        # Remove espaços extras e converte para maiúsculas para comparação
        line = ' '.join(line.strip().split())
        line_upper = line.upper()

        # Se a linha começa com - ou tem -R$, é um débito
        if line.startswith('-') or '-R$' in line:
            return False

        # Verifica se é um tipo conhecido de crédito
        for credit_type in ItauExtractParser.CREDIT_TYPES:
            if credit_type in line_upper:
                return True

        return False

    @staticmethod
    def parse_amount(amount_str: str) -> Decimal:
        """Converte uma string de valor monetário para Decimal."""
        # Remove R$ e espaços, substitui , por . para conversão
        clean_amount = amount_str.replace('R$', '').replace('.', '').replace(',', '.').strip()
        return Decimal(clean_amount)

    @staticmethod
    def clean_description(line: str) -> str:
        """Limpa a descrição da transação, removendo dados desnecessários."""
        # Remove valores monetários, datas e espaços extras
        desc = ItauExtractParser.AMOUNT_PATTERN.sub('', line)
        desc = ItauExtractParser.DATE_PATTERN.sub('', desc)
        desc = re.sub(r'\s+', ' ', desc).strip()
        return desc

    @staticmethod
    def get_transaction_type(line: str) -> str:
        """Identifica o tipo de transação com base no texto da linha."""
        line_upper = line.upper()
        for credit_type, type_name in ItauExtractParser.CREDIT_TYPES.items():
            if credit_type in line_upper:
                return type_name
        return 'OUTROS'

    def parse_line(self, line: str, page: int, page_obj=None, debug=False) -> Optional[CreditEntry]:
        """
        Analisa uma linha do extrato e retorna uma entrada de crédito se for válida.
        """
        if debug:
            print(f"[DEBUG] Analisando linha: {line[:100]}")
            
        if not self.is_credit_line(line):
            if debug:
                print(f"[DEBUG] ❌ Não é linha de crédito")
            return None

        # Extrai a data
        date_match = self.DATE_PATTERN.search(line)
        if not date_match:
            if debug:
                print(f"[DEBUG] ❌ Data não encontrada")
            return None
        date = date_match.group(1)
        # Normaliza ano com 2 dígitos para 20YY
        # Ex.: 02/06/25 -> 02/06/2025
        if len(date.split('/')[-1]) == 2:
            d, m, yy = date.split('/')
            date = f"{d}/{m}/20{yy}"

        # Extrai o valor
        amount_match = self.AMOUNT_PATTERN.search(line)
        if not amount_match:
            if debug:
                print(f"[DEBUG] ❌ Valor não encontrado")
            return None
        
        try:
            amount = self.parse_amount(amount_match.group(1))
        except (ValueError, InvalidOperation):
            if debug:
                print(f"[DEBUG] ❌ Erro ao converter valor")
            return None

        # Detecta se há um sinal de menos imediatamente antes do valor no texto bruto
        # (ex.: "-27,00" ou "- 27,00"). Nesse caso trata como débito e ignora.
        amt_text = amount_match.group(1)
        if re.search(r'[-−]\s*' + re.escape(amt_text), line):
            if debug:
                print(f"[DEBUG] ❌ Encontrado sinal de menos antes do valor")
            return None

        # Identifica o tipo de transação ANTES de checar cor
        transaction_type = self.get_transaction_type(line)
        is_known_credit_type = (transaction_type != 'OUTROS')

        # Se disponível, tenta inferir a cor do texto do valor na página PDF.
        # IMPORTANTE: Se for um tipo conhecido de crédito (PIX, TED, etc.), 
        # NÃO ignora mesmo se estiver vermelho, pois pode ser erro de formatação do PDF.
        if page_obj is not None and not is_known_credit_type:
            try:
                amt_text = amount_match.group(1)
                color = self._find_color_for_text_on_page(page_obj, amt_text)
                if color is not None:
                    if self._is_red(color):
                        # Texto em vermelho = saída (não é crédito)
                        # MAS só ignora se NÃO for um tipo conhecido de crédito
                        return None
                    # if green -> prefer credit (continue)
            except Exception:
                # Qualquer falha ao checar cor não impede o parsing baseado em texto
                pass

        # Se o valor for negativo ou zero, não é um crédito
        if amount <= 0:
            return None

        # Obtém a descrição limpa
        description = self.clean_description(line)

        return CreditEntry(
            date=date,
            description=description,
            amount=amount,
            transaction_type=transaction_type,
            raw_line=line.strip(),
            page=page
        )

    def extract_credits(self, pdf_path: str) -> List[CreditEntry]:
        """
        Extrai todas as entradas de crédito de um arquivo PDF de extrato do Itaú.
        """
        credits = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                if not text:
                    continue

                # Carrega caracteres da página (quando disponíveis) para checar cor
                page_chars = getattr(page, 'chars', None) or []

                for line in text.splitlines():
                    credit_entry = self.parse_line(line.strip(), page_num, page_obj=page)
                    if credit_entry:
                        credits.append(credit_entry)

        return credits

    # ---------- cor / cor do texto helpers ----------
    @staticmethod
    def _normalize_color_value(v):
        """Normaliza componentes de cor para o intervalo 0..1.
        Aceita tuplas com valores 0..1 ou 0..255 e strings; retorna (r,g,b) ou None.
        """
        if v is None:
            return None
        # se já é tupla/list
        if isinstance(v, (list, tuple)) and len(v) >= 3:
            r, g, b = v[0], v[1], v[2]
            try:
                # se em 0..255
                if max(r, g, b) > 1:
                    return (r / 255.0, g / 255.0, b / 255.0)
                return (float(r), float(g), float(b))
            except Exception:
                return None
        # se for string como 'rgb(0.00,1.00,0.00)'
        if isinstance(v, str):
            nums = re.findall(r"[0-9]+(?:\.[0-9]+)?", v)
            if len(nums) >= 3:
                vals = [float(x) for x in nums[:3]]
                if max(vals) > 1:
                    return tuple(x / 255.0 for x in vals)
                return tuple(vals)
        # se for float (cinza)
        if isinstance(v, (int, float)):
            val = float(v)
            if val > 1:
                val = val / 255.0
            return (val, val, val)
        return None

    @staticmethod
    def _is_green(color_tuple) -> bool:
        """Decide se a cor (r,g,b) é verde predominante."""
        c = ItauExtractParser._normalize_color_value(color_tuple)
        if not c:
            return False
        r, g, b = c
        return (g > ItauExtractParser.COLOR_MIN) and (g > r + ItauExtractParser.COLOR_DIFF) and (g > b + ItauExtractParser.COLOR_DIFF)

    @staticmethod
    def _is_red(color_tuple) -> bool:
        """Decide se a cor (r,g,b) é vermelha predominante."""
        c = ItauExtractParser._normalize_color_value(color_tuple)
        if not c:
            return False
        r, g, b = c
        return (r > ItauExtractParser.COLOR_MIN) and (r > g + ItauExtractParser.COLOR_DIFF) and (r > b + ItauExtractParser.COLOR_DIFF)

    def _find_color_for_text_on_page(self, page, target_text: str):
        """Procura na lista de caracteres (`page.chars`) uma sequência que forme `target_text`.
        Retorna a primeira cor encontrada (não_stroking_color) como agregado (most common),
        ou None se não houver informação de cor.
        """
        # Normaliza target (mantém pontos e vírgulas)
        target = target_text
        chars = getattr(page, 'chars', [])
        if not chars:
            return None

        # Concatena sequências de caracteres tentando igualar target (comparação simples)
        n = len(chars)
        for i in range(n):
            s = ''
            colors = []
            for j in range(i, min(n, i + 40)):
                ch = chars[j]
                s += ch.get('text', '')
                # coleta cor se disponível
                col = ch.get('non_stroking_color') or ch.get('stroking_color')
                if col is not None:
                    colors.append(col)
                if s == target:
                    # achou correspondência exata
                    if not colors:
                        return None
                    # retorna a cor mais frequente
                    # normaliza e escolhe média aproximada
                    # para simplicidade, retornamos o primeiro significativo
                    for c in colors:
                        norm = self._normalize_color_value(c)
                        if norm is not None:
                            return norm
                    return None
                # se já excedeu tamanho aproximado, break
                if len(s) > len(target) + 3:
                    break

        return None

        return credits


def save_csv(entries: List[CreditEntry], filepath: str) -> None:
    """Salva as entradas de crédito em um arquivo CSV."""
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Data', 'Descrição', 'Valor', 'Tipo', 'Linha Original', 'Página'])
        for entry in entries:
            writer.writerow([
                entry.date,
                entry.description,
                str(entry.amount.quantize(Decimal('.01'), rounding=ROUND_DOWN)),
                entry.transaction_type,
                entry.raw_line,
                entry.page
            ])


def save_json(entries: List[CreditEntry], filepath: str) -> None:
    """Salva as entradas de crédito em um arquivo JSON."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump([entry.to_dict() for entry in entries], f, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description='Extrai créditos (valores positivos) de um extrato do Itaú em PDF'
    )
    parser.add_argument('pdf', help='Caminho para o arquivo PDF do extrato')
    parser.add_argument(
        '--out', '-o',
        help='Arquivo de saída (csv ou json). Se omitido, imprime no stdout'
    )
    parser.add_argument(
        '--format', '-f',
        choices=['csv', 'json'],
        default='csv',
        help='Formato do arquivo de saída (padrão: csv)'
    )
    parser.add_argument(
        '--amounts-only',
        action='store_true',
        help='Imprime/salva somente os valores (um por linha) para copiar/colar no Excel'
    )
    parser.add_argument(
        '--decimal-comma', '--br',
        action='store_true',
        help='Usa vírgula como separador decimal (ex: 768,00)'
    )
    
    args = parser.parse_args()

    # Extrai os créditos do PDF
    parser = ItauExtractParser()
    try:
        entries = parser.extract_credits(args.pdf)
    except Exception as e:
        print(f'Erro durante a extração: {e}')
        return

    if not entries:
        print('Nenhum crédito encontrado no extrato.')
        return

    # Se for solicitado apenas os valores
    if args.amounts_only:
        amounts = [str(e.amount.quantize(Decimal('.01'), rounding=ROUND_DOWN)) for e in entries]
        if args.decimal_comma:
            amounts = [a.replace('.', ',') for a in amounts]
        
        if args.out:
            with open(args.out, 'w', encoding='utf-8') as f:
                for amount in amounts:
                    f.write(f'{amount}\n')
            print(f'Salvo {len(amounts)} valores em {args.out}')
        else:
            for amount in amounts:
                print(amount)
        return

    # Salva ou imprime os resultados completos
    if args.out:
        if args.format == 'csv' or args.out.lower().endswith('.csv'):
            save_csv(entries, args.out)
        else:
            save_json(entries, args.out)
        print(f'Salvo {len(entries)} créditos em {args.out}')
    else:
        # Imprime no formato tabular
        print('\nCréditos encontrados:')
        print('-' * 80)
        print(f'{"Data":<12} {"Tipo":<10} {"Valor":>12} {"Descrição":<40}')
        print('-' * 80)
        for entry in entries:
            amount_str = f'R$ {entry.amount:,.2f}'.replace(',', '@').replace('.', ',').replace('@', '.')
            print(f'{entry.date:<12} {entry.transaction_type:<10} {amount_str:>12} {entry.description[:40]:<40}')


if __name__ == '__main__':
    main()