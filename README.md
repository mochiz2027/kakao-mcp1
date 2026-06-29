# 🐾 Pet Voice On (펫보이스온) - MCP 서버

반려동물의 울음소리 주파수 및 행동 맥락을 분석하여 인간의 언어로 번역해 주는 **Model Context Protocol (MCP) 서버**입니다.  
오디오 분석, 시뮬레이션 기반 분석, 행동 맥락 융합, 1인칭 대사 변환, 건강 이상 징후 경고, 감정 라이프로그까지 **6가지 강력한 도구**를 탑재하고 있습니다.

---

## 🛠️ 기능 요약 (MCP Tools)

본 서버는 MCP 클라이언트가 직접 호출할 수 있는 **6가지 전문 도구**를 제공합니다.

| 번호 | 도구명 (Tool Name) | 설명 | 핵심 파라미터 |
| :--- | :--- | :--- | :--- |
| 1 | `analyze_pet_vocalization` | 🎵 오디오 파일(.wav/.mp3) 주파수·데시벨 분석으로 감정 도출 | `audio_path`, `pet_type` |
| 2 | `simulate_pet_voice_analysis` | 🎮 오디오 없이 울음소리 유형/강도로 시뮬레이션 분석 | `pet_type`, `vocalization_type`, `intensity` |
| 3 | `get_pet_context_booster` | 🐕 행동 맥락(꼬리 흔들기 등) 추가로 번역 정확도 향상 | `pet_type`, `behavior_description` |
| 4 | `translate_pet_emotion_to_speech` | 💬 감정 키워드 → 반려동물 1인칭 대사 변환 (4가지 스타일) | `pet_type`, `emotion`, `dialogue_style` |
| 5 | `get_pet_health_indicator` | 🏥 울음소리 패턴 기반 건강 이상 징후 조기 경고 | `pet_type`, `vocalization_pattern`, `frequency` |
| 6 | `get_pet_emotion_diary` | 📔 시간대별 감정 변화 추적 일지 및 그래프 생성 | `pet_type`, `entries` |

> 💡 **시뮬레이션 모드 지원**  
> 실제 오디오 파일이 없어도 `simulate_pet_voice_analysis` 도구를 통해  
> 울음소리 유형과 강도를 입력하는 것만으로 즉시 분석 체험이 가능합니다.

> 🎨 **4가지 대사 스타일**  
> `translate_pet_emotion_to_speech` 도구는 `cute`(귀여운), `dramatic`(극적인), `tsundere`(츤데레), `baby`(아기) 4가지 스타일을 지원합니다.

---

## ⚙️ 요구 사항 및 설치

1. **Python 3.10 이상**이 필요합니다.
2. 프로젝트 디렉토리로 이동하여 의존성 라이브러리를 설치합니다.

```bash
pip install -r requirements.txt
```

> 📌 `librosa` 라이브러리는 오디오 파일 분석에 사용됩니다. 시뮬레이션 모드만 사용할 경우 설치하지 않아도 됩니다.

---

## 🔑 환경 설정 (`.env`)

현재 버전은 외부 API 없이 독립 실행됩니다.  
향후 외부 AI 모델 API 연동 시 `.env.example`을 복사하여 `.env`로 생성하세요.

```bash
cp .env.example .env
```

---

## 🚀 서버 실행 방법

### 로컬 실행

```bash
python server.py
```

### GCP VM 서버 실행 (SSH 터미널)

```bash
# 1. 이전 프로세스 종료
sudo pkill -f server.py

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 백그라운드 실행
sudo ./venv/bin/python server.py > server.log 2>&1 &

# 4. 로그 확인
cat server.log
```

---

## 🔌 MCP 호스트 연동 가이드

### Claude Desktop 연동 설정

1. **Claude Desktop 설정 파일 열기**:
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. **설정 파일 편집** (`mcp_config.json` 내용을 복사):

```json
{
  "mcpServers": {
    "pet_voice_on_mcp": {
      "command": "C:/Users/ledpa/AppData/Local/Programs/Python/Python310/python.exe",
      "args": [
        "d:/AIwork/Anti-Graffiti/kakao-mcp1/server.py"
      ]
    }
  }
}
```

3. Claude Desktop 앱을 **완전히 종료 후 재시작**하면 도구가 등록됩니다.

### 카카오 PlayMCP 등록 정보

* **인증 방식:** `인증 사용하지 않음`
* **MCP Endpoint:** `http://[새 도메인]/mcp`
* **전송 방식:** Streamable HTTP (80번 포트)

---

## 🧪 로컬 도구 검증 (테스트 실행)

```bash
python test_client.py
```

7개의 테스트(6개 도구 + 보너스)가 실행되며, 모든 도구의 JSON 출력과 ASCII 비주얼 리포트가 정상 출력됩니다.

---

## 📋 도구 상세 사용법

### Tool 1: `analyze_pet_vocalization` (실제 오디오 분석)

```
audio_path: "/path/to/bark.wav"
pet_type: "dog"
```

### Tool 2: `simulate_pet_voice_analysis` (시뮬레이션 분석) ⭐ 추천

```
pet_type: "강아지"
vocalization_type: "bark"  # bark, whine, howl, growl, yelp, pant
intensity: "high"          # low, medium, high
duration_seconds: 2.0
```

고양이 울음소리 유형: `meow`, `purr`, `hiss`, `yowl`, `chirp`, `trill`

### Tool 3: `get_pet_context_booster` (행동 맥락 부스터)

```
pet_type: "고양이"
behavior_description: "꾹꾹이를 하며 이불 위에 웅크리고 있다"
time_of_day: "night"         # morning, afternoon, evening, night, dawn
environment: "indoor"        # indoor, outdoor, car, vet_clinic, new_place
```

### Tool 4: `translate_pet_emotion_to_speech` (감정→대사 변환)

```
pet_type: "강아지"
emotion: "happy"              # happy, sad, angry, scared, hungry, sleepy, playful, lonely
dialogue_style: "tsundere"    # cute, dramatic, tsundere, baby
situation: "집사가 퇴근하고 돌아왔다"
```

### Tool 5: `get_pet_health_indicator` (건강 경고 시스템)

```
pet_type: "고양이"
vocalization_pattern: "화장실 근처에서 자주 날카롭게 운다"
frequency: "frequent"         # rare, occasional, frequent, constant
additional_symptoms: "소변량 감소, 식욕 저하"
```

### Tool 6: `get_pet_emotion_diary` (감정 변화 일지)

```
pet_type: "강아지"
entries: [
    {"time": "08:00", "emotion": "happy", "note": "아침 산책 후"},
    {"time": "12:00", "emotion": "hungry", "note": "밥 시간"},
    {"time": "18:00", "emotion": "playful", "note": "공놀이"}
]
```
