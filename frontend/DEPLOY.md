# 배포 가이드

팀원들이 UI를 사용할 수 있도록 배포하는 방법입니다. 상황에 맞게 선택하세요.

## 현재 상태 (임시 공개 URL)

지금은 **cloudflared 임시 터널**로 배포되어 있습니다.

- 공개 URL은 이 PC에서 `cloudflared`가 실행되는 동안만 유효합니다.
- 이 PC를 끄거나 터널을 중지하면 접속이 끊깁니다.
- 재시작하면 URL이 바뀝니다.

수업 시연·짧은 공유에는 충분하지만, 상시 사용하려면 아래 **Streamlit Community
Cloud**(무료, 영구 URL)를 권장합니다.

### 임시 터널 다시 켜기 / 끄기

```bash
# 앱 실행 (백그라운드)
streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true &

# 공개 터널 (계정 불필요, 실행하면 https://*.trycloudflare.com URL 출력)
cloudflared tunnel --url http://localhost:8501

# 끄기
pkill -f "cloudflared tunnel"
pkill -f "streamlit run"
```

## 방법 A — 같은 네트워크(LAN)

팀원이 같은 Wi-Fi에 있다면, 앱 실행 중에 아래 주소로 바로 접속할 수 있습니다.

```
http://<이 PC의 LAN IP>:8501     # 예: http://192.168.1.123:8501
```

`--server.address 0.0.0.0`으로 실행해야 외부 접속이 됩니다.

## 방법 B — Streamlit Community Cloud (권장, 무료·영구)

GitHub 저장소만 있으면 무료로 상시 호스팅됩니다. 이 PC를 꺼도 유지됩니다.

1. **GitHub 인증 후 저장소 푸시** (현재 토큰이 만료되어 재로그인 필요)
   ```bash
   gh auth login            # 브라우저로 GitHub 로그인
   gh repo create ml-agent-ui --public --source=. --push
   # 또는 수동으로 remote 추가 후 git push
   ```
2. <https://share.streamlit.io> 접속 → GitHub 로그인
3. **New app** → 방금 만든 저장소 / 브랜치 / `app.py` 선택 → **Deploy**
4. 몇 분 후 `https://<앱이름>.streamlit.app` 형태의 영구 URL이 생성됩니다.

필요 파일(`requirements.txt`, `app.py`, `.streamlit/config.toml`)은 이미 준비되어
있습니다.

> 참고: GitHub에 올릴 때 회의에서 정한 대로 DB 경로/환경만 팀 기준에 맞춰 조정하세요.

## 방법 C — Docker (팀 공통 환경)

회의에서 정한 "환경세팅은 도커로 관리"에 맞춘 방법입니다. 누구든 동일 환경에서
실행할 수 있습니다.

```bash
# 이미지 빌드
docker build -t ml-agent-ui .

# 컨테이너 실행 → http://localhost:8501
docker run --rm -p 8501:8501 ml-agent-ui
```

서버/클라우드 VM에 이 컨테이너를 올리면 상시 호스팅도 가능합니다.
