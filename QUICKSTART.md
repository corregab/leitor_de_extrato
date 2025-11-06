# 🚀 QUICK START - Deploy GRATUITO em 15 Minutos# 🚀 QUICK START - Deploy em 5 Minutos



## ✅ Opção GRÁTIS: PythonAnywhere## ✅ Checklist Rápida



**100% gratuito, sem cartão de crédito!**### 1. Commit e Push

```powershell

### 1. Criar Contagit add .

- Acesse: https://www.pythonanywhere.com/registration/register/beginner/git commit -m "Preparar para deploy no Render"

- Escolha um username (será seu domínio)git push origin main

```

### 2. Enviar Código para GitHub

```powershell**OU use o script:**

cd "c:\Users\gabri\OneDrive\Documentos\documentos Gabriel\Extratos"```powershell

.\deploy.ps1 "Preparar para deploy no Render"

# Primeiro: Criar repo em https://github.com/new```

# Nome: leitor_de_extrato | Privado: ✅

### 2. Criar Conta no Render

git remote add origin https://github.com/SEU_USUARIO/leitor_de_extrato.git- Acesse: https://render.com

git branch -M main- Clique em "Get Started"

git push -u origin main- Login com GitHub

```

### 3. Novo Web Service

### 3. Clonar no PythonAnywhere1. Dashboard → **"New +"** → **"Web Service"**

No console Bash do PythonAnywhere:2. Conecte o GitHub

```bash3. Selecione repositório **"leitor_de_extrato"**

git clone https://github.com/SEU_USUARIO/leitor_de_extrato.git4. Clique **"Connect"**

cd leitor_de_extrato/WEBAPP

pip3.10 install --user -r requirements.txt### 4. Configurações Automáticas

```O `render.yaml` já está configurado! Apenas verifique:



### 4. Criar Web App✅ **Name**: leitor-extrato  

- Dashboard → Web → Add a new web app✅ **Region**: Oregon  

- Flask | Python 3.10✅ **Branch**: main  

- Path: `/home/seuusuario/leitor_de_extrato/WEBAPP/app.py`✅ **Runtime**: Python 3  



### 5. Configurar WSGI### 5. Variável de Ambiente (IMPORTANTE!)

Edite o arquivo WSGI com:Adicione em "Environment":

```python

import sys```

path = '/home/seuusuario/leitor_de_extrato'  # MUDE 'seuusuario'!FLASK_SECRET_KEY = cole-uma-chave-secreta-aqui

if path not in sys.path:```

    sys.path.insert(0, path)

**Gerar chave secreta:**

from WEBAPP.app import app as application```powershell

```python -c "import secrets; print(secrets.token_hex(32))"

```

### 6. Reload! 🎉

Seu site: `https://seuusuario.pythonanywhere.com`### 6. Deploy! 🎉

Clique em **"Create Web Service"**

---

Aguarde 3-5 minutos e seu site estará em:

## 📖 Guia Detalhado```

https://leitor-extrato.onrender.com

Veja `PYTHONANYWHERE_DEPLOY.md` para o passo a passo completo!```



------



## 💡 Recomendação## 🔄 Fazer Updates Depois



**Use PythonAnywhere!** É a melhor opção gratuita para Flask.Sempre que mudar algo:

```powershell

Me chame se precisar de ajuda! 🤖.\deploy.ps1 "descrição da mudança"

```

O Render detecta automaticamente e atualiza o site!

---

## 📞 Problemas?

Leia o arquivo `DEPLOYMENT.md` para troubleshooting completo.
