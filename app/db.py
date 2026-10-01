from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):
    pass


class DatabaseManager:
    def __init__(self):
        self.engine = None
        self.session_factory = None

    def configure(self, database_url):
        url = make_url(database_url)
        in_memory = url.get_backend_name() == "sqlite" and url.database in (None, "", ":memory:")
        # CLI commands can configure the active database again within the same process.
        if in_memory and self.engine is not None and self.engine.url == url:
            return
        if self.engine is not None:
            self.engine.dispose()

        options = {}
        if url.get_backend_name() == "sqlite":
            options["connect_args"] = {"check_same_thread": False}
            if in_memory:
                options["poolclass"] = StaticPool
        self.engine = create_engine(url, future=True, **options)
        self.session_factory = sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    def session(self):
        if self.session_factory is None:
            raise RuntimeError("Database has not been configured.")
        return self.session_factory()


db = DatabaseManager()


def get_db():
    session = db.session()
    try:
        yield session
    finally:
        session.close()
