import os
from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.tools import tool
from langchain_upstage import ChatUpstage
from dotenv import load_dotenv

# .env 파일에서 환경변수 로드
load_dotenv()

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "hypoloop_react_test"

# 1. 도구(Tools) 정의 (각각의 코드 작성 역할을 분리하여 에이전트가 선택하게 함)

@tool
def generate_eda_code(requirements: str) -> str:
    """EDA(탐색적 데이터 분석)를 수행하고 시각화하는 파이썬 코드를 생성합니다."""
    print(f">> [Tool] 'generate_eda_code' 실행됨 (요구사항: {requirements})")
    return "EDA 코드가 성공적으로 생성되었습니다. (Mock)"

@tool
def generate_feature_engineering_code(hypothesis: str) -> str:
    """가설을 검증하기 위해 새로운 파생 변수를 만들거나 결측치를 처리하는 피처 엔지니어링 파이썬 코드를 생성합니다."""
    print(f">> [Tool] 'generate_feature_engineering_code' 실행됨 (가설: {hypothesis})")
    return "피처 엔지니어링 코드가 성공적으로 생성되었습니다. (Mock)"

@tool
def generate_training_code(model_info: str) -> str:
    """전처리된 데이터를 바탕으로 머신러닝 모델을 학습(Train)시키는 파이썬 코드를 생성합니다."""
    print(f">> [Tool] 'generate_training_code' 실행됨 (모델 정보: {model_info})")
    return "모델 학습 코드가 성공적으로 생성되었습니다. (Mock)"

@tool
def generate_logging_code(tracking_info: str) -> str:
    """학습 결과(성능 지표)와 모델 파일을 MLflow 등에 기록(Logging)하는 파이썬 코드를 생성합니다."""
    print(f">> [Tool] 'generate_logging_code' 실행됨 (추적 정보: {tracking_info})")
    return "MLflow 로깅 코드가 성공적으로 생성되었습니다. (Mock)"

# 에이전트가 상황에 맞게 골라서 쓸 수 있는 도구 목록
tools = [
    generate_eda_code, 
    generate_feature_engineering_code, 
    generate_training_code, 
    generate_logging_code
]

# 2. 상태(State) 정의
# 대화 기록과 도구 호출 이력을 모두 누적하는 Messages 형태의 상태
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# 3. 에이전트 노드 정의 (중앙 집중형)
def agent_node(state: AgentState):
    print(">> [Node] Agent Thinking...")
    # LLM에 도구들을 바인딩하여 도구를 사용할 수 있는 능력을 부여
    llm = ChatUpstage().bind_tools(tools)
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

# 4. 그래프 생성 및 연결 (Agent <-> Tools 루프 구조)
workflow = StateGraph(AgentState)

# 노드 추가 (중앙 에이전트 노드 1개, 도구 실행 노드 1개)
workflow.add_node("agent", agent_node)
workflow.add_node("tools", ToolNode(tools))

# 시작점 -> 에이전트
workflow.add_edge(START, "agent")

# 에이전트 판단에 따른 조건부 라우팅 (Conditional Edge)
# 에이전트가 툴 호출을 결정하면 -> "tools" 노드로 이동
# 질문에 대한 답변을 완료했으면 -> END로 이동
workflow.add_conditional_edges(
    "agent",
    tools_condition,
)

# 툴 실행이 끝나면 무조건 다시 "agent"로 복귀하여 다음 행동을 판단 (순환 구조)
workflow.add_edge("tools", "agent")

# 앱 컴파일
app = workflow.compile()

if __name__ == "__main__":
    # 사용자 최초 입력
    user_input = "타이타닉 데이터를 이용해 생존율 예측 모델을 만들고, EDA 시각화와 최종 리포트까지 알아서 순서대로 작성해줘. 가설은 '성별과 객실 등급이 중요할 것이다'야."
    initial_state = {"messages": [HumanMessage(content=user_input)]}
    
    print("=== ReAct LangGraph 루프 테스트 시작 ===")
    for output in app.stream(initial_state):
        for key, value in output.items():
            print(f"Finished node: {key}")
    print("=== ReAct LangGraph 루프 테스트 종료 ===")
