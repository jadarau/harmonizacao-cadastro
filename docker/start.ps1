# Script PowerShell para inicializar o ambiente Docker da aplicacao Harmonizacao

Write-Host "Iniciando ambiente Docker da aplicacao Harmonizacao..." -ForegroundColor Green

# Verifica se o Docker esta rodando
try {
    docker info | Out-Null
} catch {
    Write-Host "Docker nao esta rodando. Por favor, inicie o Docker e tente novamente." -ForegroundColor Red
    exit 1
}

# Verifica se o arquivo .env existe
if (!(Test-Path ".env")) {
    Write-Host "Arquivo .env nao encontrado." -ForegroundColor Yellow
    Write-Host "Copiando .env.example para .env..." -ForegroundColor Cyan
    Copy-Item ".env.example" ".env"
    Write-Host "Por favor, edite o arquivo .env e adicione sua GROQ_API_KEY" -ForegroundColor Yellow
    Write-Host "Arquivo .env criado em: $(Get-Location)\.env" -ForegroundColor Cyan
    
    # Abre o arquivo no editor padrao
    Start-Process ".env"
    
    $groqKey = Read-Host "Digite sua GROQ_API_KEY"
    if ($groqKey) {
        (Get-Content ".env") -replace "sua_api_key_aqui", $groqKey | Set-Content ".env"
        Write-Host "GROQ_API_KEY configurada!" -ForegroundColor Green
    }
}

Write-Host "Construindo e iniciando containers..." -ForegroundColor Cyan

# Para containers existentes
docker-compose down

# Remove volumes orfaos
docker-compose down --volumes --remove-orphans

# Constroi e inicia os servicos
docker-compose up --build -d

Write-Host "Aguardando inicializacao dos servicos..." -ForegroundColor Yellow

# Aguarda o MongoDB estar saudavel
Write-Host "Verificando saude do MongoDB..." -ForegroundColor Cyan
$timeout = 60
while ($timeout -gt 0) {
    try {
        docker-compose exec mongodb mongosh --eval "db.adminCommand('ping')" | Out-Null
        Write-Host "MongoDB esta rodando!" -ForegroundColor Green
        break
    } catch {
        Write-Host "Aguardando MongoDB... ($timeout segundos restantes)" -ForegroundColor Yellow
        Start-Sleep 2
        $timeout -= 2
    }
}

if ($timeout -le 0) {
    Write-Host "Timeout aguardando MongoDB. Verificando logs..." -ForegroundColor Red
    docker-compose logs mongodb
    exit 1
}

# Aguarda a aplicacao estar pronta
Write-Host "Verificando saude da aplicacao..." -ForegroundColor Cyan
$timeout = 30
while ($timeout -gt 0) {
    try {
        Invoke-WebRequest -Uri "http://localhost:8002/v1/healthz" -TimeoutSec 2 | Out-Null
        Write-Host "Aplicacao esta rodando!" -ForegroundColor Green
        break
    } catch {
        Write-Host "Aguardando aplicacao... ($timeout segundos restantes)" -ForegroundColor Yellow
        Start-Sleep 2
        $timeout -= 2
    }
}

Write-Host ""
Write-Host "Ambiente Docker iniciado com sucesso!" -ForegroundColor Green
Write-Host ""
Write-Host "Servicos disponiveis:" -ForegroundColor Cyan
Write-Host "  API: http://localhost:8002" -ForegroundColor White
Write-Host "  Documentacao: http://localhost:8002/docs" -ForegroundColor White
Write-Host "  MongoDB: localhost:27017" -ForegroundColor White
Write-Host ""
Write-Host "Comandos uteis:" -ForegroundColor Cyan
Write-Host "  Ver logs: docker-compose logs -f" -ForegroundColor White
Write-Host "  Parar: docker-compose down" -ForegroundColor White
Write-Host "  Reiniciar: docker-compose restart" -ForegroundColor White
Write-Host ""
Write-Host "Collections criadas:" -ForegroundColor Cyan
Write-Host "  clientes (com indices otimizados)" -ForegroundColor White
Write-Host "Dados salvos em: C:\projects\db\harmonizacao\" -ForegroundColor Cyan
Write-Host ""

# Mostra status dos containers
docker-compose ps