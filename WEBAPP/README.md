# WEBAPP — Apuração de Extratos (Flask)

App web simples para enviar um PDF de extrato e extrair créditos usando os extratores existentes do repositório.

## Requisitos

- Python 3.12 (virtualenv já configurado em `.venv`)
- Dependências:
  - `WEBAPP/requirements.txt` (Flask)
  - `ITAU/requirements.txt` (pdfplumber)
  - `SANTANDER/requirements.txt` (pdfplumber, pandas e OCR opcional)

## Como rodar

No PowerShell, na raiz do repositório:

```powershell
# Ativar o ambiente (se ainda não estiver ativo)
.\.venv\Scripts\Activate.ps1

# Instalar dependências
pip install -r WEBAPP\requirements.txt
pip install -r ITAU\requirements.txt
pip install -r SANTANDER\requirements.txt

# Iniciar o servidor
python WEBAPP\app.py
```

Acesse no navegador: http://127.0.0.1:5000

## Uso

1. Selecione o banco:
  - Itaú (usa `ITAU/itau_extractor.py`)
  - Santander (usa `SANTANDER/income_extractor.py`)
2. Envie o PDF do extrato.
3. (Opcional) Marque “Gerar planilha de valores” e escolha o formato:
  - XLSX: uma planilha com 6 abas (meses em pt-BR) + aba Resumo com soma por mês
  - CSV por mês (ZIP): um arquivo .zip contendo 6 CSVs (um por mês)
4. Veja a tabela de créditos e o total. Se gerou exportação, use o botão para baixar.

## Observações

- PDFs com texto embutido funcionam direto. Para PDFs escaneados, o Santander tem fallback por OCR se você instalar Tesseract e Poppler no Windows (além das libs Python já presentes no `requirements`).
- Os arquivos enviados ficam em `WEBAPP/uploads/` com nomes aleatórios; limpe essa pasta periodicamente se desejar.
- O app não altera os extratores. Ele apenas importa e usa as APIs existentes.
