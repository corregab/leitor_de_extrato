# 🚀 Guia de Deploy - Render.com

## Passo a Passo para Publicar o Site

### 1️⃣ Preparar o Repositório GitHub

1. Certifique-se de que todos os arquivos estão commitados:
```bash
git add .
git commit -m "Preparar para deploy no Render"
git push origin main
```

### 2️⃣ Criar Conta no Render

1. Acesse: https://render.com
2. Clique em **"Get Started"**
3. Crie uma conta (pode usar GitHub para login)

### 3️⃣ Conectar o Repositório

1. No dashboard do Render, clique em **"New +"**
2. Selecione **"Web Service"**
3. Conecte sua conta do GitHub
4. Selecione o repositório **"leitor_de_extrato"**
5. Clique em **"Connect"**

### 4️⃣ Configurar o Serviço

O Render detectará automaticamente o arquivo `render.yaml`, mas verifique:

**Configurações básicas:**
- **Name**: `leitor-extrato` (ou o nome que preferir)
- **Region**: `Oregon (US West)` (mais próximo)
- **Branch**: `main`
- **Runtime**: `Python 3`

**Comandos:**
- **Build Command**: `pip install -r WEBAPP/requirements.txt`
- **Start Command**: `cd WEBAPP && gunicorn -c gunicorn_config.py app:app`

### 5️⃣ Configurar Variáveis de Ambiente

No Render, vá em **"Environment"** e adicione:

| Key | Value |
|-----|-------|
| `FLASK_SECRET_KEY` | `sua-chave-secreta-aqui-gere-uma-aleatoria` |
| `FLASK_ENV` | `production` |
| `PYTHON_VERSION` | `3.12.0` |

**Para gerar uma chave secreta segura:**
```python
import secrets
print(secrets.token_hex(32))
```

### 6️⃣ Deploy!

1. Clique em **"Create Web Service"**
2. O Render começará a fazer o build
3. Aguarde 3-5 minutos
4. Quando aparecer **"Live"**, seu site está no ar! 🎉

### 7️⃣ Acessar o Site

Seu site estará disponível em:
```
https://leitor-extrato.onrender.com
```
(ou o nome que você escolheu)

---

## 🔧 Troubleshooting

### Build Falhou?
- Verifique os logs no Render
- Certifique-se que o `requirements.txt` está correto
- Verifique se os caminhos no `render.yaml` estão corretos

### Site não carrega?
- Verifique se a porta está configurada corretamente (`PORT` env var)
- Veja os logs de runtime no dashboard do Render

### Erro ao fazer upload?
- Verifique se o limite de 16MB é suficiente
- O Render tem um limite de disco - arquivos temporários podem acumular

---

## 📊 Plano Gratuito - Limitações

O plano gratuito do Render tem:
- ✅ 750 horas/mês (suficiente para uso pessoal)
- ⚠️ O serviço "dorme" após 15min de inatividade (leva ~30s para acordar)
- ✅ 512MB de RAM
- ✅ HTTPS automático
- ✅ Deploy automático via GitHub

---

## 🔄 Atualizações Automáticas

Sempre que você fizer push para o GitHub:
```bash
git add .
git commit -m "Nova funcionalidade"
git push origin main
```

O Render automaticamente:
1. Detecta a mudança
2. Faz novo build
3. Deploy da nova versão
4. Sem downtime! 🚀

---

## 💡 Dicas

1. **Monitore os logs** - Sempre verifique os logs no Render após deploy
2. **Use variáveis de ambiente** - Nunca commite chaves secretas no código
3. **Teste localmente primeiro** - Use `gunicorn -c gunicorn_config.py app:app` antes de fazer push
4. **Limpe uploads** - Considere adicionar um cron job para limpar PDFs antigos

---

## 🆘 Suporte

- Documentação Render: https://render.com/docs
- Community Forum: https://community.render.com

Qualquer problema, me chame! 🤖
