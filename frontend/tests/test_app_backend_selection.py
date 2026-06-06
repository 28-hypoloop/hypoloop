def test_get_backend_default_is_not_api(monkeypatch):
    # 통합 브랜치: env 없으면 DataLayerBackend(hypoloop 설치 시) 또는 MockBackend
    monkeypatch.delenv("HYPOLOOP_API_URL", raising=False)
    import app
    assert type(app.get_backend()).__name__ in ("DataLayerBackend", "MockBackend")


def test_get_backend_is_api_when_env_set(monkeypatch):
    monkeypatch.setenv("HYPOLOOP_API_URL", "http://localhost:9999")
    import app
    assert type(app.get_backend()).__name__ == "ApiBackend"
