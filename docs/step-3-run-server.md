# 3) Run the server

Start the development server:
```bash
./bin/rake server
```

This runs:
```bash
uvicorn main:app --host 127.0.0.1 --port 3000 --reload
```

Useful endpoints:
- `GET /api/health`
- `POST /api/login`
- `GET /api/users`
- `POST /api/uploads`
