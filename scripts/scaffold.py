#!/usr/bin/env python3
"""Copy a giovanibrioni app template and rename the app identity fields."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

TEMPLATES = {
    "python": {
        "repo": "https://github.com/giovanibrioni/python-template-api.git",
        "local": Path("/home/giovani/projects/templates/python-template"),
        "slug": "python-template",
    },
    "nextjs": {
        "repo": "https://github.com/giovanibrioni/nextjs-template.git",
        "local": Path("/home/giovani/projects/templates/nextjs-template"),
        "slug": "nextjs-template",
    },
    "go": {
        "repo": "https://github.com/giovanibrioni/golang-template.git",
        "local": Path("/home/giovani/projects/templates/golang-template"),
        "slug": "golang-template",
    },
}

RSYNC_EXCLUDES = [
    ".git",
    ".next",
    "node_modules",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    "tsconfig.tsbuildinfo",
    ".env",
]


def replacements(stack: str, name: str) -> dict[str, list[tuple[str, str]]]:
    if stack == "python":
        return {
            "pyproject.toml": [
                ('name = "python-template"', f'name = "{name}"'),
                (
                    'description = "Async FastAPI backend template organized by domain"',
                    f'description = "Async FastAPI backend for {name}"',
                ),
            ],
            "uv.lock": [
                (
                    '[[package]]\nname = "python-template"\nversion = "0.1.0"\nsource = { editable = "." }',
                    f'[[package]]\nname = "{name}"\nversion = "0.1.0"\nsource = {{ editable = "." }}',
                ),
            ],
            "README.md": [
                ("# python-template\n", f"# {name}\n"),
                (
                    "Async FastAPI backend template. The API runs on the host with `uv`. Postgres runs in Docker.",
                    f"{name} is an async FastAPI backend. The API runs on the host with `uv`. Postgres runs in Docker.",
                ),
            ],
            "AGENTS.md": [
                (
                    "The distribution name is `python-template`.",
                    f"The distribution name is `{name}`.",
                ),
            ],
            "app/core/config.py": [
                ('app_name: str = "python-template"', f'app_name: str = "{name}"'),
                (
                    'otel_service_name: str = "python-template"',
                    f'otel_service_name: str = "{name}"',
                ),
            ],
            ".env.example": [
                ("APP_NAME=python-template", f"APP_NAME={name}"),
                ("OTEL_SERVICE_NAME=python-template", f"OTEL_SERVICE_NAME={name}"),
            ],
        }
    if stack == "go":
        module = f"github.com/pocs-dev-br/{name}"
        return {
            "go.mod": [
                ("module github.com/giovanibrioni/golang-template", f"module {module}"),
            ],
            "README.md": [
                ("# golang-template\n", f"# {name}\n"),
                (
                    "Small Go HTTP API organized by domain. Shared infrastructure lives in `internal/core`; every other package under `internal/` is a domain. Postgres runs in Docker. The API runs on the host.",
                    f"{name} is a small Go HTTP API organized by domain. Shared infrastructure lives in `internal/core`; every other package under `internal/` is a domain. Postgres runs in Docker. The API runs on the host.",
                ),
            ],
            "internal/core/config/config.go": [
                (
                    'AppName:     getenv("APP_NAME", "golang-template")',
                    f'AppName:     getenv("APP_NAME", "{name}")',
                ),
            ],
            "cmd/api/main.go": [
                ('tracing.Init(ctx, "golang-template")', f'tracing.Init(ctx, "{name}")'),
            ],
            ".env.example": [
                ("APP_NAME=golang-template", f"APP_NAME={name}"),
            ],
        }
    return {
        "package.json": [
            ('"name": "nextjs-template"', f'"name": "{name}"'),
            (
                '"description": "Full-stack Next.js template with a separate frontend and backend, backed by Postgres."',
                f'"description": "{name} is a full-stack Next.js app with a separate frontend and backend, backed by Postgres."',
            ),
        ],
        "README.md": [
            ("# nextjs-template\n", f"# {name}\n"),
            (
                "Full-stack Next.js template. The app runs on the host with Node.js. Postgres runs in Docker.",
                f"{name} is a full-stack Next.js app. The app runs on the host with Node.js. Postgres runs in Docker.",
            ),
        ],
        "src/app/layout.tsx": [
            ('title: "nextjs-template"', f'title: "{name}"'),
        ],
        "src/backend/core/config.ts": [
            (
                'APP_NAME: z.string().default("nextjs-template")',
                f'APP_NAME: z.string().default("{name}")',
            ),
            (
                'OTEL_SERVICE_NAME: z.string().default("nextjs-template")',
                f'OTEL_SERVICE_NAME: z.string().default("{name}")',
            ),
        ],
        ".env.example": [
            ("APP_NAME=nextjs-template", f"APP_NAME={name}"),
            ("OTEL_SERVICE_NAME=nextjs-template", f"OTEL_SERVICE_NAME={name}"),
        ],
    }


def valid_name(name: str) -> bool:
    if not name or name[0] not in "abcdefghijklmnopqrstuvwxyz":
        return False
    previous_hyphen = False
    for char in name:
        if char == "-":
            if previous_hyphen:
                return False
            previous_hyphen = True
            continue
        previous_hyphen = False
        if char not in "abcdefghijklmnopqrstuvwxyz0123456789":
            return False
    return not name.endswith("-")


def destination_is_usable(dest: Path) -> None:
    if not dest.exists():
        dest.mkdir(parents=True)
        return
    extras = [path.name for path in dest.iterdir() if path.name != ".git"]
    if extras:
        listed = ", ".join(sorted(extras))
        raise SystemExit(
            f"destino não está vazio ({dest}): {listed}. "
            "Use uma pasta nova ou vazia (só .git é aceito)."
        )


def rsync_tree(source: Path, dest: Path) -> None:
    command = ["rsync", "-a"]
    for exclude in RSYNC_EXCLUDES:
        command.extend(["--exclude", exclude])
    command.extend([f"{source}/", f"{dest}/"])
    subprocess.run(command, check=True)


def fetch_github(repo: str, dest: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="create-app-") as tmp:
        clone_dir = Path(tmp) / "template"
        env = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}
        subprocess.run(
            ["git", "clone", "--depth", "1", repo, str(clone_dir)],
            check=True,
            env=env,
        )
        rsync_tree(clone_dir, dest)


def rewrite_go_module(dest: Path, name: str, changed: list[str]) -> None:
    old = "github.com/giovanibrioni/golang-template"
    new = f"github.com/pocs-dev-br/{name}"
    for path in dest.rglob("*.go"):
        text = path.read_text()
        if old not in text:
            continue
        path.write_text(text.replace(old, new))
        relative = str(path.relative_to(dest))
        if relative not in changed:
            changed.append(relative)


SLUG_FILES = {
    "python": [
        ".github/workflows/ci.yml",
        "deploy/namespace.yaml",
        "deploy/postgres.yaml",
        "deploy/app.yaml",
        "deploy/kustomization.yaml",
    ],
    "nextjs": [
        ".github/workflows/ci.yml",
        "deploy/namespace.yaml",
        "deploy/postgres.yaml",
        "deploy/app.yaml",
        "deploy/kustomization.yaml",
    ],
    "go": [
        ".github/workflows/ci.yml",
        "deploy/namespace.yaml",
        "deploy/postgres.yaml",
        "deploy/app.yaml",
        "deploy/kustomization.yaml",
    ],
}


def replace_slug_files(dest: Path, stack: str, name: str, changed: list[str]) -> None:
    slug = TEMPLATES[stack]["slug"]
    for relative in SLUG_FILES.get(stack, []):
        path = dest / relative
        if not path.is_file():
            raise SystemExit(f"arquivo esperado não existe no template: {relative}")
        text = path.read_text()
        if slug not in text:
            raise SystemExit(f"texto não encontrado em {relative}: {slug!r}")
        path.write_text(text.replace(slug, name))
        if relative not in changed:
            changed.append(relative)


def apply_replacements(dest: Path, stack: str, name: str) -> list[str]:
    changed: list[str] = []
    for relative, pairs in replacements(stack, name).items():
        path = dest / relative
        if not path.is_file():
            raise SystemExit(f"arquivo esperado não existe no template: {relative}")
        text = path.read_text()
        for old, new in pairs:
            if old not in text:
                raise SystemExit(f"texto não encontrado em {relative}: {old!r}")
            text = text.replace(old, new, 1)
        path.write_text(text)
        changed.append(relative)
    if stack == "go":
        rewrite_go_module(dest, name, changed)
    replace_slug_files(dest, stack, name, changed)
    return changed


def ensure_git(dest: Path) -> None:
    if (dest / ".git").exists():
        return
    subprocess.run(["git", "init", "-b", "main"], cwd=dest, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stack", required=True, choices=sorted(TEMPLATES))
    parser.add_argument("--name", required=True)
    parser.add_argument("--dest", required=True, type=Path)
    parser.add_argument("--source", choices=("github", "local"), default="github")
    args = parser.parse_args()

    if not valid_name(args.name):
        raise SystemExit(
            "nome inválido. Use kebab-case: letra minúscula, depois letras, números ou hífens "
            f"(recebido: {args.name!r})."
        )

    spec = TEMPLATES[args.stack]
    dest = args.dest.expanduser().resolve()
    destination_is_usable(dest)

    source_used = args.source
    if args.source == "github":
        try:
            fetch_github(spec["repo"], dest)
        except subprocess.CalledProcessError:
            local = spec["local"]
            if not local.is_dir():
                raise SystemExit(
                    f"clone falhou ({spec['repo']}) e o fallback local não existe: {local}"
                ) from None
            print(
                f"clone falhou; usando a cópia local em {local}",
                file=sys.stderr,
            )
            rsync_tree(local, dest)
            source_used = "local"
    else:
        local = spec["local"]
        if not local.is_dir():
            raise SystemExit(f"template local não existe: {local}")
        rsync_tree(local, dest)

    changed = apply_replacements(dest, args.stack, args.name)
    ensure_git(dest)
    print(f"source: {source_used}")
    print(f"stack: {args.stack}")
    print(f"name: {args.name}")
    print(f"dest: {dest}")
    print("updated:")
    for relative in changed:
        print(f"  {relative}")


if __name__ == "__main__":
    main()
