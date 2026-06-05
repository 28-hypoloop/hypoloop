"""화면 간 일관된 스타일·헬퍼."""
from __future__ import annotations

import html as _html

import streamlit as st

# --- Airtable 디자인 토큰 ---
INK = PRIMARY = "#181d26"
PRIMARY_ACTIVE = "#0d1218"
CANVAS = "#ffffff"
SURFACE_SOFT = "#f8fafc"
SURFACE_STRONG = "#e0e2e6"
SURFACE_DARK = "#181d26"
HAIRLINE = "#dddddd"
BODY = "#333840"
MUTED = "#41454d"
LINK = "#1b61c9"
SUCCESS = "#006400"
WARNING = "#d97706"
# 시그니처 surface
CORAL = "#aa2d00"
FOREST = "#0a2e0e"
CREAM = "#f5e9d4"
PEACH = "#fcab79"
MINT = "#a8d8c4"
YELLOW = "#f4d35e"
MUSTARD = "#d9a441"

# 단계별 시그니처 surface (voltage 모먼트)
STAGE_SURFACE = {
    "계획수립": SURFACE_DARK, "EDA": FOREST, "베이스라인": CORAL,
    "피처엔지니어링": FOREST, "튜닝": CORAL, "리포트": SURFACE_DARK,
}

# 결과 신뢰성 경계 문구(기획서 정책)
DISCLAIMER = (
    "⚠️ 제한된 데이터·환경에서 도출된 결과이므로, "
    "프로덕션 적용 전 반드시 검토가 필요합니다."
)

# 3단계 라벨
STEPS = ["1 입력", "2 분석", "3 결과"]

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Inter+Tight:wght@400;500&display=swap');
html, body, [class*="css"] { font-family: 'Inter', system-ui, sans-serif; color: #333840; }
h1, h2, h3 { font-family: 'Inter Tight', 'Inter', system-ui, sans-serif; color: #181d26; font-weight: 500; letter-spacing: 0; }
h1 { font-weight: 400; }
div.stButton > button[kind="primary"] {
  background: #181d26; color: #ffffff; border: none; border-radius: 12px;
  padding: 16px 24px; font-weight: 500;
}
div.stButton > button[kind="primary"]:active { background: #0d1218; }
div.stButton > button[kind="secondary"] {
  background: #ffffff; color: #181d26; border: 1px solid #dddddd; border-radius: 12px;
  padding: 16px 24px; font-weight: 500;
}
.hl-banner { border-radius: 12px; padding: 16px 20px; color: #ffffff;
  font-weight: 500; margin-bottom: 16px; }
.hl-console { background: #f8fafc; border: 1px solid #dddddd; border-radius: 10px;
  padding: 16px; max-height: 520px; overflow-y: auto; }
.hl-item { display: flex; gap: 8px; padding: 6px 0; font-size: 14px; color: #333840;
  border-bottom: 1px solid #eef1f4; }
.hl-item .ic { flex: 0 0 20px; }
.hl-code { background: #181d26; color: #e6e8eb; border-radius: 8px; padding: 12px;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 12.5px;
  white-space: pre-wrap; margin: 4px 0; }
.hl-metric-card { background: #f5e9d4; border-radius: 10px; padding: 16px; }
</style>
"""


def inject_css() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)


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
    """페이지 공통 설정 + 디자인 CSS 주입. 앱 진입점에서 1회 호출."""
    st.set_page_config(
        page_title="ML 자동화 에이전트",
        page_icon="🤖",
        layout="wide",
    )
    inject_css()


def stage_banner_html(stage: str, loop: int, total_loops: int) -> str:
    """현재 단계를 시그니처 surface 배너로."""
    bg = STAGE_SURFACE.get(stage, SURFACE_DARK)
    label = _html.escape(f"▶ 현재: {stage}  ·  루프 {loop}/{total_loops}")
    return f'<div class="hl-banner" style="background:{bg}">{label}</div>'


def console_html(items) -> str:
    """콘솔 피드(ConsoleItem 리스트)를 스타일된 HTML로."""
    icons = {"llm": "🧠", "code": "💻", "log": "•"}
    rows = []
    for it in items:
        if it.kind == "code":
            rows.append(
                f'<div class="hl-item"><span class="ic">{icons["code"]}</span>'
                f'<div class="hl-code">{_html.escape(it.text)}</div></div>'
            )
        else:
            ic = icons.get(it.kind, "•")
            rows.append(
                f'<div class="hl-item"><span class="ic">{ic}</span>'
                f'<span>{_html.escape(it.text)}</span></div>'
            )
    return '<div class="hl-console">' + "".join(rows) + "</div>"
