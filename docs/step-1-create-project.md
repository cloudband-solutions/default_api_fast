# 1) Create a new project from this codebase

## 1.1 Generate the project
Run this from the template repository:

```bash
bin/create_project.sh /home/ralampay/workspace/cloudband/ragapi "RAG API"
cd /home/ralampay/workspace/cloudband/ragapi
```

The generator copies this template, removes local-only files, creates `.env`
from `.env.example`, initializes a fresh git repository, and replaces:
- `default_api_fast` with the new snake_case project name
- `default-api-fast-secret` with the new default secret
- `Default API Fast` with the display name

If the display name is omitted, the generator derives one from the target
directory name:

```bash
bin/create_project.sh ../ragapi
```

## 1.2 Install and verify
```bash
python -m venv env
source env/bin/activate
pip install -r requirements.txt
python -m app.cli db:create
python -m app.cli db:upgrade
python -m app.cli system:seed
python -m app.cli spec
```

## 1.3 Create the initial commit
```bash
git add .
git commit -m "Initial commit"
```
