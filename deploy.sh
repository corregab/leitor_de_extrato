#!/bin/bash

# Script para fazer o deploy manual no Render (opcional)

echo "🚀 Preparando deploy..."

# 1. Verifica se está no git
if [ ! -d .git ]; then
    echo "❌ Este não é um repositório git!"
    exit 1
fi

# 2. Adiciona arquivos
echo "📦 Adicionando arquivos..."
git add .

# 3. Commit
echo "💾 Fazendo commit..."
read -p "Mensagem do commit: " commit_msg
git commit -m "$commit_msg"

# 4. Push
echo "📤 Enviando para GitHub..."
git push origin main

echo "✅ Deploy iniciado! Verifique o Render em https://dashboard.render.com"
echo "⏱️  O deploy levará cerca de 3-5 minutos"
