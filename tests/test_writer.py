import yaml

from hypoloop.data.writer import build_experiment_dict, write_experiment_yml


def test_write_experiment_yml_creates_file(tmp_path):
    exp = build_experiment_dict(
        name="test_exp",
        dataset="titanic",
        hypothesis="Pclass affects survival",
        metric="accuracy",
    )
    path, yml_str = write_experiment_yml(exp, tmp_path / "exp.yml")
    assert path.exists()


def test_write_experiment_yml_returns_string(tmp_path):
    exp = build_experiment_dict(
        name="test_exp",
        dataset="titanic",
        hypothesis="Pclass affects survival",
        metric="accuracy",
    )
    path, yml_str = write_experiment_yml(exp, tmp_path / "exp.yml")
    assert isinstance(yml_str, str)
    assert len(yml_str) > 0


def test_write_experiment_yml_string_matches_file(tmp_path):
    exp = build_experiment_dict(
        name="test_exp",
        dataset="titanic",
        hypothesis="Pclass affects survival",
        metric="accuracy",
    )
    path, yml_str = write_experiment_yml(exp, tmp_path / "exp.yml")
    assert path.read_text(encoding="utf-8") == yml_str


def test_write_experiment_yml_sort_keys_false(tmp_path):
    exp = {"z_key": 1, "a_key": 2, "m_key": 3}
    _, yml_str = write_experiment_yml(exp, tmp_path / "order.yml")
    keys = [line.split(":")[0].strip() for line in yml_str.strip().splitlines()]
    assert keys == ["z_key", "a_key", "m_key"]


def test_write_experiment_yml_allow_unicode(tmp_path):
    exp = {"가설": "등급이 생존에 영향을 준다", "지표": "정확도"}
    _, yml_str = write_experiment_yml(exp, tmp_path / "unicode.yml")
    assert "가설" in yml_str
    assert "등급이 생존에 영향을 준다" in yml_str


def test_build_experiment_dict_required_keys():
    exp = build_experiment_dict(
        name="exp1",
        dataset="titanic",
        hypothesis="some hypothesis",
        metric="accuracy",
    )
    for key in ("name", "dataset", "hypothesis", "metric", "params", "created_at"):
        assert key in exp


def test_build_experiment_dict_params_default_empty():
    exp = build_experiment_dict(
        name="exp1",
        dataset="titanic",
        hypothesis="h",
        metric="accuracy",
    )
    assert exp["params"] == {}


def test_build_experiment_dict_params_passed_through():
    exp = build_experiment_dict(
        name="exp1",
        dataset="titanic",
        hypothesis="h",
        metric="accuracy",
        params={"n_estimators": 100},
    )
    assert exp["params"] == {"n_estimators": 100}


def test_write_experiment_yml_roundtrip(tmp_path):
    exp = build_experiment_dict(
        name="roundtrip",
        dataset="iris",
        hypothesis="feature X matters",
        metric="f1",
        params={"max_depth": 5},
    )
    path, _ = write_experiment_yml(exp, tmp_path / "rt.yml")
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert loaded["name"] == "roundtrip"
    assert loaded["params"]["max_depth"] == 5
