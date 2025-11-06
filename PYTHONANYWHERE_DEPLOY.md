# 🆓 DEPLOY GRATUITO - Guia Completo PythonAnywhere

## ⭐ POR QUE PYTHONANYWHERE?

- ✅ **100% GRATUITO** (sem cartão de crédito!)
- ✅ Feito especificamente para Python
- ✅ Flask já configurado
- ✅ Domínio grátis: `seuusuario.pythonanywhere.com`
- ✅ 512MB de espaço (suficiente para o projeto)
- ✅ Fácil de usar

---

## 📋 PASSO A PASSO COMPLETO

### 1️⃣ Criar Conta (2 minutos)

1. Acesse: https://www.pythonanywhere.com/registration/register/beginner/
2. Preencha:
   - **Username**: escolha bem, será seu domínio (`username.pythonanywhere.com`)
   - **Email**: seu email
   - **Password**: senha segura
3. Clique **"Register"**
4. Confirme o email

### 2️⃣ Primeiro, Enviar Código para GitHub (5 minutos)

No seu PowerShell:

```powershell
cd "c:\Users\gabri\OneDrive\Documentos\documentos Gabriel\Extratos"

# 1. Criar repo no GitHub primeiro!
# Acesse: https://github.com/new
# Nome: leitor_de_extrato
# Privado: ✅
# NÃO marque "Initialize with README"

# 2. Conectar ao GitHub (substitua 'corregab' pelo seu username)
git remote add origin https://github.com/corregab/leitor_de_extrato.git
git branch -M main
git push -u origin main
```

### 3️⃣ Clonar Código no PythonAnywhere (3 minutos)

1. Login no PythonAnywhere
2. Vá em **"Consoles"** → **"Bash"**
3. No console, digite:

```bash
# Clonar seu repositório
git clone https://github.com/corregab/leitor_de_extrato.git

# Entrar na pasta
cd leitor_de_extrato

# Verificar se está tudo lá
ls -la
```

### 4️⃣ Instalar Dependências (2 minutos)

No mesmo console Bash:

```bash
# Entrar na pasta WEBAPP
cd WEBAPP

# Instalar dependências
pip3.10 install --user -r requirements.txt

# Aguarde... pode demorar 1-2 minutos
```

### 5️⃣ Criar Web App (3 minutos)

1. Volte ao Dashboard → Aba **"Web"**
2. Clique **"Add a new web app"**
3. Escolha:
   - Domínio: `seuusuario.pythonanywhere.com` (já preenchido)
   - Framework: **Flask**
   - Python version: **Python 3.10**
4. Na próxima tela:
   - Path to your Flask app: `/home/seuusuario/leitor_de_extrato/WEBAPP/app.py`
   - Clique **"Next"**

### 6️⃣ Configurar WSGI File (2 minutos)

1. Na página do Web App, encontre **"Code"** → **"WSGI configuration file"**
2. Clique no link do arquivo (ex: `/var/www/seuusuario_pythonanywhere_com_wsgi.py`)
3. **DELETE TODO** o conteúdo
4. Substitua por:

```python
import sys
import os

# Adiciona o caminho do seu projeto
path = '/home/seuusuario/leitor_de_extrato'  # MUDE 'seuusuario' para seu username!
if path not in sys.path:
    sys.path.insert(0, path)

# Importa a aplicação Flask
from WEBAPP.app import app as application

# Configura variável de ambiente
os.environ['FLASK_SECRET_KEY'] = 'sua-chave-secreta-aqui-gere-uma-aleatoria'
```

5. **IMPORTANTE**: Substitua `seuusuario` pelo seu username do PythonAnywhere!
6. Clique **"Save"**

### 7️⃣ Ajustar Configurações (1 minuto)

Na página do Web App:

1. Role até **"Virtualenv"** (pode deixar em branco, não vamos usar)
2. Role até **"Static files"** → Adicione:
   - URL: `/static/`
   - Directory: `/home/seuusuario/leitor_de_extrato/WEBAPP/static`

3. Role até **"Working directory"**:
   - `/home/seuusuario/leitor_de_extrato/WEBAPP`

### 8️⃣ Reload e Testar! 🚀

1. No topo da página, clique no botão verde **"Reload seuusuario.pythonanywhere.com"**
2. Aguarde 5 segundos
3. Clique no link do seu site: `https://seuusuario.pythonanywhere.com`

**PRONTO!** Seu site está no ar! 🎉

---

## 🔄 Como Fazer Updates Depois

Quando você mudar algo no código:

```powershell
# No seu computador:
git add .
git commit -m "descrição da mudança"
git push origin main
```

```bash
# No console Bash do PythonAnywhere:
cd ~/leitor_de_extrato
git pull origin main

# Se mudou dependências:
cd WEBAPP
pip3.10 install --user -r requirements.txt

# Depois, volte para Web → Reload
```

---

## 🆘 Problemas Comuns

### Site mostra erro 500?
- Vá em Web → **Error log** para ver o erro
- Verifique se o caminho no WSGI está correto
- Certifique-se que substituiu `seuusuario` pelo seu username

### Imports não funcionam?
- Verifique o `sys.path` no arquivo WSGI
- Certifique-se que as dependências foram instaladas

### Upload de PDF não funciona?
- PythonAnywhere tem limite de tamanho
- Verifique permissões da pasta `uploads/`

### Site lento ou offline?
- Plano grátis tem limite de tráfego diário
- Site pode "dormir" após inatividade (acorde acessando)

---

## 📊 Limitações do Plano Gratuito

- ⚠️ Site expira após 3 meses de inatividade (só fazer login para renovar)
- ⚠️ 100 segundos de CPU/dia (suficiente para uso pessoal)
- ⚠️ 512MB de espaço em disco
- ⚠️ Apenas 1 aplicação web

**Para este projeto, isso é MAIS que suficiente!** ✅

---

## 💡 Dicas

1. **Marque no calendário**: Login a cada 2 meses para renovar conta grátis
2. **Limpe uploads**: Delete PDFs antigos da pasta `uploads/` periodicamente
3. **Monitore logs**: Sempre verifique error.log se algo não funcionar
4. **Compartilhe**: Seu link é `https://seuusuario.pythonanywhere.com`

---

## 🎯 Checklist Final

```
☐ Conta PythonAnywhere criada
☐ Código no GitHub
☐ Clonado no PythonAnywhere
☐ Dependências instaladas
☐ Web App criado
☐ WSGI configurado (com seu username!)
☐ Static files configurado
☐ Reload feito
☐ Site testado e funcionando! 🎉
```

---

**Qualquer problema, me chame!** 🚀
