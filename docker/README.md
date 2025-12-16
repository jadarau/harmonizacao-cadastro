# 🐳 Docker Setup - Harmonização

Este diretório contém a configuração Docker completa para a aplicação Harmonização com MongoDB.

## 🚀 Início Rápido

### ⚡ Comandos Essenciais

#### **Subir Todos os Serviços**
```powershell
# Windows (Automático - Recomendado)
cd docker
.\start.ps1

# Linux/Mac (Automático)
cd docker
chmod +x start.sh
./start.sh

# Manual (Qualquer OS)
cd docker
cp .env.example .env
# Edite .env com sua GROQ_API_KEY
docker-compose up --build -d
```

#### **Subir Apenas MongoDB**
```powershell
cd docker
docker-compose up -d mongodb
```

#### **Subir Apenas a API**
```powershell
cd docker
docker-compose up -d harmonizacao_app
```

#### **Subir Apenas o Kafka (Redpanda)**
```powershell
cd docker
docker-compose up -d kafka
```

#### **Parar Todos os Serviços**
```powershell
cd docker
docker-compose down
```

#### **Ver Status**
```powershell
cd docker
docker-compose ps
```

#### **Ver Logs**
```powershell
cd docker
# Todos os logs
docker-compose logs -f

# Apenas MongoDB
docker-compose logs -f mongodb

# Apenas API
docker-compose logs -f harmonizacao_app

# Apenas Kafka
docker-compose logs -f kafka
```

### Scripts Automatizados

### Windows (PowerShell)
```powershell
cd docker
.\start.ps1
```

### Linux/Mac (Bash)
```bash
cd docker
chmod +x start.sh
./start.sh
```

### Manual
```bash
cd docker
cp .env.example .env
# Edite o arquivo .env com sua GROQ_API_KEY
docker-compose up --build -d
```

## 📋 Pré-requisitos

- Docker Desktop instalado e rodando
- GROQ_API_KEY válida
- (Opcional) Kafka habilitado (já incluso via Redpanda no docker-compose)

## 🏗️ Arquitetura

```
┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │
│  FastAPI App    │────▶│    MongoDB      │
│  (Port 8002)    │     │  (Port 27017)   │
│                 │     │                 │
└─────────────────┘     └─────────────────┘
```

## 🗄️ MongoDB

### Configuração Automática
- ✅ **Database**: `harmonizacao`
- ✅ **Collection**: `clientes` (criada automaticamente)
- ✅ **Índices**: email, telefone, nome, created_at
- ✅ **Validação**: Schema JSON para dados consistentes
- ✅ **Exemplo**: Cliente de exemplo inserido

### Credenciais Padrão
- **Usuário**: `admin`
- **Senha**: `admin123`
- **URL**: `mongodb://admin:admin123@localhost:27017/harmonizacao?authSource=admin`

## 🌐 Endpoints Disponíveis

Após inicializar, os seguintes endpoints estarão disponíveis:

- **API**: http://localhost:8002
- **Documentação**: http://localhost:8002/docs
- **Redoc**: http://localhost:8002/redoc

### Principais Rotas
- `POST /v1/cliente/formulario` - Criar cliente
- `GET /v1/cliente/` - Listar clientes
- `GET /v1/cliente/{id}` - Buscar cliente
- `PUT /v1/cliente/{id}` - Atualizar cliente
- `DELETE /v1/cliente/{id}` - Remover cliente

## 🔧 Comandos Úteis

### 📊 Gerenciamento de Serviços
```powershell
# Subir todos os serviços
docker-compose up -d

# Subir com rebuild (primeira vez ou após mudanças)
docker-compose up --build -d

# Subir apenas um serviço específico
docker-compose up -d mongodb
docker-compose up -d harmonizacao_app

# Parar todos os serviços
docker-compose down

# Parar e remover volumes (⚠️ PERDERÁ DADOS)
docker-compose down --volumes

# Reiniciar serviços
docker-compose restart

# Reiniciar serviço específico
docker-compose restart mongodb
docker-compose restart harmonizacao_app

# Forçar recriação de containers
docker-compose up --force-recreate -d
```

