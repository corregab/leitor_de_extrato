"""
Extrator de créditos do extrato Nubank em PDF.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal, ROUND_DOWN
from typing import List

import pdfplumber


@dataclass
class NubankTransaction:
    """Representa uma transação de crédito do Nubank."""
    date: str
    description: str
    amount: Decimal
    transaction_type: str = "CRÉDITO"


class NubankExtractor:
    """Extrai transações de crédito de extratos Nubank em PDF."""

    def __init__(self):
        self.transactions: List[NubankTransaction] = []

    def extract_credits(self, pdf_path: str) -> List[NubankTransaction]:
        """
        Extrai todas as transações de crédito do PDF do Nubank.
        
        Args:
            pdf_path: Caminho para o arquivo PDF do extrato.
            
        Returns:
            Lista de NubankTransaction com os créditos encontrados.
        """
        self.transactions = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    self._parse_page_text(text)
        
        return self.transactions

    def _parse_page_text(self, text: str) -> None:
        """
        Processa o texto de uma página buscando transações de crédito.
        
        O formato do Nubank:
        1. Procura por linhas com data (DD MMM YYYY) + "Total de entradas"
        2. As transações de crédito aparecem APÓS essa linha
        3. Cada transação tem descrição e valor no final (formato: 1.234,56)
        4. Algumas transações ocupam múltiplas linhas
        5. Termina quando encontra "Total de saídas"
        
        Args:
            text: Texto extraído da página.
        """
        lines = text.split('\n')
        in_credits_section = False
        current_date = None
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Detecta início da seção de créditos
            # Formato: "DD MMM YYYY Total de entradas + valor"
            if 'Total de entradas' in line:
                in_credits_section = True
                # Extrai a data da mesma linha
                date_match = re.match(r'^(\d{1,2}\s+(?:JAN|FEV|MAR|ABR|MAI|JUN|JUL|AGO|SET|OUT|NOV|DEZ)\s+\d{4})', line, re.IGNORECASE)
                if date_match:
                    current_date = date_match.group(1).strip()
                continue
            
            # Detecta fim da seção de créditos
            if 'Total de sa' in line or 'Total de débitos' in line:
                in_credits_section = False
                current_date = None
                continue
            
            # Se estamos na seção de créditos, processa as transações
            if in_credits_section and current_date:
                # Busca por valores no final da linha (formato: 1.234,56 ou 123,45)
                value_pattern = r'\s+([\d.]+,\d{2})\s*$'
                value_match = re.search(value_pattern, line)
                
                if value_match:
                    value_str = value_match.group(1)
                    
                    # Extrai a descrição (tudo antes do valor)
                    description = line[:value_match.start()].strip()
                    
                    # Ignora linhas que não são transações válidas
                    if not description:
                        continue
                    
                    # Ignora linhas que são apenas informações bancárias
                    # (geralmente começam com parênteses ou são números de conta)
                    if description.startswith('(') or description.startswith('Ag'):
                        continue
                    
                    # Ignora linhas muito curtas (números de conta, códigos, etc)
                    if len(description) < 5:
                        continue
                    
                    # Ignora Resgates RDB (não devem ser contabilizados)
                    if 'Resgate RDB' in description or 'resgate rdb' in description.lower():
                        continue
                    
                    try:
                        # Converte o valor
                        value_str = value_str.replace('.', '').replace(',', '.')
                        amount = Decimal(value_str)
                        
                        if amount > 0:
                            transaction = NubankTransaction(
                                date=current_date,
                                description=description,
                                amount=amount.quantize(Decimal('.01'), rounding=ROUND_DOWN)
                            )
                            self.transactions.append(transaction)
                    
                    except (ValueError, ArithmeticError):
                        # Valor inválido, ignora
                        continue


def extract_nubank_credits(pdf_path: str) -> List[NubankTransaction]:
    """
    Função auxiliar para extrair créditos do Nubank.
    
    Args:
        pdf_path: Caminho para o arquivo PDF do extrato.
        
    Returns:
        Lista de NubankTransaction com os créditos.
    """
    extractor = NubankExtractor()
    return extractor.extract_credits(pdf_path)


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python nubank_extractor.py <caminho_do_pdf>")
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    credits = extract_nubank_credits(pdf_file)
    
    print(f"\n{'='*80}")
    print(f"EXTRATO NUBANK - CRÉDITOS")
    print(f"{'='*80}\n")
    
    if not credits:
        print("Nenhum crédito encontrado.")
    else:
        total = Decimal('0')
        for t in credits:
            print(f"{t.date:12} | {t.description:40} | R$ {str(t.amount).replace('.', ','):>12}")
            total += t.amount
        
        print(f"\n{'-'*80}")
        print(f"{'TOTAL':54} | R$ {str(total.quantize(Decimal('.01'))).replace('.', ','):>12}")
        print(f"{'='*80}\n")
