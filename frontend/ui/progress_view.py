"""진행 상태 실시간 표시 화면."""
from __future__ import annotations

import streamlit as st

from backend.interface import PipelineInput, PipelineBackend
from ui import theme


def progress_fraction(loop_index: int, loop_count: int) -> float:
    """루프 진행 기준 진행률(계약 정보만 사용).

    loop_index 0(베이스라인)부터 loop_count(리포트)까지 단조 증가하며
    리포트 단계에서 1.0에 도달한다. 단계 집합 기반과 달리 다중 루프에서
    진행률이 정체되지 않는다.
    """
    return min((loop_index + 1) / (loop_count + 1), 1.0)


def render(backend: PipelineBackend, inp: PipelineInput):
    """파이프라인을 실행하며 진행 상태를 실시간 표시. 완료 시 결과 반환."""
    theme.step_header(1)
    st.subheader("2. 파이프라인 실행 중")

    total_loops = inp.loop_count
    progress = st.progress(0.0)
    stage_box = st.empty()
    log_area = st.container()

    with st.status("분석을 시작합니다…", expanded=True) as status:
        for ev in backend.run(inp):
            label = f"[루프 {ev.loop_index}/{total_loops}] {ev.stage} — {ev.message}"
            stage_box.markdown(f"**현재:** {label}")
            log_area.write(label)
            progress.progress(progress_fraction(ev.loop_index, total_loops))
        status.update(label="분석 완료", state="complete")

    return backend.get_result()
