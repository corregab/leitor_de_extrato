# Extrator de Créditos - Itaú

Este é um script Python especializado em extrair informações de créditos (valores positivos/verdes) de extratos bancários do Itaú em PDF.

## Características

- Extração específica de créditos (valores positivos) do extrato
- Identificação automática de tipos de transação (PIX, TED, etc.)
- Suporte a exportação em CSV e JSON
- Opção para extrair apenas os valores para Excel
- Formatação adequada para números decimais (BR/US)
- Processamento limpo de descrições e dados

## Requisitos

- Python 3.7+
- pdfplumber (para extração de texto do PDF)

## Instalação

1. Instale as dependências Python:
```bash
pip install -r requirements.txt
```

## Uso

### Uso Básico
```bash
python itau_extractor.py extrato.pdf
```

### Salvar em CSV
```bash
python itau_extractor.py extrato.pdf -o creditos.csv
```

### Salvar em JSON
```bash
python itau_extractor.py extrato.pdf -o creditos.json -f json
```

### Extrair Apenas os Valores (para Excel)
```bash
python itau_extractor.py extrato.pdf --amounts-only -o valores.txt
```

### Usar Vírgula como Separador Decimal
```bash
python itau_extractor.py extrato.pdf --amounts-only --decimal-comma -o valores.txt
```

## Parâmetros

- `pdf`: Caminho para o arquivo PDF do extrato
- `--out`, `-o`: Arquivo de saída (csv ou json)
- `--format`, `-f`: Formato de saída (csv ou json)
- `--amounts-only`: Extrai apenas os valores
- `--decimal-comma`, `--br`: Usa vírgula como separador decimal

## Formato de Saída

### CSV
O arquivo CSV contém as seguintes colunas:
- Data
- Descrição
- Valor
- Tipo (PIX, TED, etc.)
- Linha Original
- Página

### JSON
O arquivo JSON contém os mesmos campos do CSV em formato estruturado.

## Exemplos de Saída

### Visualização no Terminal
```
Data         Tipo       Valor Descrição
2025-06-30   PIX     R$ 20,00 PIX QRS ALLAN CLEYT
2025-06-30   TED    R$ 400,00 TED RECEBIDA EMPRESA XYZ
```

### CSV
```csv
Data,Descrição,Valor,Tipo,Linha Original,Página
30/06/2025,PIX QRS ALLAN CLEYT,20.00,PIX,PIX QRS ALLAN CLEYT30/06,1
30/06/2025,TED RECEBIDA EMPRESA XYZ,400.00,TED,TED RECEBIDA EMPRESA XYZ 30/06,1
```