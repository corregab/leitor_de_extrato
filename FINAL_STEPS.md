# 🎯 DEPLOY GRATUITO - PythonAnywhere

## 📋 Você já tem tudo pronto!

✅ Código preparado para deploy  
✅ Git inicializado  
✅ Arquivos commitados  

---

## 🆓 OPÇÃO 1: PythonAnywhere (100% GRÁTIS - RECOMENDADO)

### Vantagens:
- ✅ Totalmente GRATUITO (para sempre!)
- ✅ Especializado em Python/Flask
- ✅ Fácil de configurar
- ✅ 512MB de espaço
- ✅ Domínio: `seuusuario.pythonanywhere.com`

### Passo a Passo:

1. **Criar conta**: https://www.pythonanywhere.com/registration/register/beginner/
   - Use um email válido
   - Escolha um username (será seu domínio)

2. **Fazer upload do código:**
   - Dashboard → **Files**
   - Upload dos arquivos ou use **Git**:
   ```bash
   # No console Bash do PythonAnywhere:
   git clone https://github.com/corregab/leitor_de_extrato.git
   cd leitor_de_extrato
   ```

3. **Instalar dependências:**
   ```bash
   cd ~/leitor_de_extrato/WEBAPP
   pip3.10 install --user -r requirements.txt
   ```

4. **Configurar Web App:**
   - Dashboard → **Web** → **Add a new web app**
   - Framework: **Flask**
   - Python version: **3.10**
   - Path: `/home/seuusuario/leitor_de_extrato/WEBAPP/app.py`

5. **Configurar WSGI:**
   - Edite o arquivo WSGI que foi criado
   - Substitua o conteúdo por:
   ```python
   import sys
   path = '/home/seuusuario/leitor_de_extrato'
   if path not in sys.path:
       sys.path.insert(0, path)
   
   from WEBAPP.app import app as application
   ```

6. **Reload** e pronto! 🎉
   - Seu site: `https://seuusuario.pythonanywhere.com`

---

## 🆓 OPÇÃO 2: Railway.app ($5 GRÁTIS/MÊS)

### Vantagens:
- ✅ $5 de crédito mensal (suficiente para site pequeno)
- ✅ Deploy super fácil
- ✅ Domínio personalizado grátis

### Passo a Passo:

1. **Criar conta**: https://railway.app
   - Login com GitHub

2. **Novo projeto:**
   - New Project → Deploy from GitHub repo
   - Selecione `leitor_de_extrato`

3. **Configurações automáticas:**
   Railway detecta Python e Flask automaticamente!

4. **Variáveis de ambiente:**
   - Adicione: `PORT=8080`
   - Adicione: `FLASK_SECRET_KEY=<chave-secreta>`

5. **Deploy automático!** ✅

---

## 🆓 OPÇÃO 3: Vercel (GRÁTIS)

**⚠️ Limitação:** Vercel é para sites serverless, então precisa adaptar um pouco.

---

## 🎯 RECOMENDAÇÃO:

**Use PythonAnywhere!** É:
- ✅ 100% gratuito
- ✅ Feito para Python
- ✅ Mais fácil de configurar
- ✅ Sem surpresas de cobrança

---

## 📋 Checklist PythonAnywhere:

```
1. ☐ Criar conta no PythonAnywhere
2. ☐ Fazer push do código para GitHub
3. ☐ Clonar repo no PythonAnywhere via console Bash
4. ☐ Instalar dependências com pip
5. ☐ Criar Web App (Flask, Python 3.10)
6. ☐ Configurar WSGI file
7. ☐ Reload e testar!
```

---

## 🆘 Dúvidas?

Me chame que eu te ajudo com qualquer uma das opções! 🤖
