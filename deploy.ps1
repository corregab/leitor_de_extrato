# Script PowerShell para fazer deploy
# Uso: .\deploy.ps1 "mensagem do commit"

param(
    [Parameter(Mandatory=$true)]
    [string]$CommitMessage
)

Write-Host "🚀 Preparando deploy..." -ForegroundColor Cyan

# Verifica se está no repositório git
if (-not (Test-Path .git)) {
    Write-Host "❌ Este não é um repositório git!" -ForegroundColor Red
    exit 1
}

# Adiciona arquivos
Write-Host "📦 Adicionando arquivos..." -ForegroundColor Yellow
git add .

# Commit
Write-Host "💾 Fazendo commit..." -ForegroundColor Yellow
git commit -m $CommitMessage

# Push
Write-Host "📤 Enviando para GitHub..." -ForegroundColor Yellow
git push origin main

Write-Host ""
Write-Host "✅ Deploy iniciado!" -ForegroundColor Green
Write-Host "🔗 Verifique o status em: https://dashboard.render.com" -ForegroundColor Cyan
Write-Host "⏱️  O deploy levará cerca de 3-5 minutos" -ForegroundColor Yellow
