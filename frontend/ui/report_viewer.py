"""최종 보고서 뷰어(리포트/지표/코드/실험설정 탭)."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from backend.interface import PipelineResult
from ui import theme


def _metrics_dataframe(result: PipelineResult) -> pd.DataFrame:
    rows = [
        {
            "루프": m.loop_index,
            "지표": m.metric_name,
            "베이스라인": m.baseline,
            "값": m.value,
            "향상폭(Δ)": round(m.value - m.baseline, 4),
        }
        for m in result.metrics_history
    ]
    return pd.DataFrame(rows)


def render(result: PipelineResult) -> None:
    """보고서 화면 렌더링."""
    theme.step_header(2)
    st.subheader("3. 분석 결과")
    theme.disclaimer_banner()

    tab_report, tab_metric, tab_code, tab_yaml = st.tabs(
        ["📄 리포트", "📈 성능지표", "💻 코드", "⚙️ 실험설정"]
    )

    with tab_report:
        st.markdown(result.report_md)
        st.download_button("리포트 다운로드 (.md)", result.report_md,
                           file_name="report.md", mime="text/markdown")

    with tab_metric:
        df = _metrics_dataframe(result)
        if not df.empty:
            chart_df = df.set_index("루프")[["베이스라인", "값"]]
            st.line_chart(chart_df)
            st.dataframe(df, width="stretch")
            best = df.iloc[-1]
            st.metric(label=f"최종 {best['지표']}", value=best["값"],
                      delta=best["향상폭(Δ)"])
        else:
            st.info("지표 데이터가 없습니다.")

    with tab_code:
        st.code(result.final_code, language="python")
        st.download_button("코드 다운로드 (.py)", result.final_code,
                           file_name="pipeline.py", mime="text/x-python")

    with tab_yaml:
        st.code(result.experiment_yaml, language="yaml")
        st.download_button("실험설정 다운로드 (.yml)", result.experiment_yaml,
                           file_name="experiment.yml", mime="text/yaml")
