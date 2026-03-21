# 4) Run with Gunicorn

For a production-style process model:
```bash
gunicorn main:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:3000
```

You can still keep `bin/rake server` for local development and reserve
Gunicorn for deployment or staging parity.
