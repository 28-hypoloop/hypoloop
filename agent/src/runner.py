import argparse
import os

def main():
    parser = argparse.ArgumentParser(description="Agent Trigger Script")
    parser.add_argument("--trigger_id", type=str, required=True, help="트리거 고유 ID")
    parser.add_argument("--project_id", type=str, required=True, help="대상 프로젝트 ID")
    parser.add_argument("--hypothesis_id", type=str, required=True, help="대상 가설 ID")
    
    args = parser.parse_args()
    
    print(f"[*] Agent Started with Trigger ID: {args.trigger_id}")
    print(f"[*] Target Project ID: {args.project_id}")
    print(f"[*] Target Hypothesis ID: {args.hypothesis_id}")
    
    # 동적 경로 조합 (최상위 디렉토리 기준)
    # 현재 파일은 agent/src/runner.py 이므로, 최상위 경로는 ../../ 입니다.
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    hypothesis_dir = os.path.join(base_dir, "data", "projects", args.project_id, "hypotheses", args.hypothesis_id)
    
    print(f"[*] Target Directory: {hypothesis_dir}")
    
    if not os.path.exists(hypothesis_dir):
        print(f"[!] Target directory does not exist: {hypothesis_dir}")
        return
        
    hypothesis_file = os.path.join(hypothesis_dir, f"u_id_{args.hypothesis_id}.yml")
    if os.path.exists(hypothesis_file):
        print(f"[*] Successfully located hypothesis file: {hypothesis_file}")
        # 추후 yaml 모듈 등을 이용해 실제 파싱 진행
    else:
        print(f"[!] Hypothesis file not found: {hypothesis_file}")

if __name__ == "__main__":
    main()
