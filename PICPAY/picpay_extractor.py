#!/usr/bin/env python3
"""Extrator de créditos de extratos do PicPay."""
from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass, asdict
from typing import List
from decimal import Decimal, InvalidOperation

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

try:
    from PyPDF2 import PdfReader
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False


@dataclass
class PicPayTransaction:
    """Representa uma transação de crédito no extrato do PicPay."""
    date: str
    description: str
    amount: Decimal
    transaction_type: str
    raw_line: str
    page: int


class PicPayExtractor:
    """Extrator especializado para extratos do PicPay."""
    
    # Padrões de regex
    DATE_PATTERN = re.compile(r'(\d{2}/\d{2}/\d{4})')
    # Captura valores SEM sinal de menos no início
    AMOUNT_PATTERN = re.compile(r'(?<![-\−])\s*R\$\s*(\d{1,3}(?:\.\d{3})*,\d{2})')
    
    @staticmethod
    def parse_amount(amount_str: str) -> Decimal:
        """Converte string de valor para Decimal."""
        clean = amount_str.replace('.', '').replace(',', '.')
        return Decimal(clean)

    def extract_credits(self, pdf_path: str) -> List[PicPayTransaction]:
        """Extrai todas as entradas de crédito do PDF."""
        credits = []
        
        # Tenta PyPDF2 primeiro (mais robusto para PDFs problemáticos)
        if HAS_PYPDF2:
            try:
                reader = PdfReader(pdf_path)
                for page_num, page in enumerate(reader.pages, 1):
                    try:
                        text = page.extract_text()
                        if text:
                            credits.extend(self._process_text(text, page_num))
                    except Exception:
                        continue
                if credits:
                    return credits
            except Exception:
                pass
        
        # Fallback para pdfplumber
        if HAS_PDFPLUMBER:
            try:
                with pdfplumber.open(pdf_path) as pdf:
                    for page_num, page in enumerate(pdf.pages, 1):
                        try:
                            text = page.extract_text(x_tolerance=3, y_tolerance=3)
                            if text:
                                credits.extend(self._process_text(text, page_num))
                        except Exception:
                            continue
            except Exception:
                pass
        
        return credits
    
    def _process_text(self, text: str, page_num: int) -> List[PicPayTransaction]:
        """Processa texto extraído e retorna transações de crédito."""
        credits = []
        lines = text.splitlines()
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            line_upper = line.upper()
            
            # IMPORTANTE: Só pega linhas com "Pix Recebido" (não "Enviado")
            if 'PIX RECEBIDO' not in line_upper:
                continue
            
            # Se tiver "Enviado" na linha, ignora
            if 'ENVIADO' in line_upper:
                continue
            
            # Verifica se tem sinal de menos ANTES do R$ (débito)
            if re.search(r'[-\−]\s*R\$', line):
                continue
            
            # Extrai data
            date_match = self.DATE_PATTERN.search(line)
            date = date_match.group(1) if date_match else '-'
            
            # Extrai valor (sem sinal de menos)
            amount_match = self.AMOUNT_PATTERN.search(line)
            if not amount_match:
                continue
            
            try:
                amount = self.parse_amount(amount_match.group(1))
            except (ValueError, InvalidOperation):
                continue
            
            if amount <= 0:
                continue
            
            # Descrição simples
            description = 'Pix Recebido'
            
            credits.append(PicPayTransaction(
                date=date,
                description=description,
                amount=amount,
                transaction_type='PIX',
                raw_line=line,
                page=page_num
            ))
        
        return credits


def main():
    parser = argparse.ArgumentParser(description='Extrai créditos de extrato do PicPay')
    parser.add_argument('pdf', help='Caminho para o arquivo PDF')
    parser.add_argument('--out', '-o', help='Arquivo de saída (csv ou json)')
    parser.add_argument('--format', '-f', choices=['csv', 'json'], default='csv')
    args = parser.parse_args()
    
    extractor = PicPayExtractor()
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
