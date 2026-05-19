# ChitGit

ChitGit is a full-stack repository chat assistant that lets you upload a GitHub repo, index its code, and ask questions against it in a conversational UI.

## Highlights

- GitHub authentication with Clerk.
- Repository ingestion and background upload jobs.
- Semantic search over repository chunks using Qdrant and sentence-transformers.
- Chat responses grounded in the uploaded repository content.
- Separate React/Vite client and FastAPI Python server.

## Tech Stack

- Client: React 19, TypeScript, Vite, Tailwind CSS, Clerk, Axios.
- Server: FastAPI, SQLModel/Pydantic, Qdrant, Sentence Transformers, Uvicorn.
- Local services: Redis via Docker Compose.

## Repository Layout

```text
Client/   React application
Server/   FastAPI backend and workers
docker-compose.yml   Local Redis service
```

## Prerequisites

- Node.js 20 or newer.
- pnpm.
- Python 3.11 or newer.
- Docker and Docker Compose.

## Environment Setup

Create a `Server/.env` file and supply your own values for the backend services.

```bash
cp Server/.env.example Server/.env
```

## Run Locally

1. Start Redis:

```bash
docker compose up -d
```

2. Install and start the server:

```bash
cd Server
python -m venv .venv
source .venv/bin/activate
pip install -r requirement.txt
uvicorn main:app --reload --port 8000
```

3. Install and start the client:

```bash
cd Client
pnpm install
pnpm dev
```

The client is configured to talk to `http://localhost:8000`.

## Validation

- Client: `pnpm lint` and `pnpm build` inside `Client/`.
- Server: `python -m compileall Server`.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).