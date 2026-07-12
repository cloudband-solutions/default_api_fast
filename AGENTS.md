# Code Conventions

## Workflow

- Write tests first before implementing a feature or changing behavior.
- Add or update the relevant spec under `spec/` first, confirm the failure, then implement the code.
- Keep controllers thin and move business logic into command objects under `app/operations`.

## Models

- Place SQLAlchemy models in `app/models`.
- Inherit from `Base` in `app.db`.
- Define `__tablename__` explicitly.
- Use typed SQLAlchemy mappings with `Mapped[...]` and `mapped_column(...)`.
- Keep persistence concerns and small model helpers on the model, such as `to_dict()`, status predicates, and lightweight state transitions like `soft_delete()`.
- Follow the existing `User` model style for timestamps, ids, and serialization.

## Controllers

- Place route handlers in `app/controllers/<resource>_controller.py`.
- Define a module-level `router = APIRouter(...)`.
- Keep request handlers focused on HTTP concerns: parsing input, dependency injection, auth, calling an operation, and shaping the HTTP response.
- Use Pydantic schemas from `app/schemas` for request and response contracts.
- Inject the database session with `Depends(get_db)`.
- Reuse auth dependencies like `require_active_user` for protected endpoints.
- Register new routers in `app/routes.py`.
- When an endpoint performs business rules, validation, creation, updates, or other domain behavior, delegate that work to an operation instead of embedding it in the controller.

## Operations

- Implement business logic using the command pattern in `app/operations/<domain>`.
- Use one class per action, matching the existing pattern such as `Save` in `app/operations/users/save.py` and `Login` in `app/operations/system/login.py`.
- Operation objects should receive their dependencies and inputs in `__init__`, expose `execute()`, and store results on the instance such as `user` or `payload`.
- For validation-oriented commands, inherit from `Validator`, populate `payload`, and use `valid()` or `invalid()` after `execute()`.
- Controllers should instantiate the command, call `execute()`, and translate the result into the HTTP response.

Example command pattern, based on `Save` and `Login`:

```python
from app.operations.validator import Validator


class CreateWidget(Validator):
    def __init__(self, session, name=None):
        super().__init__()
        self.session = session
        self.name = name
        self.widget = None
        self.payload = {"name": []}

    def execute(self):
        if not self.name:
            self.payload["name"].append("required")

        self.count_errors()

        if self.valid():
            self.widget = Widget(name=self.name)
            self.session.add(self.widget)
            self.session.commit()
            self.session.refresh(self.widget)
```

The controller should only coordinate the command and HTTP response:

```python
command = CreateWidget(session=db, name=request.name)
command.execute()

if command.invalid():
    raise HTTPException(status_code=422, detail=command.payload)

return command.widget
```

## Tests

- Keep specs under `spec/<resource>/test_<action>.py`.
- Follow the existing pytest style with simple request/response assertions.
- Use `client` for API requests, `db_session` when database setup is needed, and `auth_headers` for protected endpoints.
- Use factories from `spec/factories.py` for database records instead of hand-building persisted objects.
- Cover the happy path first, then add failure cases for validation, missing records, and authentication when relevant.
- When adding a new feature, update specs before implementation and keep the new code aligned with the existing request-level testing style.
