"""대시보드 순수 로직: 이벤트 스트림을 콘솔/지표/단계 상태로 분류·누적."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Set

from backend.interface import ProgressEvent, MetricRecord

CONSOLE_KINDS = ("llm", "code", "log")
DEFAULT_MAX_CONSOLE = 30


@dataclass
class ConsoleItem:
    kind: str          # "llm" | "code" | "log"
    text: str
    loop_index: int


@dataclass
class DashboardState:
    """이벤트를 적용해 대시보드가 그릴 상태를 누적한다."""
    max_console: int = DEFAULT_MAX_CONSOLE
    console: List[ConsoleItem] = field(default_factory=list)
    metrics: List[MetricRecord] = field(default_factory=list)
    stages_done: Set[str] = field(default_factory=set)
    current_stage: str = ""
    current_loop: int = 0

    def apply(self, ev: ProgressEvent) -> None:
        self.current_stage = ev.stage
        self.current_loop = ev.loop_index
        if ev.kind == "stage":
            if ev.status == "done":
                self.stages_done.add(ev.stage)
        elif ev.kind in CONSOLE_KINDS:
            text = ev.detail if ev.detail else ev.message
            self.console.append(ConsoleItem(ev.kind, text, ev.loop_index))
            if len(self.console) > self.max_console:
                self.console = self.console[-self.max_console:]
        elif ev.kind == "metric" and ev.metric is not None:
            self.metrics.append(ev.metric)

    def latest_metric(self) -> Optional[MetricRecord]:
        return self.metrics[-1] if self.metrics else None

    def loop_progress(self, loop_count: int) -> float:
        """루프 진행 기준 진행률(단조 증가, 정체 없음).

        current_loop 0(베이스라인)부터 loop_count(리포트)까지 진행하며 1.0에 도달.
        단계명 집합 기반과 달리 같은 단계가 루프마다 반복돼도 진행바가 멈추지 않는다.
        """
        if loop_count <= 0:
            return 0.0
        return min((self.current_loop + 1) / (loop_count + 1), 1.0)
