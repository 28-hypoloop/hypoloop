"""ML 자동화 에이전트 — Streamlit 진입점. 세션 상태로 세 화면을 라우팅."""
from __future__ import annotations

import streamlit as st

from backend.mock import MockBackend
from ui import theme, input_form, progress_view, report_viewer


def get_backend():
    """백엔드 주입 지점. 통합 시 MockBackend()를 실제 구현으로 교체."""
    return MockBackend()


def main() -> None:
    theme.page_setup()
    st.title("🤖 ML 자동화 에이전트")

    if "view" not in st.session_state:
        st.session_state.view = "input"
        st.session_state.pipeline_input = None
        st.session_state.result = None

    backend = get_backend()
    view = st.session_state.view

    if view == "input":
        inp = input_form.render(backend)
        if inp is not None:
            st.session_state.pipeline_input = inp
            st.session_state.view = "running"
            st.rerun()

    elif view == "running":
        # 실제 백엔드의 run()/get_result()는 실패할 수 있다(네트워크·OOM·모델 오류).
        # 사용자가 진행 화면에 갇히지 않도록 오류를 안내하고 입력으로 돌아갈 길을 준다.
        try:
            result = progress_view.render(backend, st.session_state.pipeline_input)
        except Exception as exc:  # noqa: BLE001 - 사용자에게 그대로 안내
            st.error(f"분석 중 오류가 발생했습니다: {exc}")
            if st.button("입력 화면으로 돌아가기"):
                st.session_state.view = "input"
                st.rerun()
            return
        st.session_state.result = result
        st.session_state.view = "report"
        st.rerun()

    elif view == "report":
        report_viewer.render(st.session_state.result)
        if st.button("새 분석 시작"):
            st.session_state.view = "input"
            st.session_state.pipeline_input = None
            st.session_state.result = None
            st.rerun()


if __name__ == "__main__":
    main()
