# 3) Run the server

If your app uses SQS locally, start MiniStack first in a separate terminal:

```bash
bin/start_ministack.sh
```

Export the `AWS_ENDPOINT` and `SQS_QUEUE_URL` values printed by that script
before starting the app server.

Start the development server:
```bash
python -m app.cli server
```

This runs:
```bash
uvicorn main:app --host 127.0.0.1 --port 3000 --reload
```

Useful endpoints:
- `GET /health`
- `POST /login`
- `/users` CRUD endpoints require an authenticated admin user
- `POST /uploads`
