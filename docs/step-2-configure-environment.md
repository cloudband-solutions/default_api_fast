# 2) Configure the environment

## 2.1 Create your virtual environment
```bash
python -m venv env
source env/bin/activate
pip install -r requirements.txt
```

## 2.2 Create `.env`
Generated projects already include `.env`. If you are setting up this template
repository directly, create it from `.env.example`:

```bash
cp .env.example .env
```

Key settings:
- `APP_ENV`: `development`, `test`, or `production`
- `DATABASE_URL`: optional full override
- `DB_*`: component-based PostgreSQL settings used by `database.yaml`
- `SECRET_KEY`: JWT signing key
- `STORAGE_*`: local or S3-backed file storage
- `AWS_ENDPOINT`: point this to `http://localhost:4566` when using MiniStack
- `SQS_QUEUE_URL`: queue URL for the SQS queue the app should use

## 2.3 Local SQS with MiniStack
If your development flow uses SQS, start MiniStack in a separate terminal:

```bash
bin/start_ministack.sh
```

The script:
- starts MiniStack on `http://localhost:4566`
- creates a FIFO queue
- prints the `AWS_ENDPOINT` and `SQS_QUEUE_URL` values to export into your shell or save in `.env`

Typical local values look like:

```bash
AWS_ENDPOINT=http://localhost:4566
SQS_QUEUE_URL=http://localhost:4566/000000000000/tphlms.fifo
```

## 2.4 Default database names
`database.yaml` builds database names from `DB_NAME`:
- development: `${DB_NAME}_development`
- test: `${DB_NAME}_test`
- production: `${DB_NAME}`

For example, a generated project named `ragapi` uses:
- development: `ragapi_development`
- test: `ragapi_test`
- production: `ragapi`
