import pytest


@pytest.fixture
def db_path(tmp_path):
    return tmp_path / "test.db"


@pytest.fixture
def sample_csv(tmp_path):
    csv_file = tmp_path / "sample.csv"
    csv_file.write_text("a,b,c\n1,2,3\n4,5,6\n7,8,9\n", encoding="utf-8")
    return csv_file
