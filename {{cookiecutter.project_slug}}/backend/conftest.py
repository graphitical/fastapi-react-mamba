import typing as t

import pytest
from app.core import config, security
from app.db import models
from app.db.session import Base, get_db
from app.main import app
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import NullPool
from sqlalchemy_utils import create_database, database_exists, drop_database


def get_test_db_url() -> str:
    return f"{config.SQLALCHEMY_DATABASE_URI}_test"


@pytest.fixture(scope="session")
def engine():
    return create_engine(get_test_db_url(), poolclass=NullPool)


# Create/drop the test database once per session.
@pytest.fixture(scope="session", autouse=True)
def create_test_db(engine):
    url = get_test_db_url()
    assert not database_exists(
        url), "Test database already exists. Aborting tests."
    create_database(url)
    Base.metadata.create_all(engine)
    yield
    engine.dispose()  # ensure no open connections
    drop_database(url)


@pytest.fixture
def test_db(engine):
    connection = engine.connect()
    trans = connection.begin()

    # Use SQLAlchemy 2.0 style Session
    session = Session(bind=connection, expire_on_commit=False)
    session.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(s, t):
        if t.nested and not t._parent.nested:
            s.expire_all()
            s.begin_nested()

    try:
        yield session
    finally:
        session.close()
        trans.rollback()
        connection.close()


@pytest.fixture
def client(test_db):
    def _get_test_db():
        yield test_db

    app.dependency_overrides[get_db] = _get_test_db
    c = TestClient(app)
    try:
        yield c
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def test_password() -> str:
    return "securepassword"


def get_password_hash() -> str:
    # fast and deterministic for tests
    return "supersecrethash"


@pytest.fixture
def test_user(test_db) -> models.User:
    user = models.User(
        email="fake@email.com",
        hashed_password=get_password_hash(),
        is_active=True,
        first_name="",
        last_name=""
    )
    test_db.add(user)
    test_db.flush()  # no commit; stays inside the outer transaction
    return user


@pytest.fixture
def test_superuser(test_db) -> models.User:
    user = models.User(
        email="fakeadmin@email.com",
        hashed_password=get_password_hash(),
        is_superuser=True,
        first_name="",
        last_name=""
    )
    test_db.add(user)
    test_db.flush()
    return user


def verify_password_mock(first: str, second: str) -> bool:
    return True


@pytest.fixture
def user_token_headers(client: TestClient, test_user, test_password, monkeypatch) -> t.Dict[str, str]:
    monkeypatch.setattr(security, "verify_password", verify_password_mock)
    r = client.post(
        "/api/token", data={"username": test_user.email, "password": test_password})
    a_token = r.json()["access_token"]
    return {"Authorization": f"Bearer {a_token}"}


@pytest.fixture
def superuser_token_headers(client: TestClient, test_superuser, test_password, monkeypatch) -> t.Dict[str, str]:
    monkeypatch.setattr(security, "verify_password", verify_password_mock)
    r = client.post(
        "/api/token", data={"username": test_superuser.email, "password": test_password})
    a_token = r.json()["access_token"]
    return {"Authorization": f"Bearer {a_token}"}
