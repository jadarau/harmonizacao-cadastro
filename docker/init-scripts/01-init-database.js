// Script de inicialização do MongoDB para criar a collection de clientes
// Este script é executado automaticamente quando o container é iniciado pela primeira vez

print("🚀 Iniciando configuração do banco de dados harmonizacao...");

// Conecta ao banco de dados
db = db.getSiblingDB('harmonizacao');

// Cria a collection de clientes se não existir
if (!db.getCollectionNames().includes('clientes')) {
    print("📁 Criando collection 'clientes'...");
    
    // Cria a collection
    db.createCollection('clientes', {
        validator: {
            $jsonSchema: {
                bsonType: "object",
                required: ["nome", "nascimento"],
                properties: {
                    nome: {
                        bsonType: "string",
                        description: "Nome do cliente é obrigatório"
                    },
                    telefone: {
                        bsonType: "array",
                        items: {
                            bsonType: "string"
                        },
                        description: "Array de telefones"
                    },
                    email: {
                        bsonType: "array",
                        items: {
                            bsonType: "string"
                        },
                        description: "Array de emails"
                    },
                    nascimento: {
                        bsonType: "string",
                        description: "Data de nascimento é obrigatória"
                    },
                    enderecos: {
                        bsonType: "array",
                        items: {
                            bsonType: "object",
                            properties: {
                                logradouro: { bsonType: "string" },
                                numero: { bsonType: "string" },
                                complemento: { bsonType: "string" },
                                bairro: { bsonType: "string" },
                                cidade: { bsonType: "string" },
                                estado: { bsonType: "string" },
                                cep: { bsonType: "string" },
                                tipo: { bsonType: "string" }
                            }
                        }
                    },
                    created_at: {
                        bsonType: "date",
                        description: "Data de criação"
                    },
                    updated_at: {
                        bsonType: "date",
                        description: "Data de atualização"
                    }
                }
            }
        }
    });
    
    print("✅ Collection 'clientes' criada com sucesso!");
} else {
    print("ℹ️  Collection 'clientes' já existe.");
}

// Cria índices para otimizar consultas
print("🔍 Criando índices...");

db.clientes.createIndex({ "email": 1 }, { name: "idx_email" });
db.clientes.createIndex({ "telefone": 1 }, { name: "idx_telefone" });
db.clientes.createIndex({ "nome": 1 }, { name: "idx_nome" });
db.clientes.createIndex({ "created_at": -1 }, { name: "idx_created_at" });

print("✅ Índices criados com sucesso!");

// Insere um cliente de exemplo (opcional)
if (db.clientes.countDocuments() === 0) {
    print("📝 Inserindo cliente de exemplo...");
    
    db.clientes.insertOne({
        nome: "Cliente Exemplo",
        telefone: ["11987654321"],
        email: ["exemplo@email.com"],
        nascimento: "1990-01-01",
        enderecos: [{
            logradouro: "Rua Exemplo",
            numero: "123",
            bairro: "Centro",
            cidade: "São Paulo",
            estado: "SP",
            cep: "01234567",
            tipo: "residencial"
        }],
        created_at: new Date(),
        updated_at: new Date()
    });
    
    print("✅ Cliente de exemplo inserido!");
}

print("🎉 Configuração do banco de dados concluída com sucesso!");
print("📊 Collections disponíveis:", db.getCollectionNames());
print("📈 Total de clientes:", db.clientes.countDocuments());