# Extrator de Créditos - Nubank

Extrai transações de crédito (entradas) de extratos Nubank em PDF.

## Instalação

```bash
pip install -r requirements.txt
```

## Uso via linha de comando

```bash
python nubank_extractor.py caminho/do/extrato.pdf
```

## Uso como módulo

```python
from nubank_extractor import extract_nubank_credits

credits = extract_nubank_credits('extrato.pdf')

for transaction in credits:
    print(f"{transaction.date} - {transaction.description}: R$ {transaction.amount}")
```

## Formato esperado

O extrator procura por linhas no formato:
- `DD MMM    Descrição    R$ valor`
- `DD/MM     Descrição    R$ +valor`

Apenas valores positivos (créditos) são extraídos.

## Integração

Este extrator está integrado ao sistema web em `WEBAPP/app.py`.
