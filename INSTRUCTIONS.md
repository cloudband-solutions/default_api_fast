# Quick Start

```bash
cp .env.example .env
python -m venv env
source env/bin/activate
pip install -r requirements.txt
python -m app.cli db.create
python -m app.cli db.upgrade
python -m app.cli server
```

Run specs with:

```bash
python -m app.cli spec
```
