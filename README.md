# Easy-CMDB-REST-API

A REST API for Easy CMDB, a configuration management database for tracking IT assets (servers, applications, databases, network devices and more) and their lifecycle status.

Built with [FastAPI](https://fastapi.tiangolo.com/), [SQLModel](https://sqlmodel.tiangolo.com/) and [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/).

## Requirements

- Python 3.14
- [uv](https://docs.astral.sh/uv/)

## Getting started

```bash
uv sync               # install dependencies into .venv
uv run fastapi dev    # start the development server with auto-reload
```

The API is then available at <http://127.0.0.1:8000>, with interactive docs at:

- Swagger UI: <http://127.0.0.1:8000/docs>
- ReDoc: <http://127.0.0.1:8000/redoc>

The database tables are created automatically on startup. By default the data is stored in a local SQLite file, `cmdb.db`.

To run in production mode, use `uv run fastapi run`.

## Configuration

Settings are read from environment variables prefixed with `CMDB_`, or from a `.env` file in the project root.

| Variable             | Default                  | Description                                   |
| -------------------- | ------------------------ | --------------------------------------------- |
| `CMDB_APP_NAME`      | `Easy CMDB REST API`     | Title shown in the API docs                   |
| `CMDB_DATABASE_URL`  | `sqlite:///./cmdb.db`    | SQLAlchemy database URL                       |
| `CMDB_ECHO_SQL`      | `false`                  | Log every SQL statement (useful for debugging) |
| `CMDB_MAX_BODY_SIZE` | `1048576` (1 MiB)        | Maximum request body size in bytes            |

Example `.env`:

```dotenv
CMDB_DATABASE_URL=sqlite:///./cmdb.db
CMDB_ECHO_SQL=true
```

`.env` is git-ignored. Don't commit credentials.

## API overview

| Method   | Path                          | Description                          |
| -------- | ----------------------------- | ------------------------------------ |
| `GET`    | `/health`                     | Service and database health check    |
| `GET`    | `/configuration-items/`       | List configuration items             |
| `POST`   | `/configuration-items/`       | Create a configuration item          |
| `GET`    | `/configuration-items/{id}`   | Get a configuration item             |
| `PATCH`  | `/configuration-items/{id}`   | Partially update a configuration item |
| `DELETE` | `/configuration-items/{id}`   | Delete a configuration item          |

Listing supports these query parameters:

- `ci_type`: filter by type (`server`, `virtual_machine`, `application`, `database`, `network_device`, `storage`, `service`, `other`)
- `status`: filter by status (`planned`, `active`, `maintenance`, `retired`)
- `offset` / `limit`: pagination (`limit` defaults to 50, maximum 100)

Example:

```bash
curl -X POST http://127.0.0.1:8000/configuration-items/ \
  -H 'Content-Type: application/json' \
  -d '{"name": "web-01", "ci_type": "server", "status": "active", "owner": "ops"}'

curl 'http://127.0.0.1:8000/configuration-items/?ci_type=server&status=active'
```

See `/docs` for full request and response schemas.

## Project structure

```text
src/easy_cmdb_rest_api/
├── main.py                 # App factory, lifespan and router registration
├── config.py               # Settings (CMDB_* environment variables)
├── database.py             # Database engine and session dependency
├── models.py               # SQLModel table and request/response models
└── routers/
    ├── health.py           # /health
    └── configuration_items.py  # /configuration-items
tests/                      # pytest suite (uses an in-memory SQLite database)
```

## Development

```bash
uv run pytest                    # run the tests
uv run ruff check .              # lint
uv run ruff format .             # format
uv run ty check src tests        # type-check
```

The [CI workflow](.github/workflows/ci.yml) runs the same checks on every pull request and push to `main`. It also fails if `uv.lock` is out of date with `pyproject.toml`.

Add dependencies with `uv add <package>`, or `uv add --dev <package>` for development-only tools.

## Security scanning

The [Security workflow](.github/workflows/security.yml) runs on every pull request, on pushes to `main`, weekly, and on demand. Any finding fails the build.

| Check            | Type | What it covers                                                   |
| ---------------- | ---- | ---------------------------------------------------------------- |
| Bandit           | SAST | Common Python security issues in `src/`                          |
| Semgrep          | SAST | Python, FastAPI and GitHub Actions rulesets across the repo      |
| pip-audit        | SCA  | Known vulnerabilities in every package pinned in `uv.lock`       |

[Dependabot](.github/dependabot.yml) proposes weekly updates for Python packages and GitHub Actions, waiting 7 days after each release.

To run the same scans locally:

```bash
uvx bandit --recursive src
uvx semgrep scan --config p/python --config p/fastapi --config p/github-actions --metrics=off --error
uv export --frozen --no-emit-project --all-groups --format requirements-txt -o /tmp/req.txt \
  && uvx pip-audit -r /tmp/req.txt --disable-pip --strict
```

## Roadmap

- Database migrations with Alembic (tables are currently created on startup)
- Authentication and authorisation
- Relationships between configuration items

## License

Released under the [MIT License](LICENSE).
