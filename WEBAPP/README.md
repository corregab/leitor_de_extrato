# WEBAPP — Apuração de Extratos (Flask)

App web simples para enviar um PDF de extrato e extrair créditos usando os extratores existentes do repositório.

## 🚀 Funcionalidades

- ✅ Suporte para múltiplos bancos: Itaú, Santander, Nubank, PicPay, Mercado Pago
- 📄 Upload de múltiplos arquivos PDF (até 10 arquivos por vez)
- 🔍 Busca em tempo real nos resultados
- 🚫 Filtro para excluir transações por nome
- 📋 Copiar valores para a área de transferência
- 🖨️ Impressão otimizada dos resultados
- 📱 Design responsivo para mobile
- 🔒 Segurança aprimorada com validação de arquivos

## Requisitos

- Python 3.12+ (virtualenv já configurado em `.venv`)
- Dependências:
  - `WEBAPP/requirements.txt` (Flask, pdfplumber, PyPDF2, gunicorn)
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
  - Nubank (usa `NUBANK/nubank_extractor.py`)
  - PicPay (usa `PICPAY/picpay_extractor.py`)
  - Mercado Pago (usa `MERCADOPAGO/mercadopago_extractor.py`)

2. Envie um ou mais PDFs do extrato (máximo 10 arquivos, 16 MB cada).

3. (Opcional) Digite nomes separados por vírgula para excluir transações.

4. Clique em "Processar Extrato" e aguarde.

5. Veja a tabela de créditos com:
   - 🔍 Busca em tempo real
   - 📋 Botão para copiar valores
   - 🖨️ Botão para imprimir
   - Total de créditos encontrados

## Melhorias Implementadas

### Segurança
- Validação robusta de arquivos (sem path traversal)
- Cabeçalhos de segurança HTTP (X-Frame-Options, CSP, etc.)
- Limite de tamanho de arquivo (16 MB)
- Limite de quantidade de arquivos (10 por vez)
- Tratamento seguro de erros

### UX/UI
- Indicador de carregamento durante processamento
- Contador de arquivos selecionados
- Mensagens de erro amigáveis
- Design responsivo para mobile
- Estilos otimizados para impressão
- Busca instantânea nos resultados

### Performance
- Processamento eficiente de múltiplos arquivos
- Limpeza automática de arquivos temporários
- Logging apropriado para debug

## Observações

- PDFs com texto embutido funcionam direto. Para PDFs escaneados, o Santander tem fallback por OCR se você instalar Tesseract e Poppler no Windows (além das libs Python já presentes no `requirements`).
- Os arquivos enviados ficam em `WEBAPP/uploads/` com nomes aleatórios e são automaticamente deletados após o processamento.
- O app não altera os extratores. Ele apenas importa e usa as APIs existentes.

## Deploy

Para deploy em produção:
- Configure `FLASK_SECRET_KEY` como variável de ambiente
- Use gunicorn: `gunicorn -c gunicorn_config.py app:app`
- Veja `QUICKSTART.md` para instruções de deploy no Render ou PythonAnywhere
