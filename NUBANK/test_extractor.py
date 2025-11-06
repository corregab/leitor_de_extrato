"""
Script de teste para o extrator Nubank.
Teste rápido sem PDF real.
"""

from nubank_extractor import NubankExtractor
from decimal import Decimal


def test_parse():
    """Testa o parsing de texto simulado."""
    extractor = NubankExtractor()
    
    # Simula texto de extrato Nubank
    sample_text = """
    Extrato Nubank
    
    15 JAN    Transferência recebida - João Silva    R$ 1.234,56
    20 JAN    PIX recebido                           R$ 500,00
    22 FEV    Pagamento efetuado                     R$ -150,00
    25 FEV    Cashback Nubank                        R$ 25,50
    01 MAR    Rendimento da conta                    R$ 12,34
    """
    
    extractor._parse_page_text(sample_text)
    
    print(f"\n{'='*70}")
    print("TESTE DO EXTRATOR NUBANK")
    print(f"{'='*70}\n")
    
    if extractor.transactions:
        print(f"✅ Encontradas {len(extractor.transactions)} transações de crédito:\n")
        
        total = Decimal('0')
        for t in extractor.transactions:
            print(f"  {t.date:10} | {t.description:35} | R$ {str(t.amount).replace('.', ','):>10}")
            total += t.amount
        
        print(f"\n{'-'*70}")
        print(f"  {'TOTAL':47} | R$ {str(total).replace('.', ','):>10}")
        print(f"{'='*70}\n")
    else:
        print("⚠️  Nenhuma transação encontrada no texto de teste.")
        print("    Isso pode ser normal dependendo do formato do seu extrato.\n")


if __name__ == '__main__':
    test_parse()
    print("💡 Para testar com um PDF real, use:")
    print("   python nubank_extractor.py caminho/do/extrato.pdf\n")
