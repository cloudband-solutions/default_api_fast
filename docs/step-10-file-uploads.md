# 10) File uploads (local + S3)

The upload controller stores files through `app/storage.py`. Two storage modes
are supported:
- `local`
- `s3`

## 10.1 Local storage
Default local storage uses:
- root: `storage/`
- public endpoint: `/api/files/{key}`

Upload a file:
```bash
curl -F file=@avatar.png http://127.0.0.1:3000/api/uploads
```

## 10.2 S3 storage
Set:
```bash
STORAGE_SERVICE=s3
STORAGE_S3_BUCKET=your-bucket
STORAGE_S3_REGION=ap-southeast-1
```

You can also set:
- `STORAGE_S3_ENDPOINT`
- `STORAGE_S3_PREFIX`
- `STORAGE_S3_PUBLIC_URL`
- `STORAGE_S3_ACL`
