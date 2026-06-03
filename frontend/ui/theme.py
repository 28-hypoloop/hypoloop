"""화면 간 일관된 스타일·헬퍼."""
from __future__ import annotations

import streamlit as st

# 색상 토큰
PRIMARY = "#2563eb"
SUCCESS = "#16a34a"
WARNING = "#d97706"
MUTED = "#6b7280"

# 결과 신뢰성 경계 문구(기획서 정책)
DISCLAIMER = (
    "⚠️ 제한된 데이터·환경에서 도출된 결과이므로, "
    "프로덕션 적용 전 반드시 검토가 필요합니다."
)

# 3단계 라벨
STEPS = ["1 입력", "2 분석", "3 결과"]


def step_header(active_index: int) -> None:
    """상단 스텝 표시. active_index: 0=입력,1=분석,2=결과."""
    cols = st.columns(len(STEPS))
    for i, (col, label) in enumerate(zip(cols, STEPS)):
        if i < active_index:
            col.markdown(f"✅ **{label}**")
        elif i == active_index:
            col.markdown(f":blue[**▶ {label}**]")
        else:
            col.markdown(f":gray[{label}]")
    st.divider()


def disclaimer_banner() -> None:
    """결과 신뢰성 경계 문구 배너."""
    st.warning(DISCLAIMER)


def page_setup() -> None:
    """페이지 공통 설정. 앱 진입점에서 1회 호출."""
    st.set_page_config(
        page_title="ML 자동화 에이전트",
        page_icon="🤖",
        layout="wide",
    )