### 📋 Monitoramento e Logs
```powershell
# Ver status dos containers
docker-compose ps

# Ver logs em tempo real (todos)
docker-compose logs -f

# Ver logs de serviço específico
docker-compose logs -f mongodb
docker-compose logs -f harmonizacao_app

# Logs do Kafka (Redpanda)
docker-compose logs -f kafka

# Ver logs das últimas N linhas
docker-compose logs --tail=50 mongodb

# Ver logs com timestamp
docker-compose logs -f -t mongodb

# Limpar logs (se necessário)
docker system prune
```

### 🔍 Diagnóstico e Debug
```powershell
# Verificar saúde dos containers
docker-compose ps

# Inspecionar container
docker inspect harmonizacao_mongodb
docker inspect harmonizacao_api

# Entrar no container (bash)
docker-compose exec mongodb bash
docker-compose exec harmonizacao_app bash

# Verificar rede
docker network ls
docker network inspect docker_harmonizacao_network

# Ver uso de recursos
docker stats

# Verificar volumes
docker volume ls
```

### 🗄️ Comandos MongoDB
```powershell
# Acessar MongoDB via shell
docker-compose exec mongodb mongosh -u admin -p admin123 --authenticationDatabase admin harmonizacao

# Verificar conexão
docker-compose exec mongodb mongosh --eval "db.adminCommand('ping')"

# Backup do banco
docker-compose exec mongodb mongodump --uri="mongodb://admin:admin123@localhost:27017/harmonizacao?authSource=admin" --out=/data/backup

# Restore do banco
docker-compose exec mongodb mongorestore --uri="mongodb://admin:admin123@localhost:27017/harmonizacao?authSource=admin" /data/backup/harmonizacao

# Ver collections
docker-compose exec mongodb mongosh -u admin -p admin123 --authenticationDatabase admin harmonizacao --eval "show collections"

# Contar documentos na collection clientes
docker-compose exec mongodb mongosh -u admin -p admin123 --authenticationDatabase admin harmonizacao --eval "db.clientes.countDocuments()"
```

### 🌐 Teste de API
```powershell
# Health check da API
curl http://localhost:8002/v1/healthz

# Health check do cliente service
curl http://localhost:8002/v1/cliente/healthz

# Teste do endpoint de documentação
start http://localhost:80022/docs

# Teste simples de cliente (POST)
curl -X POST "http://localhost:8002/v1/cliente/formulario" -H "Content-Type: application/json" -d '{
  "nome": "Teste Cliente",
  "telefone": ["11999999999"],
  "email": ["teste@email.com"],
  "nascimento": "1990-01-01",
  "enderecos": []
}'
```

### 🧹 Limpeza e Manutenção
```powershell
# Parar todos os containers
docker-compose down

# Remover containers órfãos
docker-compose down --remove-orphans

# Limpar imagens não utilizadas
docker image prune

# Limpar sistema (containers, networks, volumes órfãos)
docker system prune

# Limpar tudo (⚠️ CUIDADO - remove tudo)
docker system prune -a --volumes

# Rebuild completo (limpa e reconstrói)
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### 🚨 Troubleshooting Rápido
```powershell
# Se não conseguir acessar API
docker-compose logs harmonizacao_app

# Se MongoDB não conectar
docker-compose logs mongodb

# Se porta estiver ocupada
netstat -ano | findstr :8002
netstat -ano | findstr :27017

