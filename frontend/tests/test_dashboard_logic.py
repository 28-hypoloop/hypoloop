from backend.interface import ProgressEvent, MetricRecord
from ui.dashboard_logic import DashboardState, ConsoleItem


def ev(kind="stage", stage="EDA", loop=0, status="running", message="m",
       detail="", metric=None):
    return ProgressEvent(stage=stage, loop_index=loop, status=status,
                         message=message, kind=kind, detail=detail, metric=metric)


def test_stage_event_tracks_current_and_done():
    s = DashboardState()
    s.apply(ev(kind="stage", stage="베이스라인", loop=0, status="running"))
    assert s.current_stage == "베이스라인"
    assert s.current_loop == 0
    s.apply(ev(kind="stage", stage="베이스라인", loop=0, status="done"))
    assert "베이스라인" in s.stages_done


def test_console_accumulates_llm_code_log():
    s = DashboardState()
    s.apply(ev(kind="llm", detail="Solar 호출"))
    s.apply(ev(kind="code", detail="print(1)"))
    s.apply(ev(kind="log", message="로그줄"))
    assert len(s.console) == 3
    assert [c.kind for c in s.console] == ["llm", "code", "log"]
    assert s.console[0].text == "Solar 호출"
    assert s.console[2].text == "로그줄"


def test_console_capped_at_max():
    s = DashboardState(max_console=5)
    for i in range(8):
        s.apply(ev(kind="log", message=f"l{i}"))
    assert len(s.console) == 5
    assert s.console[0].text == "l3"


def test_metric_event_accumulates_and_latest():
    s = DashboardState()
    m0 = MetricRecord(loop_index=0, metric_name="accuracy", baseline=0.7, value=0.7)
    m1 = MetricRecord(loop_index=1, metric_name="accuracy", baseline=0.7, value=0.8)
    s.apply(ev(kind="metric", metric=m0))
    s.apply(ev(kind="metric", metric=m1))
    assert len(s.metrics) == 2
    assert s.latest_metric().value == 0.8


def test_latest_metric_none_when_empty():
    assert DashboardState().latest_metric() is None


def test_loop_progress_advances_each_loop():
    s = DashboardState()
    s.apply(ev(stage="베이스라인", loop=0))
    p0 = s.loop_progress(3)
    s.apply(ev(stage="피처엔지니어링", loop=1))
    p1 = s.loop_progress(3)
    s.apply(ev(stage="튜닝", loop=2))
    p2 = s.loop_progress(3)
    assert p0 < p1 < p2   # 루프마다 단조 증가(정체 없음)


def test_loop_progress_reaches_one_at_report():
    s = DashboardState()
    s.apply(ev(stage="리포트", loop=3))
    assert s.loop_progress(3) == 1.0


def test_loop_progress_zero_when_no_loops():
    assert DashboardState().loop_progress(0) == 0.0
