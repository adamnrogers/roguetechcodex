# RogueTech Codex

A locally hosted, searchable wiki for the [RogueTech](https://roguetech.fandom.com/wiki/RogueTech_Wiki) BattleTech mod. Ingests mech, vehicle, weapon, and equipment definitions from mod JSON files and serves a browsable interface.

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- A local copy of the RogueTech mod

## Setup

1. Copy `.env.example` to `.env` and point `RT_ROOT` at your RogueTech mod directory:

   ```env
   RT_ROOT=/path/to/RogueTech
   ```

2. Build images and run the pipeline to generate the database:

   ```sh
   make fresh
   ```

   Then open **http://localhost** (port 80).

On subsequent starts (database already exists):

```sh
make up
```

## Make Targets

### Production

| Target              | What it does                                              |
|---------------------|-----------------------------------------------------------|
| `make fresh`        | Full rebuild: ingest data + start services                |
| `make up`           | Start API + frontend (requires `roguetech.db`)            |
| `make down`         | Stop all services                                         |
| `make build`        | Rebuild Docker images                                     |
| `make pipeline`     | Re-run data ingestion (rebuilds `roguetech.db`)           |
| `make logs`         | Tail all service logs                                     |
| `make logs-api`     | Tail API logs only                                        |
| `make shell-api`    | Shell into the running API container                      |
| `make shell-pipeline` | Interactive pipeline debugging shell                    |
| `make ps`           | Show running containers                                   |

### Development

| Target              | What it does                                              |
|---------------------|-----------------------------------------------------------|
| `make dev`          | Start API + frontend with hot reload (source-mounted)     |
| `make dev-down`     | Stop dev services                                         |
| `make dev-build`    | Rebuild dev images (after `requirements.txt`/`package.json` changes) |
| `make dev-pipeline` | Rebuild `roguetech.db` in dev mode                        |
| `make dev-logs`     | Tail dev logs                                             |

## Architecture

```
RT_ROOT (mod JSON files)
  → pipeline   Python 3.11 - classifies and ingests JSON into SQLite
  → roguetech.db
  → api        FastAPI + aiosqlite - REST endpoints
  → frontend   Vue 3 SPA - browsable grid + detail views
```

| Layer    | Technology                    | Port |
|----------|-------------------------------|------|
| Pipeline | Python 3.11 + SQLite          | -    |
| API      | FastAPI + aiosqlite           | 8000 |
| Frontend | Vue 3 + Vite, served by nginx | 80   |

In production nginx serves the built frontend on port 80 and reverse-proxies `/api` to the backend container.

## API Endpoints

| Method | Path                        | Description                    |
|--------|-----------------------------|--------------------------------|
| GET    | `/api/v1/mechs`             | List chassis with filters/sort |
| GET    | `/api/v1/mechs/{chassis_id}`| Chassis detail + variants      |
| GET    | `/health`                   | Health check                   |

## Development

Hot reload - no image rebuild needed when editing Python or Vue files:

```sh
make dev           # start API + frontend
make dev-down      # stop
make dev-build     # rebuild after requirements.txt or package.json changes
make dev-pipeline  # rebuild roguetech.db
make dev-logs      # tail output
```

Frontend is at **http://localhost:5173**, API at **http://localhost:8000**.

<details>
<summary>Running without Docker</summary>

**Frontend**:
```sh
cd frontend/src && npm install && npm run dev
```

**API**:
```sh
cd api && uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Pipeline**:
```sh
cd pipeline && python -m pipeline.ingest --full-rebuild
```
</details>
