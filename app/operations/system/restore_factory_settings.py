import app.models  # noqa: F401
from app.db import Base
from app.operations.users.save import Save as SaveUser


class RestoreFactorySettings:
    def __init__(self, session):
        self.session = session
        self.user = None

    def execute(self):
        for table in reversed(Base.metadata.sorted_tables):
            self.session.execute(table.delete())

        command = SaveUser(
            session=self.session,
            email="admin@example.com",
            first_name="Admin",
            last_name="Example",
            role="admin",
            password="password",
            password_confirmation="password",
        )
        command.execute()

        if command.invalid():
            self.session.rollback()
            raise RuntimeError(f"Could not restore factory settings: {command.payload}")

        self.user = command.user
