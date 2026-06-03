"""UI ↔ 백엔드 합의 계약. 백엔드 팀은 PipelineBackend를 구현한다."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterator, List, Protocol, runtime_checkable

# 파이프라인 단계(진행 화면 체크리스트 순서)
PIPELINE_STAGES: List[str] = [
    "계획수립", "EDA", "베이스라인", "피처엔지니어링", "튜닝", "리포트",
]

# 태스크 종류
TASK_TYPES: List[str] = ["classification", "regression"]


@dataclass
class DataCard:
    target_column: str            # 예측 대상 컬럼
    task_type: str                # "classification" | "regression"
    description: str = ""         # 데이터셋 자유 설명


@dataclass
class PipelineInput:
    csv_path: str                 # 업로드된 CSV 저장 경로
    loop_count: int               # 성능 개선 루프 횟수
    data_card: DataCard
    llm_instruction: str          # 가설·목표·평가산식 자유 텍스트


@dataclass
class ProgressEvent:
    stage: str                    # PIPELINE_STAGES 중 하나
    loop_index: int               # 0 = 베이스라인
    status: str                   # "running" | "done" | "failed"
    message: str                  # 사용자에게 보일 한 줄 설명


@dataclass
class MetricRecord:
    loop_index: int
    metric_name: str              # 예: "accuracy", "rmse"
    baseline: float               # 베이스라인 값
    value: float                  # 해당 루프 값


@dataclass
class PipelineResult:
    report_md: str                # 최종 마크다운 보고서
    final_code: str               # 실행 가능한 Python 코드
    metrics_history: List[MetricRecord] = field(default_factory=list)
    experiment_yaml: str = ""     # 백엔드가 생성한 yml 내용


@runtime_checkable
class PipelineBackend(Protocol):
    """백엔드 구현이 따라야 할 인터페이스."""

    def validate_input(self, inp: PipelineInput) -> List[str]:
        """입력 검증. 문제 메시지 리스트 반환(빈 리스트면 통과)."""
        ...

    def run(self, inp: PipelineInput) -> Iterator[ProgressEvent]:
        """파이프라인 실행. 진행 이벤트를 순차 yield."""
        ...

    def get_result(self) -> PipelineResult:
        """run() 완료 후 최종 결과 반환."""
        ...
