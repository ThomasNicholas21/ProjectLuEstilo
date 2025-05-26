
# 📦 API de Gerenciamento de Pedidos

## 💡 Descrição do Projeto
Esta API, desenvolvida com FastAPI e SQLAlchemy, gerencia autenticação de usuários, clientes, produtos e pedidos (Order & OrderItem). O sistema utiliza PostgreSQL em container Docker, alembic para migrações, autenticação JWT, validação de CPF e controle de permissão por perfis. Sentry integra o rastreamento de erros, e o fluxo está coberto por testes automatizados.

## 🎯 Funcionalidades
- **Auth**: login, registro e refresh de token JWT  
- **Clientes**: CRUD de clientes com validação de CPF  
- **Produtos**: CRUD de produtos com estoque e categorias  
- **Pedidos**: criação, listagem (com filtros), atualização e remoção de pedidos e items  
- **Logs de Erro**: captura automática via Sentry  
- **Validações**: CPF, perfis de usuário (role_validator)  

## 💻 Tecnologias Utilizadas
- **FastAPI**
- **Pydantic**
- **SQLAlchemy** + **Alembic**  
- **PostgreSQL** (via Docker)  
- **JWT** (PyJWT + passlib + bcrypt)  
- **pytest** 
- **python-dotenv**, **python-multipart**, **httpx**  
- **Sentry SDK**
  
## 🚀 Deploy
A aplicação está hospedada no Render (Docker + variáveis de ambiente):  
🌐 https://projectluestilo.onrender.com

## 📝 Logs e Monitoramento
- **Sentry**: captura exceções automaticamente. Configure `SENTRY_DSN` no `.env`.

## 🙋‍♂️ Como Rodar o Projeto

### 1. Preparar Ambiente Local (sem Docker)
```bash
# Clone o repositório
git clone https://github.com/seu-usuario/seu-projeto.git
cd seu-projeto

# Crie e ative venv
python -m venv venv
source venv/bin/activate     # Linux/macOS
venv\Scripts\activate        # Windows

# Instale dependências
pip install -r requirements.txt

# Configure .env
cp dotenv/.env_example dotenv/.env
# Preencha as variáveis: DATABASE_URL, SECRET_KEY, SENTRY_DSN, ENVIRONMENT=development.

```

### 2. Com Docker
```bash
# Na raiz do projeto
docker-compose up --build
```

O serviço ficará disponível em `http://localhost:8000` e a documentação interativa em `http://localhost:8000/docs`.

## ✅ Testes
```bash
# Dentro do venv ou container
docker-compose run --rm lu_estilo_api pytest --maxfail=1 --disable-warnings -q
```

---

Feito por **Thomas Nicholas**
