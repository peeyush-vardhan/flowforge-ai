# FlowForge AI Monorepo

FlowForge AI is an AI workflow builder that converts natural language into executable workflow graphs.

## Structure

- `apps/web` — Next.js + TypeScript + Tailwind + shadcn-style UI + React Flow front-end.
- `apps/api` — FastAPI (Python 3.11) service that compiles natural language into workflow graphs.
- `packages/shared-types` — shared workflow graph TypeScript types.
- `packages/node-registry` — typed catalog of built-in workflow nodes.
- `docs` — product and API documentation (placeholder).
- `evals` — evaluation prompt JSONs (placeholder).
- `examples` — sample workflow graph JSONs.

## Getting started

1. Install Node.js (LTS) and Python 3.11.
2. From the repo root, install JS dependencies:

```bash
npm install
```

3. Install Python dependencies for the API:

```bash
cd apps/api
pip install -e ".[dev]"
```

4. From the repo root, run both web and API in dev mode:

```bash
npm run dev
```

The web app will typically run on `http://localhost:3000` and the API on `http://localhost:8000`.

## Environment variables

See `.env.example` for configuration. The current setup does not require any secrets to run locally.

