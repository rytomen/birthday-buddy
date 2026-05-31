import json
import os
import time
from datetime import date

from flask import Flask, Response, g, jsonify, request
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.birthdays import upcoming
from app.cache import Cache
from app.db import init_db, make_engine, make_session_factory
from app.metrics import (
    active_requests,
    friends_added_total,
    friends_total,
    http_request_duration_seconds,
    http_requests_total,
)
from app.models import Friend


def create_app(database_url=None, redis_url=None):
    app = Flask(__name__)
    engine = make_engine(database_url)
    init_db(engine)
    session_factory = make_session_factory(engine)
    cache = Cache(redis_url)

    def count_friends():
        session = session_factory()
        try:
            return session.query(Friend).count()
        finally:
            session.close()

    @app.before_request
    def _start_timer():
        g.start_time = time.time()
        active_requests.inc()

    @app.after_request
    def _record_metrics(response):
        endpoint = request.url_rule.rule if request.url_rule else request.path
        duration = time.time() - getattr(g, "start_time", time.time())
        http_request_duration_seconds.labels(endpoint).observe(duration)
        http_requests_total.labels(
            request.method, endpoint, str(response.status_code)
        ).inc()
        active_requests.dec()
        return response

    @app.get("/metrics")
    def metrics():
        friends_total.set(count_friends())
        return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.get("/")
    def index():
        return "<h1>BirthdayBuddy</h1><p>Трекер дней рождения друзей.</p>"

    @app.get("/api/friends")
    def list_friends():
        session = session_factory()
        try:
            friends = session.query(Friend).order_by(Friend.name).all()
            return jsonify([f.to_dict() for f in friends])
        finally:
            session.close()

    @app.post("/api/friends")
    def add_friend():
        data = request.get_json(silent=True) or {}
        name = data.get("name")
        birth_date = data.get("birth_date")
        if not name or not birth_date:
            return jsonify({"error": "name and birth_date are required"}), 400
        try:
            parsed = date.fromisoformat(birth_date)
        except ValueError:
            return jsonify({"error": "birth_date must be YYYY-MM-DD"}), 400
        session = session_factory()
        try:
            friend = Friend(name=name, birth_date=parsed)
            session.add(friend)
            session.commit()
            result = friend.to_dict()
        finally:
            session.close()
        cache.delete("upcoming")
        friends_added_total.inc()
        return jsonify(result), 201

    @app.get("/api/upcoming")
    def upcoming_friends():
        cached = cache.get("upcoming")
        if cached is not None:
            return app.response_class(cached, mimetype="application/json")
        session = session_factory()
        try:
            friends = session.query(Friend).all()
            soon = upcoming(friends)
            payload = json.dumps([f.to_dict() for f in soon])
        finally:
            session.close()
        cache.set("upcoming", payload)
        return app.response_class(payload, mimetype="application/json")

    return app


app = create_app()


if __name__ == "__main__":
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8000"))
    app.run(host=host, port=port)
