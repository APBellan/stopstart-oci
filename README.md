# StopStart OCI

Aplicação para gerenciar stop/start de instâncias no OCI, com:

- Mapeamento automático por compartments via SDK OCI
- Navegação hierárquica de compartments
- Configuração individual de instâncias via popup
- Scheduler para aplicar stop/start/reboot

## Desenvolvimento

### Requisitos

- Docker + Docker Compose
- Git
- VSCode (recomendado)

### Subir ambiente de desenvolvimento

```bash
cd deploy
docker compose -f docker-compose.dev.yml up --build

## Migrações de Banco de Dados (Alembic)

O projeto já está configurado com Alembic (`backend/alembic` e `backend/alembic.ini`),  
então **não é necessário rodar `alembic init`** em nenhum ambiente.

As migrações sempre são executadas **dentro do container `api`**, via `docker compose`.

---

### Estrutura

- Backend (API): `backend/`
- Docker Compose: `deploy/docker-compose.yml`
- Serviço da API no Docker Compose: `api`
- Serviço do Postgres no Docker Compose: `db`
- Banco de dados:
  - host (dentro da rede Docker): `db:5432`
  - usuário/senha: `stopstart / stopstart`
  - nome do banco: `stopstart`

A variável de ambiente `DATABASE_URL` é definida no serviço `api`:

## Aplicar migrations

Para aplicar todas as migrations pendentes (do estado atual até a última disponível – head):

cd deploy
docker compose exec api alembic upgrade head


Isso roda o upgrade() de cada migration na ordem correta e atualiza a tabela alembic_version no banco.

## Ver histórico de migrations

# Listar o histórico:

cd deploy
docker compose exec api alembic history


# Ver a migration atualmente aplicada:

cd deploy
docker compose exec api alembic current

## Fazer downgrade (voltar uma versão)

# Se precisar voltar uma versão:

cd deploy
docker compose exec api alembic downgrade -1


# Ou voltar para uma revision específica:

# Exemplo: voltar para a initial_schema
docker compose exec api alembic downgrade 14b7965b718d


⚠️ Cuidado: downgrades podem quebrar dados (drop de colunas, tabelas etc.). Use apenas em ambiente de desenvolvimento/homologação, ou com um plano de migração reversível em produção.

Fluxo típico de desenvolvimento

Alterar/Adicionar models em app/models/....

# Gerar migration:

docker compose exec api alembic revision --autogenerate -m "minha mudança"


Revisar o arquivo criado em alembic/versions/.

# Aplicar:

docker compose exec api alembic upgrade head

