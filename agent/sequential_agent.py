import os
from typing import TypedDict, Annotated
import operator
from langgraph.graph import StateGraph, START, END
from langchain_upstage import ChatUpstage
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

# .env 파일에서 환경변수 명시적 로드
load_dotenv()

# Ensure LANGCHAIN_TRACING_V2 is set for LangSmith
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "hypoloop_sequential_test"

# 1. 상태(State) 정의
class AgentState(TypedDict):
    messages: Annotated[list[str], operator.add]
    hypothesis: str
    training_code: str
    eda_code: str
    report_content: str

# 2. 노드(Node) 함수 정의 (툴을 사용하지 않고 목업 데이터로 흐름만 테스트)
def plan_node(state: AgentState):
    print(">> [Node 1] 계획 수립 및 가설 생성 (Mock)")
    titanic_hypothesis = (
        "Goal: 타이타닉 탑승객 생존 여부 예측\n"
        "Hypothesis: 기본 변수 외에 이름(Name)에서 사회적 지위(Title)를 추출하고, "
        "Age 결측치를 Title별 중앙값으로 채우며, SibSp와 Parch로 FamilySize 및 IsAlone 파생 변수를 "
        "만들어 조합하면 생존율 예측 성능이 크게 향상될 것이다."
    )
    return {"hypothesis": titanic_hypothesis}

def generate_training_node(state: AgentState):
    print(">> [Node 2] 학습 코드 생성 (실제 API 호출 테스트)")
    hypothesis = state.get("hypothesis", "")
    
    # 하드코딩된 목업 대신, 이전 노드의 가설(hypothesis)을 프롬프트에 넣어 실제 API가 코드를 잘 뱉는지 테스트
    try:
        llm = ChatUpstage()
        prompt = f"다음 가설을 검증하는 타이타닉 머신러닝 파이썬 코드를 작성해줘. 피처 엔지니어링과 MLflow 추적 로직을 포함해야 해.\n\n가설: {hypothesis}"
        
        response = llm.invoke([HumanMessage(content=prompt)])
        generated_code = response.content
    except Exception as e:
        generated_code = f"# API 호출 에러 (UPSTAGE_API_KEY 환경변수 설정 필요):\n# {e}"
        
    return {"training_code": generated_code}

def execute_training_node(state: AgentState):
    print(">> [Node 3] 학습 코드 실행 (Mock)")
    # 실제 실행하지 않고 성공했다고 가정
    return {"messages": ["Training executed successfully."]}

def generate_eda_node(state: AgentState):
    print(">> [Node 4] 시각화 코드 생성 (Mock)")
    mock_eda_code = (
        "import matplotlib.pyplot as plt\n"
        "import seaborn as sns\n"
        "# Generate feature importance plot\n"
        "print('Feature Importances: Sex: 0.35, Title_Mr: 0.20, Pclass: 0.15, Age: 0.10, FamilySize: 0.10, IsAlone: 0.05, Fare: 0.05')\n"
        "plt.savefig('feature_importance.png')\n"
        "# Save new engineered features to Feast\n"
        "print('Registered Title, FamilySize, IsAlone to Feast Feature Store')\n"
    )
    return {"eda_code": mock_eda_code}

def execute_eda_node(state: AgentState):
    print(">> [Node 5] 시각화 및 피처스토어 등록 실행 (Mock)")
    return {"messages": ["EDA executed successfully."]}

def write_report_node(state: AgentState):
    print(">> [Node 6] 마크다운 리포트 작성 (Mock)")
    mock_report = (
        "# 타이타닉 생존자 예측 심층 실험 리포트\n\n"
        "## 실험 결과\n"
        "- **가설**: 이름(Name)에서 추출한 Title(사회적 지위)과 정교한 결측치 처리, FamilySize 파생 변수가 예측력을 극대화할 것이다.\n"
        "- **모델 성능**: Accuracy 0.845 (성능 향상됨!)\n\n"
        "## 피처 엔지니어링 효율성 분석\n"
        "- **Sex & Title_Mr (매우 효율적)**: 성별과 'Mr' 타이틀이 가장 높은 중요도(0.35, 0.20)를 기록. 생존을 가르는 핵심 피처임.\n"
        "- **Pclass & Age (효율적)**: 객실 등급(0.15)과 Title별 중앙값으로 결측치를 보간한 Age(0.10)가 유의미하게 작동함.\n"
        "- **FamilySize & IsAlone (보통)**: 파생 변수들의 중요도 합이 0.15를 차지하며 예측력을 안정화함. Feast 스토어에 공식 등록 완료.\n"
    )
    return {"report_content": mock_report}

# 3. 그래프(Graph) 생성 및 직렬 연결
workflow = StateGraph(AgentState)

workflow.add_node("plan", plan_node)
workflow.add_node("generate_training", generate_training_node)
workflow.add_node("execute_training", execute_training_node)
workflow.add_node("generate_eda", generate_eda_node)
workflow.add_node("execute_eda", execute_eda_node)
workflow.add_node("write_report", write_report_node)

# 루프 없이 START 부터 END 까지 1회성(순차적) 진행
workflow.add_edge(START, "plan")
workflow.add_edge("plan", "generate_training")
workflow.add_edge("generate_training", "execute_training")
workflow.add_edge("execute_training", "generate_eda")
workflow.add_edge("generate_eda", "execute_eda")
workflow.add_edge("execute_eda", "write_report")
workflow.add_edge("write_report", END)

# 앱 컴파일
app = workflow.compile()

if __name__ == "__main__":
    # 목업 데이터로 테스트 실행
    initial_state = {
        "messages": ["Start sequential test"],
        "hypothesis": "",
        "training_code": "",
        "eda_code": "",
        "report_content": ""
    }
    
    print("=== 직렬 LangGraph 테스트 시작 ===")
    for output in app.stream(initial_state):
        # 각 노드가 실행될 때마다 상태 출력
        for key, value in output.items():
            print(f"Finished node: {key}")
    print("=== 직렬 LangGraph 테스트 종료 ===")
