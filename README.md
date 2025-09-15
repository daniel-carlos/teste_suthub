# Teste Suthub — API + Queue System

Guia rápido para executar o projeto localmente (sem Docker) e com Docker Compose.

## Requisitos
- Git
- Python 3.12+ e pip
- Docker Desktop (para usar Docker/Docker Compose)
- Windows (testado no Windows; outras plataformas podem funcionar com ajustes)
- Opcional: MongoDB instalado localmente (se não quiser usar Docker para o Mongo)

## 1) Clonar o repositório
```cmd
git clone https://github.com/daniel-carlos/teste_suthub.git
cd teste_suthub
```

## 2) Variáveis de ambiente
Este repositório NÃO versiona arquivos `.env`. Use os exemplos e copie-os:

- Para Docker Compose (na raiz):
```cmd
copy .env-example .env
```
- Para execução local (sem Docker):
```cmd
copy api\.env-example api\.env
copy queue_system\.env-example queue_system\.env
```

Valores padrão sugeridos:
- `DB_USERNAME=daniel`
- `DB_PASSWORD=daniel`
- Para local (sem Docker): `DB_HOST=localhost`
- Para Docker Compose, o host é definido via compose como `mongo` (não precisa ajustar nos .env locais quando usar apenas Docker).

---

## 3) Rodando com Docker Compose
1) Na raiz, confirme que existe o arquivo `.env` (criado a partir de `.env-example`).
2) Suba os serviços (API, Queue e MongoDB):
```cmd
docker compose up -d --build
```
3) API disponível em: http://localhost:8000
4) Logs (opcional):
```cmd
docker compose logs -f api
```
5) Parar e remover:
```cmd
docker compose down
```

---

## 4) Rodando local (sem Docker)
### 4.1) Subir o MongoDB
Opção recomendada (usar Docker apenas para o Mongo):
```cmd
docker run -d --name mongo -p 27017:27017 ^
  -e MONGO_INITDB_ROOT_USERNAME=daniel ^
  -e MONGO_INITDB_ROOT_PASSWORD=daniel ^
  mongo:6.0
```
Isso inicia o MongoDB com usuário/senha de root (daniel/daniel) em `localhost:27017`.

### 4.2) Preparar e iniciar a API
Em um terminal:
```cmd
cd api
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn run:app --host 0.0.0.0 --port 8000 --reload
```
API em http://localhost:8000

### 4.3) Iniciar o Queue System
Em outro terminal:
```cmd
cd queue_system
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python run.py
```
O processo lerá mensagens da coleção `messageCollection` e atualizará os cadastros.

---

## 5) Testes com pytest
Os testes estão em `api/tests` e usam `mongomock`, então NÃO é necessário ter MongoDB ou Docker rodando.

### Instalar dependências de teste e executar
```cmd
cd api
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install pytest mongomock
pytest -q
```

### Executar um arquivo ou teste específico
```cmd
# Arquivo específico
pytest -q tests\test_age_groups.py

# Mostrar prints/logs durante os testes
pytest -q -s
```

### Saída detalhada (verbose)
```cmd
pytest -v
```

---

## Endpoints úteis
- GET `http://localhost:8000/` — health check simples
- GET `http://localhost:8000/age-groups`
- POST `http://localhost:8000/age-groups`
- GET `http://localhost:8000/enroll`
- POST `http://localhost:8000/enroll`

## Observações
- Se a API não conectar no Mongo, verifique se o Mongo está ativo em `localhost:27017` (execução local) ou se os serviços do Compose estão de pé.
- No Docker Compose, os serviços usam `DB_HOST=mongo` automaticamente e dependem do serviço `mongo`.

## Autenticação

Autenticação para as rotas de gerenciamento.

- As credenciais ficam no arquivo `api/credentials.json` no formato:

```
{
  "users": [
    { "username": "admin", "password": "admin", "token": "secreta-palavra" }
  ]
}
```

- Faça login em `POST /auth/login` com:

```
{ "username": "admin", "password": "admin" }
```

Resposta:

```
{ "token": "secreta-palavra" }
```

- Para criar/atualizar/apagar age groups envie o header:

```
X-Token: secreta-palavra
```

As rotas de leitura (GET) e as demais entidades continuam abertas.

## Arquivos usados para o desenvolvimento
A pasta `_tests` contém dois arquivos que criei para facilitar o desenvolvimento e irão facilitar os testes:
- **seed_age_group.py**: cria 3 age_groups
- **seed.py**: cria enrolls em larga escala (passe um argumento informando a quantidade `python seed.py 7` para criar 7 enrolls ou deixe vazio para criar uma quantidade aleatória de enrolls entre 2 a 8)

> Importante: para rodar os arquivos, o serviço `api` precisa estar rodando