# 🎯 PASSO FINAL - Conectar ao GitHub e Deploy

## 📋 Você já tem tudo pronto!

✅ Código preparado para deploy  
✅ Git inicializado  
✅ Arquivos commitados  
✅ Configurações do Render prontas  

---

## 🔗 PRÓXIMOS PASSOS:

### 1️⃣ Criar Repositório no GitHub

1. Acesse: https://github.com/new
2. **Repository name**: `leitor_de_extrato`
3. **Description**: `Sistema web para extração de créditos de extratos bancários (Itaú, Santander, Nubank)`
4. **Private** ✅ (recomendado - contém lógica de negócio)
5. **NÃO** marque "Initialize with README" (já temos)
6. Clique **"Create repository"**

### 2️⃣ Conectar e Enviar (no PowerShell)

Copie e cole os comandos que o GitHub mostrar, ou use estes:

```powershell
cd "c:\Users\gabri\OneDrive\Documentos\documentos Gabriel\Extratos"

# Adicionar remote (substitua SEU_USUARIO pelo seu username do GitHub)
git remote add origin https://github.com/corregab/leitor_de_extrato.git

# Renomear branch para main (se necessário)
git branch -M main

# Enviar para o GitHub
git push -u origin main
```

**Se pedir autenticação:**
- Use seu Personal Access Token (não senha!)
- Ou configure SSH keys

### 3️⃣ Deploy no Render

Agora que está no GitHub:

1. Acesse: https://dashboard.render.com
2. Clique **"New +"** → **"Web Service"**
3. Conecte GitHub e selecione `leitor_de_extrato`
4. O Render detectará `render.yaml` automaticamente
5. Adicione variável de ambiente:
   ```
   FLASK_SECRET_KEY = <gere com: python -c "import secrets; print(secrets.token_hex(32))">
   ```
6. Clique **"Create Web Service"**

### 4️⃣ Aguarde o Deploy 🚀

- Build: ~2-3 minutos
- Primeira vez pode demorar mais
- Quando mostrar **"Live"**, está no ar!

Seu site estará em:
```
https://leitor-extrato.onrender.com
```

---

## 🔄 Fazer Updates Depois

Sempre que modificar o código:

```powershell
# Usar o script de deploy
.\deploy.ps1 "descrição da mudança"
```

**OU manualmente:**
```powershell
git add .
git commit -m "descrição da mudança"
git push origin main
```

O Render automaticamente detecta e faz novo deploy!

---

## 🆘 Problemas Comuns

### Erro ao fazer push?
```powershell
# Se der erro de autenticação, use Personal Access Token:
# Settings → Developer settings → Personal access tokens → Generate new token
# Use o token como senha
```

### Render não encontra o repo?
- Certifique-se que conectou a conta GitHub certa
- Verifique se o repo é privado e você deu permissão ao Render

### Build falha no Render?
- Verifique os logs no dashboard
- Certifique-se que `render.yaml` está no root
- Verifique se `WEBAPP/requirements.txt` está correto

---

## 📊 Status Atual

```
✅ Git inicializado
✅ Código commitado
✅ Arquivos de deploy criados
⏳ Aguardando: Criar repo no GitHub
⏳ Aguardando: Push para GitHub  
⏳ Aguardando: Deploy no Render
```

---

## 💡 Dicas

1. **Mantenha o repo privado** - Contém lógica de negócio
2. **Use .gitignore** - Nunca commite PDFs de clientes
3. **Monitore os logs** - Dashboard do Render mostra tudo
4. **Teste localmente** - Sempre teste antes de fazer push

---

## 🎉 Pronto para Começar!

Execute os comandos acima e em **10 minutos** seu site estará público! 🚀

Qualquer dúvida, me chame! 🤖
