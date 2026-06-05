# tool.py
from langchain_core.tools import tool

@tool
def list_directory(path: str) -> str:
    """프로젝트 폴더 트리 구조 및 파일 목록 확인 (ls, tree 역할)"""
    # TODO: 폴더 트리 구조 및 파일 목록을 문자열 형태로 반환하도록 구현
    pass

@tool
def search_code(pattern: str, path: str) -> str:
    """특정 변수나 함수가 사용된 위치 검색 (grep 역할)"""
    # TODO: 주어진 경로에서 패턴을 검색하고 일치하는 라인과 파일 정보를 반환하도록 구현
    pass

@tool
def read_file(file_path: str) -> str:
    """소스 코드 내용 확인"""
    # TODO: 파일 경로를 받아 소스 코드 내용을 문자열로 반환하도록 구현
    pass

@tool
def write_file(file_path: str, content: str) -> str:
    """에이전트가 생각한 ML 코드를 실제 파이썬 파일로 저장"""
    # TODO: 주어진 내용을 파일로 저장하고 성공 여부를 반환하도록 구현
    pass

@tool
def execute_command(command: str) -> str:
    """터미널에서 스크립트를 구동하고, 결과(Stdout) 및 에러(Stderr) 반환"""
    # TODO: subprocess 등을 이용해 명령어를 실행하고 결과를 반환하도록 구현
    pass

# Define your LangGraph tools here
tools = [
    list_directory,
    search_code,
    read_file,
    write_file,
    execute_command
]
