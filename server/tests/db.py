from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker


TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