# Resetar ambiente completo
docker-compose down --volumes
docker system prune -f
docker-compose up --build -d
```

## 📊 Verificação de Saúde

### MongoDB
```bash
docker-compose exec mongodb mongosh --eval "db.adminCommand('ping')"
```

### API
```bash
curl http://localhost:8002/v1/healthz
```

## 🔍 Monitoramento

### Status dos Containers
```bash
docker-compose ps
```

### Uso de Recursos
```bash
docker stats
```

### Logs de Inicialização
Os scripts de inicialização mostram:
- ✅ Collection `clientes` criada
- ✅ Índices otimizados aplicados
- ✅ Cliente de exemplo inserido
- 📊 Estatísticas do banco

## 🛠️ Personalização

### Variáveis de Ambiente (.env)
```env
# Obrigatório
GROQ_API_KEY=sua_chave_aqui

# MongoDB (opcional - valores padrão funcionam)
MONGODB_URL=mongodb://admin:admin123@mongodb:27017/harmonizacao?authSource=admin
MONGODB_DATABASE=harmonizacao
MONGODB_COLLECTION_CLIENTES=clientes

# API (opcional)
ENABLE_CORS=true
CORS_ALLOW_ORIGINS=["*"]

# Kafka (opcional)
KAFKA_ENABLED=true
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
KAFKA_TOPIC_CLIENTE=clientes
```

### Portas
- **API**: 8002 (configurável no docker-compose.yml)
- **MongoDB**: 27017 (configurável no docker-compose.yml)
 - **Kafka**: 9092 (broker), 9644 (admin - Redpanda)

## 🗃️ Persistência de Dados

Os dados do MongoDB são salvos localmente no diretório `C:\projects\db\harmonizacao\`. Este diretório:
- ✅ **Persiste** entre reinicializações do container
- ✅ **Mapeia diretamente** o sistema de arquivos do MongoDB
- ✅ **Facilita backup** (simples cópia de pasta)
- ✅ **Centralizado** para todos os projetos em `C:\projects\db\`
- ⚠️ **Não é versionado** no Git (.gitignore aplicado)

### Backup dos Dados
```bash
# Backup simples (cópia de diretório)
cp -r "C:\projects\db\harmonizacao" "C:\projects\db\backup-harmonizacao-$(date +%Y%m%d)"

# Backup via MongoDB (mais seguro)
docker-compose exec mongodb mongodump --uri="mongodb://admin:admin123@localhost:27017/harmonizacao?authSource=admin" --out=/data/backup

# Restore
docker-compose exec mongodb mongorestore --uri="mongodb://admin:admin123@localhost:27017/harmonizacao?authSource=admin" /data/backup/harmonizacao
```

### Localização dos Dados
- **Container**: `/data/db`
- **Host**: `C:\projects\db\harmonizacao\`
- **Mapeamento**: `C:/projects/db/harmonizacao:/data/db`

## 🚨 Troubleshooting

### **Problemas com PowerShell Scripts**

#### **Erro: "execução de scripts foi desabilitada"**
```
.\start.ps1 : O arquivo não pode ser carregado porque a execução de scripts foi desabilitada neste sistema.
```

**Soluções:**

##### **Opção 1: Alterar Política (Recomendada)**
```powershell
# Execute como Administrador
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Depois execute o script
.\start.ps1
```

##### **Opção 2: Bypass Temporário (Mais Seguro)**
```powershell
# Executa uma vez sem alterar política permanente
PowerShell -ExecutionPolicy Bypass -File .\start.ps1
```

##### **Opção 3: Desbloqueio do Arquivo**
```powershell
# Windows pode bloquear arquivos baixados
Unblock-File .\start.ps1

# Depois execute normalmente
.\start.ps1
```

##### **Opção 4: Comandos Manuais (Alternativa)**
```powershell
# Se não quiser usar scripts, execute manualmente:

# 1. Criar arquivo .env
if (!(Test-Path ".env")) { 
    Copy-Item ".env.example" ".env"
    Write-Host "Edite o arquivo .env com sua GROQ_API_KEY"
    notepad .env
}

# 2. Iniciar serviços
docker-compose up --build -d

# 3. Verificar status
docker-compose ps

