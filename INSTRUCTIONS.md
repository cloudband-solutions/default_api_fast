# Quick Start

```bash
cp .env.example .env
python -m venv env
source env/bin/activate
pip install -r requirements.txt
./bin/rake db.create
./bin/rake db.upgrade
./bin/rake server
```

Run specs with:

```bash
./bin/spec
```
