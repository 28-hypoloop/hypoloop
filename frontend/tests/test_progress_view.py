from ui.progress_view import progress_fraction


def test_progress_advances_each_loop():
    # 루프가 진행될수록 진행률이 단조 증가(정체되지 않음)
    assert progress_fraction(0, 3) < progress_fraction(1, 3) < progress_fraction(2, 3)


def test_progress_reaches_one_at_report():
    # 마지막 루프(리포트) 시점에 100% 도달
    assert progress_fraction(3, 3) == 1.0


def test_progress_starts_above_zero_at_baseline():
    assert 0.0 < progress_fraction(0, 3) < 1.0


def test_progress_clamped_to_one():
    # 혹시 loop_index가 loop_count를 넘어도 1.0을 넘지 않음
    assert progress_fraction(5, 3) == 1.0
