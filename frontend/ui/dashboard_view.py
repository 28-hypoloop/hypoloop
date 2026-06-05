"""실행 중 라이브 대시보드: 에이전트 콘솔 + 실시간 지표."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from backend.interface import PipelineInput, PipelineBackend
from ui import theme
from ui.dashboard_logic import DashboardState


def _metrics_df(metrics) -> pd.DataFrame:
    rows = [{"루프": m.loop_index, "베이스라인": m.baseline, "값": m.value}
            for m in metrics]
    return pd.DataFrame(rows).set_index("루프") if rows else pd.DataFrame()


def render(backend: PipelineBackend, inp: PipelineInput):
    """파이프라인을 실행하며 라이브 대시보드를 갱신. 완료 시 결과 반환."""
    theme.step_header(1)
    st.subheader("2. 에이전트 실행 — 라이브 대시보드")
    st.caption("🧠 LLM 호출 · 💻 생성 코드는 현재 데모(시뮬레이션)이며, "
               "데이터 적재·지표는 실제 백엔드를 사용합니다.")

    banner = st.empty()
    progress = st.progress(0.0)
    col_console, col_metric = st.columns([2, 1])
    console_box = col_console.empty()
    metric_box = col_metric.empty()
    chart_box = col_metric.empty()

    state = DashboardState()
    for ev in backend.run(inp):
        state.apply(ev)
        banner.markdown(
            theme.stage_banner_html(state.current_stage, state.current_loop,
                                    inp.loop_count),
            unsafe_allow_html=True)
        progress.progress(state.loop_progress(inp.loop_count))
        console_box.markdown(theme.console_html(state.console),
                             unsafe_allow_html=True)
        m = state.latest_metric()
        if m is not None:
            delta = round(m.value - m.baseline, 4)
            metric_box.metric(f"최신 {m.metric_name}", m.value,
                              delta if delta != 0 else None)
            df = _metrics_df(state.metrics)
            if not df.empty:
                chart_box.line_chart(df)

    progress.progress(1.0)
    return backend.get_result()
