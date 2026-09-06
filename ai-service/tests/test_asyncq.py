"""Тесты асинхронной очереди генерации лекал (локальный fallback-режим)."""
import sys
import time
from pathlib import Path
from unittest.mock import Mock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.asyncq import (  # noqa: E402
    _broker_available,
    download_path,
    get_job,
    submit_render_job,
)
from app.pattern.render import RenderResult  # noqa: E402


def test_broker_available_returns_bool():
    assert isinstance(_broker_available(), bool)


def test_submit_and_poll_job_success(monkeypatch, tmp_path):
    png = tmp_path / "result.png"
    png.write_bytes(b"PNGDATA")

    def _fake_render(*args, **kwargs):
        return RenderResult(file_path=png, log="OK")

    monkeypatch.setattr("app.asyncq._broker_available", lambda: False)
    monkeypatch.setattr("app.asyncq.render_pattern", _fake_render)

    job_id = submit_render_job("skirt", {"waist_circ": 70})
    assert job_id

    deadline = time.time() + 5
    snapshot = None
    while time.time() < deadline:
        snapshot = get_job(job_id)
        if snapshot and snapshot.state == "SUCCESS":
            break
        time.sleep(0.05)

    assert snapshot is not None
    assert snapshot.state == "SUCCESS"
    assert snapshot.result["template"] == "skirt"
    assert download_path(job_id) == png


def test_submit_job_failure_recorded(monkeypatch):
    def _bad_render(*args, **kwargs):
        raise RuntimeError("docker crashed")

    monkeypatch.setattr("app.asyncq._broker_available", lambda: False)
    monkeypatch.setattr("app.asyncq.render_pattern", _bad_render)

    job_id = submit_render_job("skirt", {"waist_circ": 70})

    deadline = time.time() + 5
    snapshot = None
    while time.time() < deadline:
        snapshot = get_job(job_id)
        if snapshot and snapshot.state == "FAILURE":
            break
        time.sleep(0.05)

    assert snapshot is not None
    assert snapshot.state == "FAILURE"
    assert "docker crashed" in (snapshot.error or "")
    assert download_path(job_id) is None


def test_unknown_job_returns_none(monkeypatch):
    # если брокер недоступен и id не в локальных — задача неизвестна
    def _broken(*_a, **_k):
        raise RuntimeError("no broker")

    monkeypatch.setattr("app.asyncq.tasks.celery_app.AsyncResult", _broken)
    assert get_job("no-such-job") is None


def test_job_snapshot_dict_contains_download_url():
    from app.asyncq import JobSnapshot

    snap = JobSnapshot(
        job_id="x",
        state="SUCCESS",
        result={"png_path": "C:/tmp/a.png", "template": "skirt"},
    )
    data = snap.as_dict("localhost:8000")
    assert data["status"] == "success"
    assert data["download_url"] == "http://localhost:8000/api/patterns/jobs/x/result"
    assert data["error"] is None