---
name: create-app
description: >-
  Scaffolds a new app from the giovanibrioni Python (FastAPI), Next.js, or Go
  templates: clones the template and renames the app identity fields (package
  name, description, APP_NAME, OTEL service name, README title). Use when the
  user asks to create a new app or project from these templates, in Portuguese
  or English — for example "criar a app users-api em python", "novo projeto
  nextjs chamado billing-web", "create an app from the python template",
  "scaffold a next.js app", or "criar app golang users-service".
---

# Create app from template

Cria um projeto novo a partir dos templates em `github.com/giovanibrioni`. O script aplica as trocas de nome. Não reimplemente a cópia nem o replace.

## Origem dos templates

Clone do GitHub. A pasta local só entra se o clone falhar (sem rede ou sem acesso ao repo privado).

| Stack | Repositório | Fallback local |
|-------|-------------|----------------|
| `python` | `https://github.com/giovanibrioni/python-template-api.git` | `/home/giovani/projects/templates/python-template` |
| `nextjs` | `https://github.com/giovanibrioni/nextjs-template.git` | `/home/giovani/projects/templates/nextjs-template` |
| `go` | `https://github.com/giovanibrioni/golang-template.git` | `/home/giovani/projects/templates/golang-template` |

O GitHub é a origem porque o clone traz só o que está commitado, sem `.git` do template, `.next`, `node_modules` ou caches. Mudança local no template só entra no app novo depois do push, a menos que o clone falhe e o script use o fallback.

## O que extrair do pedido

- **Nome da app** em kebab-case: `users-api`. Se o usuário escrever `Users API` ou `users_api`, normalize para `users-api` e use esse nome.
- **Stack**: `python` para python, py, fastapi ou uv. `nextjs` para next, next.js, nextjs. `go` para golang, go. Se faltar um dos dois, pergunte. Não chute.

O destino é o diretório de trabalho atual quando o usuário está na pasta do projeto novo. Se ele der outro caminho, use esse caminho. A pasta precisa estar vazia ou conter só `.git`.

## Executar

```bash
python3 ~/.cursor/skills/create-app/scripts/scaffold.py \
  --stack python \
  --name users-api \
  --dest .
```

`--source local` só quando o usuário pedir a cópia local de propósito.

O script falha se algum texto esperado não existir mais no template. Nesse caso, atualize `replacements()` em `scripts/scaffold.py` para o texto novo e rode de novo numa pasta limpa. Não faça replace solto no restante do repositório.

Não rode `make install`, não crie commit e não faça push. O script só faz `git init` quando a pasta ainda não tem `.git`.

## O que é renomeado

Só a identidade da app. O slug antigo (`python-template`, `nextjs-template`, ou `golang-template`) vira o nome novo nestes arquivos:

**Python**

- `pyproject.toml`: `name` e `description` (`Async FastAPI backend for {nome}`)
- `uv.lock`: o pacote editável `source = { editable = "." }`
- `README.md`: título e a primeira frase
- `AGENTS.md`: a frase `The distribution name is \`{nome}\`.`
- `app/core/config.py`: defaults de `app_name` e `otel_service_name`
- `.env.example`: `APP_NAME` e `OTEL_SERVICE_NAME`

**Next.js**

- `package.json`: `name` e `description`
- `README.md`: título e a primeira frase
- `src/app/layout.tsx`: `metadata.title`
- `src/backend/core/config.ts`: defaults de `APP_NAME` e `OTEL_SERVICE_NAME`
- `.env.example`: `APP_NAME` e `OTEL_SERVICE_NAME`

**Go**

- `go.mod`: `module github.com/giovanibrioni/golang-template` → `module github.com/giovanibrioni/{nome}`
- `README.md`: título e a primeira frase
- `config.yaml`: `app_name` e `service_name`
- `.env.example`: `APP_NAME` e `OTEL_SERVICE_NAME`

## O que não muda

- O pacote Python continua `app`. Imports `app.*` ficam.
- O banco continua `app` e o banco de teste `app_test` (`DATABASE_URL`, `POSTGRES_DB`, `docker/postgres/init.sql`).
- As skills de review e os caminhos no `Makefile` (`.cursor/skills/python-template-review` e `.cursor/skills/nextjs-template-review`) permanecem com esses nomes.
- Domínio de exemplo `items`, portas e o restante do template.

## Depois

Diga o nome, o stack, a origem usada (`github` ou `local`) e os arquivos alterados. Aponte os comandos do README (`make install`, `make up`, `make migrate`, `make dev`) sem executá-los.
