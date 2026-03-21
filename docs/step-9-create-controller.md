# 9) Create a controller (example: Project)

Add `app/controllers/projects_controller.py`:
```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db


router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("")
def index(session: Session = Depends(get_db)):
    return {"records": []}
```

Then register it in `app/routes.py`:
```python
from app.controllers.projects_controller import router as projects_router

api_router.include_router(projects_router)
```

This keeps the same controller-per-domain structure used by the Flask starter,
but uses FastAPI routers and dependencies instead of Flask blueprints and
decorators.
