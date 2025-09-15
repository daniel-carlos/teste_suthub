# Testes com Pytest

Este projeto inclui testes abrangentes para a API FastAPI usando pytest.

## Estrutura dos Testes

- `tests/conftest.py` - Configurações e fixtures compartilhadas
- `tests/test_api.py` - Testes principais para todos os endpoints da API
- `tests/test_integration.py` - Testes de integração com dados realistas usando Faker
- `tests/requirements.txt` - Dependências específicas para testes
- `pytest.ini` - Configuração do pytest

## Dependências dos Testes

```
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2
faker==19.12.0
mongomock==4.1.2
python-dotenv==1.0.0
```

## Como Executar os Testes

### Opção 1: Usando o script batch (Windows)
```bash
run_tests.bat
```

### Opção 2: Manualmente
```bash
# Instalar dependências dos testes
pip install -r tests/requirements.txt

# Executar todos os testes
pytest tests/ -v

# Executar testes específicos
pytest tests/test_api.py -v
pytest tests/test_integration.py -v

# Executar um teste específico
pytest tests/test_api.py::TestRootEndpoint::test_read_root -v
```

## Cobertura dos Testes

Os testes cobrem:

### Endpoints da API:
- ✅ `GET /` - Endpoint raiz
- ✅ `GET /enroll` - Listar matrículas
- ✅ `POST /enroll` - Criar matrícula
- ✅ `GET /enroll/{id}` - Obter matrícula específica
- ✅ `PUT /enroll/{id}` - Atualizar matrícula
- ✅ `DELETE /enroll/{id}` - Deletar matrícula
- ✅ `GET /age-groups` - Listar grupos etários
- ✅ `POST /age-groups` - Criar grupo etário
- ✅ `PUT /age-groups/{id}` - Atualizar grupo etário
- ✅ `DELETE /age-groups/{id}` - Deletar grupo etário

### Cenários de Teste:
- ✅ Operações bem-sucedidas
- ✅ Validação de dados de entrada
- ✅ Tratamento de erros (IDs inválidos, registros não encontrados)
- ✅ Casos extremos (idades fora de faixa, dados faltando)
- ✅ Testes com dados realistas usando Faker
- ✅ Operações em lote

### Tipos de Teste:
- **Testes Unitários**: Testam endpoints individuais isoladamente
- **Testes de Integração**: Testam fluxos completos com dados realistas
- **Testes de Validação**: Verificam validação de entrada e tratamento de erros

## Estrutura dos Testes

### test_api.py
- `TestRootEndpoint`: Testa o endpoint raiz
- `TestAgeGroupEndpoints`: Testa operações CRUD para grupos etários
- `TestEnrollEndpoints`: Testa operações CRUD para matrículas
- `TestDataValidation`: Testa validação de dados de entrada

### test_integration.py
- `TestWithFakeData`: Testes com dados gerados pelo Faker
- Testes de casos extremos
- Testes de operações em lote

## Mocking

Os testes usam mocking para:
- **MongoDB**: Mock das operações de banco de dados usando `unittest.mock`
- **Coleções**: Mock das coleções MongoDB para isolar os testes
- **Respostas**: Mock das respostas do banco para cenários específicos

## Executando Testes Específicos

```bash
# Apenas testes de grupos etários
pytest tests/test_api.py::TestAgeGroupEndpoints -v

# Apenas testes de matrícula
pytest tests/test_api.py::TestEnrollEndpoints -v

# Apenas testes de validação
pytest tests/test_api.py::TestDataValidation -v

# Apenas testes com dados falsos
pytest tests/test_integration.py::TestWithFakeData -v
```

## Relatórios de Teste

Para gerar relatórios mais detalhados:

```bash
# Relatório com detalhes de falhas
pytest tests/ -v --tb=long

# Relatório resumido
pytest tests/ --tb=short

# Apenas mostrar falhas
pytest tests/ --tb=no
```