# 4. Testar API
curl http://localhost:8002/v1/healthz
```

#### **Erro: "caracteres especiais" ou "string não tem terminador"**
```
A cadeia de caracteres não tem o terminador
```

**Solução:**
```powershell
# O arquivo pode ter problemas de codificação
# Use a versão manual ou recriar o arquivo

# Comando direto sem script:
docker-compose up --build -d
```

#### **Verificar Política Atual**
```powershell
# Ver política atual
Get-ExecutionPolicy

# Ver todas as políticas
Get-ExecutionPolicy -List
```

#### **Tipos de Política PowerShell**
- **Restricted** (Padrão): Não executa scripts
- **RemoteSigned** (Recomendada): Executa scripts locais e assinados remotos
- **Unrestricted**: Executa qualquer script (menos seguro)

### **Problemas com Docker**

### MongoDB não inicia
```bash
# Verificar logs
docker-compose logs mongodb

# Verificar permissões do diretório (Windows)
icacls "C:\projects\db\harmonizacao"

# Limpar dados locais (⚠️ perderá dados)
Remove-Item "C:\projects\db\harmonizacao\*" -Recurse -Force
docker-compose up -d mongodb
```

### API não conecta ao MongoDB
```bash
# Verificar rede
docker network ls
docker network inspect docker_harmonizacao_network

# Verificar variáveis de ambiente
docker-compose exec harmonizacao_app env | grep MONGODB
```

### Porta já em uso
```bash
# Verificar processos usando a porta
netstat -ano | findstr :8002
netstat -ano | findstr :27017

# Alterar portas no docker-compose.yml se necessário
```

## 📚 Estrutura de Arquivos

```
docker/
├── docker-compose.yml      # Configuração principal
├── Dockerfile             # Imagem da aplicação
├── .env.example           # Exemplo de variáveis
├── start.sh              # Script de inicialização (Linux/Mac)
├── start.ps1             # Script de inicialização (Windows)
├── README.md             # Esta documentação
└── init-scripts/
    └── 01-init-database.js   # Script de inicialização do MongoDB

C:/projects/db/harmonizacao/   # Dados do MongoDB (externo)
├── .gitignore             # Ignora dados no Git
└── [arquivos do MongoDB]  # Dados persistidos
```

---

## 📖 Quick Reference - Comandos Mais Usados

### 🚀 **Iniciar Ambiente**
```powershell
cd docker
.\start.ps1                    # Windows (automático)

# Se der erro de script bloqueado:
PowerShell -ExecutionPolicy Bypass -File .\start.ps1

# OU Manual
docker-compose up --build -d   # Manual
```

### 🔍 **Verificar Status**
```powershell
docker-compose ps             # Status dos containers
docker-compose logs -f        # Ver logs em tempo real
curl http://localhost:8002/v1/healthz  # Testar API
```

### 🛑 **Parar Ambiente**
```powershell
docker-compose down           # Parar tudo (mantém dados)
docker-compose down --volumes # Parar + apagar dados (⚠️)
```

### 🔧 **Debug/Manutenção**
```powershell
docker-compose logs mongodb           # Logs do MongoDB
docker-compose logs harmonizacao_app  # Logs da API
docker-compose restart               # Reiniciar tudo
docker-compose exec mongodb bash     # Entrar no container
```

### 🌐 **Acessos Rápidos**
- **API**: http://localhost:8002
- **Documentação**: http://localhost:8002/docs  
- **MongoDB**: localhost:27017 (admin/admin123)
- **Dados**: C:\projects\db\harmonizacao\

### 🆘 **Resolver Problemas**
```powershell
# Reset completo
docker-compose down --volumes
docker system prune -f
docker-compose up --build -d

# Verificar portas ocupadas
netstat -ano | findstr :8002
netstat -ano | findstr :27017
```

**💡 Dica**: Use sempre `.\start.ps1` para inicialização automática e verificação de problemas!