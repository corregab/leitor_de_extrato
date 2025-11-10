# 📊 Leitor de Extrato - Apuração Automática de Créditos

Sistema web para análise automática de extratos bancários, extraindo e consolidando informações de créditos de forma rápida e segura.

## 🚀 Funcionalidades

### Bancos Suportados
- ✅ **Itaú** - Extração completa de créditos
- ✅ **Santander** - Análise de receitas com OCR opcional
- ✅ **Nubank** - Processamento de transações
- ✅ **PicPay** - Extração de movimentações
- ✅ **Mercado Pago** - Análise de transações

### Recursos
- 📄 Upload de múltiplos PDFs (até 10 arquivos, 16 MB cada)
- 🔍 Busca em tempo real nos resultados
- 🚫 Filtro por nome para excluir transações específicas
- 📋 Cópia rápida de valores para a área de transferência
- 🖨️ Impressão otimizada de relatórios
- 📱 Interface responsiva para mobile
- 🔒 Segurança com validação robusta de arquivos

## 🎯 Acesso Rápido

- **Web App**: [https://leitor-extrato.onrender.com](https://leitor-extrato.onrender.com)
- **Documentação WEBAPP**: [WEBAPP/README.md](WEBAPP/README.md)
- **Guia de Deploy**: [QUICKSTART.md](QUICKSTART.md)

## 📦 Estrutura do Projeto

```
leitor_de_extrato/
├── WEBAPP/              # Aplicação web Flask
│   ├── app.py          # Aplicação principal
│   ├── templates/      # Templates HTML
│   ├── static/         # CSS, JS, imagens
│   └── requirements.txt
├── ITAU/               # Extrator Itaú
├── SANTANDER/          # Extrator Santander
├── NUBANK/             # Extrator Nubank
├── PICPAY/             # Extrator PicPay
├── MERCADOPAGO/        # Extrator Mercado Pago
└── docs/               # Documentação
```

## 🛠️ Instalação e Uso Local

### Pré-requisitos
- Python 3.12+
- pip

### Instalação

```bash
# Clone o repositório
git clone https://github.com/corregab/leitor_de_extrato.git
cd leitor_de_extrato

# Crie e ative o ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Instale as dependências
pip install -r WEBAPP/requirements.txt
```

### Execução

```bash
# Desenvolvimento
python WEBAPP/app.py

# Produção
cd WEBAPP
gunicorn -c gunicorn_config.py app:app
```

Acesse: http://localhost:5000

## 🌐 Deploy em Produção

### Opção 1: Render (Recomendado - Grátis)

1. Faça fork deste repositório
2. Acesse [Render.com](https://render.com) e conecte seu GitHub
3. Crie um novo Web Service apontando para o repositório
4. O `render.yaml` já está configurado!
5. Deploy automático em cada push

Veja o guia completo: [QUICKSTART.md](QUICKSTART.md)

### Opção 2: PythonAnywhere (Grátis)

Guia completo: [PYTHONANYWHERE_DEPLOY.md](PYTHONANYWHERE_DEPLOY.md)

## 🔒 Segurança

O sistema implementa várias camadas de segurança:

- ✅ Cabeçalhos HTTP de segurança (HSTS, X-Frame-Options, etc.)
- ✅ Validação robusta de arquivos (anti path-traversal)
- ✅ Limite de tamanho e quantidade de arquivos
- ✅ Limpeza automática de arquivos temporários
- ✅ Tratamento seguro de erros
- ✅ Logs detalhados para auditoria

## 📊 API Endpoints

- `GET /` - Página inicial
- `POST /process` - Processar extratos
- `GET /health` - Health check
- `GET /robots.txt` - SEO robots

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Faça fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto é mantido pela **Flexcredit**.

## 🆘 Suporte

- 📧 Issues: [GitHub Issues](https://github.com/corregab/leitor_de_extrato/issues)
- 📖 Wiki: [GitHub Wiki](https://github.com/corregab/leitor_de_extrato/wiki)

## 🎨 Screenshots

### Página Inicial
![Homepage](docs/screenshots/homepage.png)

### Resultados
![Results](docs/screenshots/results.png)

### Página de Erro
![Error Page](docs/screenshots/error.png)

---

**Desenvolvido com ❤️ por Flexcredit**
