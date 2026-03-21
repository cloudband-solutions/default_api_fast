# 1) Create a new project from this codebase

## 1.1 Copy the repository
```bash
cp -R /home/ralampay/workspace/cloudband/default_api_fast /home/ralampay/workspace/cloudband/ragapi
cd /home/ralampay/workspace/cloudband/ragapi
```

## 1.2 Update the project naming defaults
Search and replace the default name with your new one:
```bash
rg -n "default_api_fast|default-api-fast|Default API Fast"
```

Update these files first:
- `README.md`
- `config.py`
- `spec/settings.py`
- `.env.example`
- `.env.test`

Suggested defaults:
- `default_api_fast` -> `ragapi`
- `default-api-fast-secret` -> `ragapi-secret`
- `Default API Fast` -> `RAG API`

Example edits:
```python
# config.py
SQLALCHEMY_DATABASE_URI = os.getenv(
    "DATABASE_URL",
    _db_config.get("uri", "postgresql+psycopg://postgres:postgres@localhost:5432/ragapi_development"),
)
SECRET_KEY = os.getenv("SECRET_KEY", "ragapi-secret")
```

```python
# spec/settings.py
SQLALCHEMY_DATABASE_URI = _db_config.get(
    "uri",
    "postgresql+psycopg://postgres:postgres@localhost:5432/ragapi_test",
)
```

## 1.3 Start a fresh git repository
If you copied this project to start a new service, remove the original git
history and initialize your own repository:
```bash
rm -rf .git
git init
git add .
git commit -m "Initial commit"
```
