#!/usr/bin/env python3
"""Extrator de créditos de extratos do Mercado Pago."""
from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass, asdict
from typing import List, Optional
from decimal import Decimal, ROUND_DOWN, InvalidOperation

import pdfplumber


@dataclass
class MercadoPagoTransaction:
    """Representa uma transação de crédito no extrato do Mercado Pago."""
    date: str
    description: str
    amount: Decimal
    transaction_type: str
    raw_line: str
    page: int


class MercadoPagoExtractor:
    """Extrator especializado para extratos do Mercado Pago."""
    
    # Padrões de regex
    DATE_PATTERN = re.compile(r'(\d{2}-\d{2}-\d{4})')
    AMOUNT_PATTERN = re.compile(r'R\$\s*([-]?\d{1,3}(?:\.\d{3})*,\d{2})')
    
    # Palavras-chave para identificar créditos
    CREDIT_KEYWORDS = ['RENDIMENTOS', 'RENDIMENTO', 'PIX RECEBIDO', 'RECEBIDO', 'TRANSFERÊNCIA RECEBIDA', 'TRANSFERENCIA RECEBIDA', 'DEPOSITO', 'DEPÓSITO']
    
    # Palavras-chave para excluir (débitos)
    DEBIT_KEYWORDS = ['PIX ENVIADA', 'ENVIADO', 'ENVIADA', 'PAGAMENTO', 'COMPRA', 'SAQUE', 'TARIFA', 'TAXA']
    
    # Palavras de resumo/totais para excluir
    SUMMARY_KEYWORDS = ['ENTRADAS:', 'SAIDAS:', 'SALDO INICIAL', 'SALDO FINAL', 'TOTAL']

    @staticmethod
    def parse_amount(amount_str: str) -> Decimal:
        """Converte string de valor para Decimal."""
        # Remove R$ e espaços
        clean = amount_str.replace('R$', '').strip()
        # Remove separador de milhares e troca vírgula por ponto
        clean = clean.replace('.', '').replace(',', '.')
        return Decimal(clean)

    @staticmethod
    def is_credit_line(line: str) -> bool:
        """Verifica se a linha representa um crédito."""
        line_upper = line.upper()
        
        # Exclui linhas de resumo/totais
        if any(kw in line_upper for kw in MercadoPagoExtractor.SUMMARY_KEYWORDS):
            return False
        
        # Exclui débitos
        if any(kw in line_upper for kw in MercadoPagoExtractor.DEBIT_KEYWORDS):
            return False
        
        # Aceita créditos conhecidos
        if any(kw in line_upper for kw in MercadoPagoExtractor.CREDIT_KEYWORDS):
            return True
        
        return False

    def extract_credits(self, pdf_path: str) -> List[MercadoPagoTransaction]:
        """Extrai todas as entradas de crédito do PDF."""
        credits = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                if not text:
                    continue
                
                lines = text.splitlines()
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Verifica se é linha de crédito
                    if not self.is_credit_line(line):
                        continue
                    
                    # Extrai data
                    date_match = self.DATE_PATTERN.search(line)
                    if not date_match:
                        continue
                    date = date_match.group(1)
                    
                    # Extrai valor
                    amount_match = self.AMOUNT_PATTERN.search(line)
                    if not amount_match:
                        continue
                    
                    try:
                        amount = self.parse_amount(amount_match.group(1))
                    except (ValueError, InvalidOperation):
                        continue
                    
                    # Só aceita valores positivos (créditos)
                    if amount <= 0:
                        continue
                    
                    # Identifica tipo de transação
                    line_upper = line.upper()
                    if 'RENDIMENTO' in line_upper:
                        transaction_type = 'RENDIMENTO'
                    elif 'PIX' in line_upper and 'RECEBID' in line_upper:
                        transaction_type = 'PIX RECEBIDO'
                    elif 'TRANSFER' in line_upper and 'RECEBID' in line_upper:
                        transaction_type = 'TRANSFERÊNCIA'
                    else:
                        transaction_type = 'CRÉDITO'
                    
                    # Monta descrição
                    description = line
                    # Remove valor e data da descrição
                    description = self.AMOUNT_PATTERN.sub('', description)
                    description = self.DATE_PATTERN.sub('', description)
                    description = re.sub(r'\d{10,}', '', description)  # Remove IDs longos
                    description = re.sub(r'\s+', ' ', description).strip()
                    
                    credits.append(MercadoPagoTransaction(
                        date=date,
                        description=description or transaction_type,
                        amount=amount,
                        transaction_type=transaction_type,
                        raw_line=line,
                        page=page_num
                    ))
        
        return credits


def main():
    parser = argparse.ArgumentParser(description='Extrai créditos de extrato do Mercado Pago')
    parser.add_argument('pdf', help='Caminho para o arquivo PDF')
    parser.add_argument('--out', '-o', help='Arquivo de saída (csv ou json)')
    parser.add_argument('--format', '-f', choices=['csv', 'json'], default='csv')
    args = parser.parse_args()
    
    extractor = MercadoPagoExtractor()
    try:
        credits = extractor.extract_credits(args.pdf)
    except Exception as e:
        print(f'Erro: {e}')
        return
    
    if not credits:
        print('Nenhum crédito encontrado.')
        return
    
    print(f'Encontrados {len(credits)} créditos')
    total = sum(c.amount for c in credits)
    print(f'Total: R$ {total:,.2f}'.replace(',', '@').replace('.', ',').replace('@', '.'))
    
    if args.out:
        if args.format == 'json' or args.out.endswith('.json'):
            with open(args.out, 'w', encoding='utf-8') as f:
                json.dump([asdict(c) for c in credits], f, ensure_ascii=False, indent=2, default=str)
        else:
            with open(args.out, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Data', 'Descrição', 'Valor', 'Tipo', 'Página'])
                for c in credits:
                    writer.writerow([c.date, c.description, str(c.amount), c.transaction_type, c.page])
        print(f'Salvo em {args.out}')
    else:
        for c in credits:
            print(f"{c.date} | R$ {c.amount:,.2f} | {c.description}")


if __name__ == '__main__':
    main()
