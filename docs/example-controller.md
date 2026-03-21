# Example Controller

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db


router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("")
def index(session: Session = Depends(get_db)):
    return {"records": []}
```
