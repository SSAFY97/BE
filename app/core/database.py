from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db() -> None:
    from app.models.post import Post

    inspector = inspect(engine)
    if "posts" in inspector.get_table_names():
        columns = {column["name"] for column in inspector.get_columns("posts")}
        if "writer" not in columns:
            # Preserve legacy anonymous posts while bringing the MVP schema forward.
            with engine.begin() as connection:
                connection.execute(
                    text("ALTER TABLE posts ADD COLUMN writer VARCHAR(100) NOT NULL DEFAULT '익명'")
                )
    Base.metadata.create_all(bind=engine)
