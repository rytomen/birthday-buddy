from datetime import date

from app.birthdays import days_until_birthday, upcoming
from app.main import create_app


def make_client():
    app = create_app(database_url="sqlite:///:memory:")
    return app.test_client()


def test_health():
    client = make_client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_add_and_list_friend():
    client = make_client()
    response = client.post(
        "/api/friends",
        json={"name": "Ivan", "birth_date": "1990-06-15"},
    )
    assert response.status_code == 201
    listed = client.get("/api/friends").get_json()
    assert len(listed) == 1
    assert listed[0]["name"] == "Ivan"


def test_add_friend_validation():
    client = make_client()
    response = client.post("/api/friends", json={"name": "no date"})
    assert response.status_code == 400


def test_days_until_birthday():
    today = date(2026, 6, 1)
    assert days_until_birthday(date(1990, 6, 15), today=today) == 14


def test_upcoming_filters_and_sorts():
    today = date(2026, 6, 1)

    class FakeFriend:
        def __init__(self, name, birth_date):
            self.name = name
            self.birth_date = birth_date

    friends = [
        FakeFriend("Soon", date(1990, 6, 10)),
        FakeFriend("Later", date(1990, 12, 31)),
        FakeFriend("Today", date(1990, 6, 1)),
    ]
    result = upcoming(friends, within_days=30, today=today)
    assert [f.name for f in result] == ["Today", "Soon"]
