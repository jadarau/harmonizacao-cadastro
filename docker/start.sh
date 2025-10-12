#!/bin/bash

# Script para inicializar o ambiente Docker da aplicação Harmonização

echo "🚀 Iniciando ambiente Docker da aplicação Harmonização..."

# Verifica se o Docker está rodando
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker não está rodando. Por favor, inicie o Docker e tente novamente."
    exit 1
fi

# Verifica se o arquivo .env existe
if [ ! -f ".env" ]; then
    echo "⚠️  Arquivo .env não encontrado."
    echo "📋 Copiando .env.example para .env..."
    cp .env.example .env
    echo "✏️  Por favor, edite o arquivo .env e adicione sua GROQ_API_KEY"
    echo "📁 Arquivo .env criado em: $(pwd)/.env"
    
    # No Windows, abrir o arquivo no editor padrão
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        start .env
    fi
    
    read -p "🔑 Digite sua GROQ_API_KEY: " groq_key
    if [ ! -z "$groq_key" ]; then
        sed -i "s/sua_api_key_aqui/$groq_key/" .env
        echo "✅ GROQ_API_KEY configurada!"
    fi
fi

echo "🐳 Construindo e iniciando containers..."

# Para containers existentes
docker-compose down

# Remove volumes orfãos
docker-compose down --volumes --remove-orphans

# Constrói e inicia os serviços
docker-compose up --build -d

echo "⏳ Aguardando inicialização dos serviços..."

# Aguarda o MongoDB estar saudável
echo "🔍 Verificando saúde do MongoDB..."
timeout=60
while [ $timeout -gt 0 ]; do
    if docker-compose exec mongodb mongosh --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
        echo "✅ MongoDB está rodando!"
        break
    fi
    echo "⏳ Aguardando MongoDB... ($timeout segundos restantes)"
    sleep 2
    ((timeout-=2))
done

if [ $timeout -le 0 ]; then
    echo "❌ Timeout aguardando MongoDB. Verificando logs..."
    docker-compose logs mongodb
    exit 1
fi

# Aguarda a aplicação estar pronta
echo "🔍 Verificando saúde da aplicação..."
timeout=30
while [ $timeout -gt 0 ]; do
    if curl -s http://localhost:8002/v1/healthz > /dev/null 2>&1; then
        echo "✅ Aplicação está rodando!"
        break
    fi
    echo "⏳ Aguardando aplicação... ($timeout segundos restantes)"
    sleep 2
    ((timeout-=2))
done

echo ""
echo "🎉 Ambiente Docker iniciado com sucesso!"
echo ""
echo "📊 Serviços disponíveis:"
echo "  🌐 API: http://localhost:8002"
echo "  📚 Documentação: http://localhost:8002/docs"
echo "  🗄️  MongoDB: localhost:27017"
echo ""
echo "🔧 Comandos úteis:"
echo "  📋 Ver logs: docker-compose logs -f"
echo "  🛑 Parar: docker-compose down"
echo "  🔄 Reiniciar: docker-compose restart"
echo ""
echo "📁 Collections criadas:"
echo "  📝 clientes (com índices otimizados)"
echo "💾 Dados salvos em: C:/projects/db/harmonizacao/"
echo ""

# Mostra status dos containers
docker-compose ps