# SML lexical analyzer

This project combines the React/Vite interface with the authoritative Python
lexer in `backend/lexer.py`.

Lexer design and CLI documentation live in `backend/README.md`. Demo-ready SML
inputs and their expected outcomes are documented in `examples/README.md`.

## Local setup

Install the frontend and backend dependencies:

```powershell
corepack pnpm install
python -m pip install -r requirements.txt
```

Start the Python API in one terminal:

```powershell
npm run dev:api
```

Start the website in another terminal:

```powershell
npm run dev
```

The `npm run` commands work even when `pnpm` is not installed globally. The
repository pins its package manager version, so `corepack pnpm ...` can be used
for lockfile-aware dependency installation.

Vite proxies requests under `/api` to `http://127.0.0.1:8000`. Set
`SML_API_URL` before starting Vite if the API uses a different address.

## Checks

```powershell
python -m unittest backend.test_server backend.test_examples backend.test_operators backend.test_words
npm run build
```
