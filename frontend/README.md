# ML 자동화 에이전트 — UI / 프론트

ML 파이프라인 자동화 에이전트의 **Streamlit 프론트엔드**입니다. 입력 폼과 보고서
뷰어를 제공하며, 백엔드는 `PipelineBackend` 인터페이스로 분리되어 있어 백엔드 팀과
병렬로 개발할 수 있습니다. 현재는 `MockBackend`로 전체 흐름이 동작합니다.

## 화면 구성

1. **입력 화면** — CSV 업로드(미리보기), 데이터 카드(타깃 컬럼·태스크 종류·설명),
   루프 횟수, 언어모델 입력(가설·목표·평가산식)
2. **진행 화면** — 단계별·루프별 진행 상태 실시간 표시
3. **보고서 화면** — 탭 4개: 리포트(MD+다운로드) / 성능지표(차트·표) / 코드 / 실험설정

## 실행

```bash
pip install -r requirements.txt
streamlit run app.py
```

브라우저에서 `http://localhost:8501` 접속. 샘플 데이터는 `sample_data/sample.csv`.

## 테스트

```bash
python -m pytest -v
```

## 프로젝트 구조

```
app.py                  # 진입점 + 세션 상태 라우팅(입력→진행→보고서)
ui/theme.py             # 스텝 헤더, 경계 문구, 색상 토큰
ui/input_form.py        # 입력 폼 + 검증·태스크 추정
ui/progress_view.py     # 진행 상태 실시간 표시
ui/report_viewer.py     # 보고서 뷰어(4탭)
backend/interface.py    # ★ UI↔백엔드 합의 계약(dataclass + Protocol)
backend/mock.py         # Mock 구현(통합 시 교체 대상)
sample_data/            # 샘플 CSV·리포트
tests/                  # 단위 테스트
```

## 백엔드 통합 가이드

UI는 `backend/interface.py`의 `PipelineBackend` 프로토콜에만 의존합니다.
백엔드 팀은 이 프로토콜을 구현한 클래스를 제공하고, `app.py`의 `get_backend()`에서
`MockBackend()`를 그 클래스로 교체하면 통합이 끝납니다.

구현해야 할 메서드:

| 메서드 | 반환 | 설명 |
| --- | --- | --- |
| `validate_input(inp)` | `list[str]` | 입력 검증 메시지(빈 리스트면 통과) |
| `run(inp)` | `Iterator[ProgressEvent]` | 진행 이벤트 스트리밍(yield) |
| `get_result()` | `PipelineResult` | 최종 결과(리포트·코드·지표·yml) |

주고받는 데이터 형식(`DataCard`, `PipelineInput`, `ProgressEvent`, `MetricRecord`,
`PipelineResult`)은 `backend/interface.py`의 dataclass 정의를 참고하세요. 계약을
변경할 때는 이 파일을 양 팀이 함께 리뷰합니다.
