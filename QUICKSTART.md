# 🚀 QUICK START - Deploy em 5 Minutos

## ✅ Checklist Rápida

### 1. Commit e Push
```powershell
git add .
git commit -m "Preparar para deploy no Render"
git push origin main
```

**OU use o script:**
```powershell
.\deploy.ps1 "Preparar para deploy no Render"
```

### 2. Criar Conta no Render
- Acesse: https://render.com
- Clique em "Get Started"
- Login com GitHub

### 3. Novo Web Service
1. Dashboard → **"New +"** → **"Web Service"**
2. Conecte o GitHub
3. Selecione repositório **"leitor_de_extrato"**
4. Clique **"Connect"**

### 4. Configurações Automáticas
O `render.yaml` já está configurado! Apenas verifique:

✅ **Name**: leitor-extrato  
✅ **Region**: Oregon  
✅ **Branch**: main  
✅ **Runtime**: Python 3  

### 5. Variável de Ambiente (IMPORTANTE!)
Adicione em "Environment":

```
FLASK_SECRET_KEY = cole-uma-chave-secreta-aqui
```

**Gerar chave secreta:**
```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

### 6. Deploy! 🎉
Clique em **"Create Web Service"**

Aguarde 3-5 minutos e seu site estará em:
```
https://leitor-extrato.onrender.com
```

---

## 🔄 Fazer Updates Depois

Sempre que mudar algo:
```powershell
.\deploy.ps1 "descrição da mudança"
```

O Render detecta automaticamente e atualiza o site!

---

## 📞 Problemas?

Leia o arquivo `DEPLOYMENT.md` para troubleshooting completo.
