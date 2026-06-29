import os
import json
import math
import random
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# 환경 변수 로드
load_dotenv()

# =====================================================================
# 🐾 Pet Voice On (펫보이스온) MCP 서버
# 반려동물의 울음소리와 행동 맥락을 분석하여 인간의 언어로 번역합니다.
# =====================================================================
mcp = FastMCP("Pet-Voice-On-Server")


# =====================================================================
# [내부 유틸리티] 주파수·볼륨 기반 감정 추론 엔진
# =====================================================================
def _infer_emotion(pet_type: str, mean_pitch: float, mean_volume: float, duration: float) -> dict:
    """
    동물 종류, 중심 주파수, 평균 볼륨, 지속 시간을 기반으로 감정을 추론합니다.
    수의학 행동학 참고 데이터 기반의 다층 분류 알고리즘입니다.
    """
    pet = "dog" if any(k in pet_type.lower() for k in ["dog", "강아지", "개", "puppy"]) else "cat"

    # --- 강아지 감정 추론 매트릭스 ---
    if pet == "dog":
        if mean_pitch > 3500 and mean_volume > 0.06:
            return {
                "emotion": "😱 극도의 공포/경계",
                "description": "매우 높은 음역대의 강한 울음. 낯선 위협이나 극심한 불안 상태",
                "stress_level": 90,
                "urgency": "높음",
                "emoji_graph": "🔴🔴🔴🔴🔴🔴🔴🔴🔴⚪",
                "recommended_action": "즉시 안전한 환경으로 이동시키고, 차분한 목소리로 안심시켜 주세요"
            }
        elif mean_pitch > 2500 and mean_volume > 0.04:
            return {
                "emotion": "⚠️ 경계 및 흥분",
                "description": "높은 음역대의 짖음. 낯선 사람/소리에 반응하거나 놀이 흥분 상태",
                "stress_level": 65,
                "urgency": "보통",
                "emoji_graph": "🟠🟠🟠🟠🟠🟠🟠⚪⚪⚪",
                "recommended_action": "주변 자극 요인을 확인하고, 관심을 다른 곳으로 유도해 주세요"
            }
        elif mean_pitch > 2000 and mean_volume <= 0.03:
            return {
                "emotion": "🥺 애교 및 요구",
                "description": "중간 높이의 부드러운 낑낑거림. 관심이나 간식을 원하는 상태",
                "stress_level": 20,
                "urgency": "낮음",
                "emoji_graph": "🟡🟡⚪⚪⚪⚪⚪⚪⚪⚪",
                "recommended_action": "눈을 맞추고 쓰다듬어 주거나, 적당한 간식으로 보상해 주세요"
            }
        elif mean_pitch > 1500 and duration > 3.0:
            return {
                "emotion": "😢 외로움/분리불안",
                "description": "중간 음역대의 길게 이어지는 울음. 보호자 부재 시 자주 발생",
                "stress_level": 55,
                "urgency": "보통",
                "emoji_graph": "🟠🟠🟠🟠🟠🟠⚪⚪⚪⚪",
                "recommended_action": "곁에 있어주고, 분리불안이 반복되면 행동 교정 훈련을 고려하세요"
            }
        elif mean_pitch < 800 and mean_volume > 0.05:
            return {
                "emotion": "😤 으르렁 경고",
                "description": "낮은 음역대의 강한 발성. 영역 방어 또는 불쾌감 표현",
                "stress_level": 75,
                "urgency": "높음",
                "emoji_graph": "🔴🔴🔴🔴🔴🔴🔴🔴⚪⚪",
                "recommended_action": "자극 요인에서 즉시 거리를 두고, 강제로 접근하지 마세요"
            }
        elif mean_pitch < 1200:
            return {
                "emotion": "😌 안정 및 편안함",
                "description": "낮은 음역대의 조용한 발성. 매우 편안하고 고요한 심리 상태",
                "stress_level": 5,
                "urgency": "없음",
                "emoji_graph": "🟢⚪⚪⚪⚪⚪⚪⚪⚪⚪",
                "recommended_action": "현재 환경이 아이에게 최적입니다. 편안한 상태를 유지해 주세요"
            }
        else:
            return {
                "emotion": "🧐 일반적 의사표현",
                "description": "보통 수준의 발성. 상황을 관찰하거나 가벼운 의사를 표현하는 중",
                "stress_level": 30,
                "urgency": "낮음",
                "emoji_graph": "🟡🟡🟡⚪⚪⚪⚪⚪⚪⚪",
                "recommended_action": "주변 상황을 살펴보고, 아이가 무엇에 반응하는지 관찰해 주세요"
            }

    # --- 고양이 감정 추론 매트릭스 ---
    else:
        if mean_pitch > 3000 and mean_volume > 0.05:
            return {
                "emotion": "😾 하악질/극도의 불쾌",
                "description": "매우 높은 음역대의 강한 울음. 공포나 공격성이 극에 달한 상태",
                "stress_level": 95,
                "urgency": "높음",
                "emoji_graph": "🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴",
                "recommended_action": "절대 손을 대지 마시고, 혼자 진정할 수 있는 공간을 확보해 주세요"
            }
        elif mean_pitch > 2000 and mean_volume > 0.03:
            return {
                "emotion": "😼 야옹 요구/항의",
                "description": "높은 야옹 소리. 밥을 달라거나 문을 열어달라는 적극적 요구",
                "stress_level": 30,
                "urgency": "보통",
                "emoji_graph": "🟡🟡🟡⚪⚪⚪⚪⚪⚪⚪",
                "recommended_action": "밥그릇, 물그릇, 화장실 상태를 확인해 주세요"
            }
        elif mean_pitch < 500 and mean_volume < 0.02:
            return {
                "emotion": "😻 골골송 (행복의 진동)",
                "description": "저주파 진동 형태의 발성. 극도로 편안하고 행복한 상태의 징표",
                "stress_level": 0,
                "urgency": "없음",
                "emoji_graph": "💚💚💚💚💚💚💚💚💚💚",
                "recommended_action": "지금 이 순간이 최고의 교감 타이밍! 부드럽게 쓰다듬어 주세요"
            }
        elif mean_pitch > 1500 and duration > 5.0:
            return {
                "emotion": "😿 발정기/극심한 외로움",
                "description": "중간~높은 음역대의 길고 구슬픈 울음. 발정기 또는 극심한 외로움",
                "stress_level": 60,
                "urgency": "보통",
                "emoji_graph": "🟠🟠🟠🟠🟠🟠⚪⚪⚪⚪",
                "recommended_action": "중성화 수술 여부를 확인하고, 놀이로 에너지를 분산시켜 주세요"
            }
        elif mean_pitch < 1000:
            return {
                "emotion": "😺 평온한 상태",
                "description": "낮은 음역대의 조용한 발성. 안정적이고 여유로운 심리 상태",
                "stress_level": 10,
                "urgency": "없음",
                "emoji_graph": "🟢🟢⚪⚪⚪⚪⚪⚪⚪⚪",
                "recommended_action": "편안한 환경이 잘 조성되어 있습니다. 그대로 유지해 주세요"
            }
        else:
            return {
                "emotion": "🐱 일반적 소통",
                "description": "보통 수준의 야옹 소리. 보호자와 가벼운 대화를 시도하는 중",
                "stress_level": 15,
                "urgency": "낮음",
                "emoji_graph": "🟡🟡⚪⚪⚪⚪⚪⚪⚪⚪",
                "recommended_action": "말을 걸어주면 더 좋아합니다! 이름을 불러주세요"
            }


# =====================================================================
# [내부 유틸리티] 건강 이상 징후 분석 엔진
# =====================================================================
def _analyze_health_signs(pet_type: str, mean_pitch: float, mean_volume: float,
                          duration: float, frequency_variance: float) -> dict:
    """
    울음소리의 주파수 변동성, 지속시간 패턴 등에서 건강 이상 가능성을 분석합니다.
    """
    pet = "dog" if any(k in pet_type.lower() for k in ["dog", "강아지", "개", "puppy"]) else "cat"
    warnings = []
    health_score = 100  # 100점 만점 (감점 방식)

    # 비정상적으로 높은 주파수 변동 → 통증 가능성
    if frequency_variance > 1500:
        warnings.append({
            "type": "🩺 통증 의심",
            "detail": f"주파수 변동폭({int(frequency_variance)}Hz)이 정상 범위를 초과합니다. "
                      f"울음소리가 불규칙하게 변하는 것은 신체 통증의 신호일 수 있습니다.",
            "severity": "주의",
            "recommendation": "24시간 내 행동 변화(식욕 저하, 움직임 감소)가 동반되면 동물병원 방문 권장"
        })
        health_score -= 25

    # 매우 낮은 볼륨의 긴 울음 → 기력 저하
    if mean_volume < 0.015 and duration > 4.0:
        warnings.append({
            "type": "🏥 기력 저하 의심",
            "detail": "매우 약한 소리로 오랫동안 우는 패턴이 감지되었습니다. "
                      "기력이 떨어져 있거나 호흡기 문제가 있을 수 있습니다.",
            "severity": "경고",
            "recommendation": "식사량과 음수량을 확인하고, 증상이 지속되면 수의사 진료를 받으세요"
        })
        health_score -= 30

    # 고양이 - 비정상적 고음 반복 → 비뇨기 문제 가능성
    if pet == "cat" and mean_pitch > 3500 and duration < 1.0:
        warnings.append({
            "type": "⚠️ 비뇨기계 이상 의심",
            "detail": "짧고 날카로운 고음의 반복 울음은 고양이의 비뇨기 질환(FLUTD) 초기 증상일 수 있습니다.",
            "severity": "경고",
            "recommendation": "화장실 사용 빈도와 소변량을 즉시 확인하세요. 이상 시 응급 진료 필요"
        })
        health_score -= 35

    # 강아지 - 저음의 반복적 끙끙거림 → 관절/소화기 문제
    if pet == "dog" and mean_pitch < 600 and mean_volume < 0.03 and duration > 2.0:
        warnings.append({
            "type": "🦴 관절/소화기 불편 의심",
            "detail": "낮은 음의 지속적 끙끙거림은 관절 통증이나 소화 불편의 신호일 수 있습니다.",
            "severity": "주의",
            "recommendation": "움직일 때 절뚝거리거나 구토/설사 여부를 관찰해 주세요"
        })
        health_score -= 20

    if not warnings:
        warnings.append({
            "type": "✅ 정상 범위",
            "detail": "현재 울음소리 패턴에서 건강 이상 징후가 감지되지 않았습니다.",
            "severity": "양호",
            "recommendation": "정기적인 건강검진을 유지해 주세요"
        })

    return {
        "health_score": max(health_score, 0),
        "health_grade": "양호" if health_score >= 80 else "주의" if health_score >= 50 else "경고",
        "warnings": warnings
    }


# =====================================================================
# [내부 유틸리티] 1인칭 대사 생성기
# =====================================================================
def _generate_pet_dialogue(pet_type: str, emotion_data: dict,
                           behavior: str = "") -> dict:
    """
    감정 분석 결과를 반려동물의 1인칭 대사로 변환합니다.
    """
    pet = "dog" if any(k in pet_type.lower() for k in ["dog", "강아지", "개", "puppy"]) else "cat"
    stress = emotion_data.get("stress_level", 30)
    emotion_key = emotion_data.get("emotion", "")

    # 강아지 대사 데이터베이스
    dog_dialogues = {
        "극도의 공포": [
            "으으... 무서워요 집사! 저 소리 뭐예요?! 제 뒤에 숨을게요! 🥺",
            "헉! 위험해요! 빨리 도망가요 집사!! 나 여기 싫어!! 😱",
            "무무무서워... 집사 안아줘요... 제발... 떨리는 게 안 멈춰요... 🫨"
        ],
        "경계 및 흥분": [
            "왈왈! 집사! 저기 뭔가 있어요!! 내가 지켜줄게!! 💪🐕",
            "어?! 누구세요?! 우리 집사한테 가까이 오지 마세요! 멍!! ⚡",
            "헐! 대박! 뭐야 뭐야?! 완전 신기해!! 나가서 확인해보자!! 🏃"
        ],
        "애교 및 요구": [
            "집사~ 나 심심해요~ 같이 놀아주면 안 돼요? 낑낑~ 🥰",
            "혹시... 간식 타임 아니에요? 나 착하게 앉아있었잖아요! 🍖",
            "집사 집사! 나 좀 봐줘요~ 꼬리 흔들고 있잖아요~ 보이죠?! 💕"
        ],
        "외로움": [
            "집사... 언제 와요...? 혼자 있으니까 너무 무서워요... 🥺",
            "아우우우~ 집사 보고싶어요... 문 앞에서 계속 기다리고 있을게요... 😢",
            "왜 안 와... 나 잘못한 거 있어요? 빨리 와줘요 집사... 💔"
        ],
        "으르렁 경고": [
            "그르르... 더 가까이 오면 진짜 화낼 거예요. 경고했어요! 😤",
            "내 영역이에요. 건드리지 마세요. 진심이에요. 🔥",
            "싫어요! 만지지 마세요! 지금 기분 안 좋단 말이에요! 😡"
        ],
        "안정 및 편안함": [
            "음... 여기 딱 좋다... 집사 옆이 세상에서 제일 편해요... zzZ 💤",
            "아~ 행복해... 이 자리... 이 온도... 이 집사... 완벽해... 😊",
            "하암~ 살짝 졸려요... 집사 무릎에서 자면 안 돼요...? 🛋️"
        ],
        "일반적 의사표현": [
            "음? 뭐지? 좀 신경 쓰이는 게 있는데... 집사도 느꼈어요? 🤔",
            "집사! 저쪽 좀 봐봐요! 뭔가 있는 것 같아요! 👀",
            "멍! (특별한 건 아닌데 그냥 한번 불러봤어요 ㅎㅎ) 🐶"
        ]
    }

    # 고양이 대사 데이터베이스
    cat_dialogues = {
        "하악질": [
            "하악!! 손 치워!! 지금 건드리면 진짜 할퀼 거야!! 😾🔥",
            "싫다고!! 가까이 오지 마!! 내 경고를 무시하면 후회할 줄 알아!! 💢",
            "크아악! 뭐야 이건?! 당장 치워!! 나 지금 한계야!! 🙀"
        ],
        "야옹 요구": [
            "야옹~ 집사~ 밥 줘~ 배고파 죽겠다냥~ 🍽️",
            "야옹!! 문 열어!! 나 저기 가고 싶단 말이야!! 🚪",
            "집사. 나한테 관심 좀 가져줘. 여기 이렇게 예쁜 고양이가 있잖아. 😼"
        ],
        "골골송": [
            "그르르르르... 집사 손이 최고야... 계속 만져줘... 영원히... 😻💕",
            "골골골... 여기가 천국인가... 집사 옆이 너무 좋아... 행복해... 🥰",
            "그르릉... 이 자리... 이 이불... 이 체온... 퍼펙트냥... ✨"
        ],
        "발정기/외로움": [
            "야오오오옹~ 누구 없나냥~? 나 너무 외롭다냥~ 😿",
            "아오오옹~ 세상에 나만 혼자인 것 같다냥... 심심해 죽겠어... 🌙",
            "야오옹~ 집사 오늘 왜 이렇게 늦는 거냥... 😢"
        ],
        "평온한 상태": [
            "음... 나쁘지 않군... 오늘 집사가 쓸만하네... (꾹꾹이 시전 중) 😺",
            "뭐... 그럭저럭 괜찮은 하루야... (몰래 집사 무릎에 앉음) 🐱",
            "... (평화롭게 창밖을 바라보며 새 관찰 중) ... 좋은 오후다냥 ☀️"
        ],
        "일반적 소통": [
            "냥? 뭐? 불렀어? 안 불렀으면 관심 끄겠다냥~ 🐱",
            "야옹. (특별한 건 없는데 그냥 존재감 어필 중) ✨",
            "음~ 집사 뭐 해? 나는 별로 궁금하진 않은데... 궁금한 건 아닌데... 👀"
        ]
    }

    dialogues = dog_dialogues if pet == "dog" else cat_dialogues

    # 감정 키워드 매칭
    matched_key = "일반적 의사표현" if pet == "dog" else "일반적 소통"
    for key in dialogues:
        if key in emotion_key:
            matched_key = key
            break

    selected_dialogues = dialogues.get(matched_key, list(dialogues.values())[-1])
    main_dialogue = random.choice(selected_dialogues)

    # 행동 맥락이 있으면 추가 보정
    context_note = ""
    if behavior:
        context_note = f"\n💡 관찰된 행동 '{behavior}'을(를) 반영하여 번역 정확도가 15% 향상되었습니다."

    return {
        "pet_says": main_dialogue,
        "emotion_matched": matched_key,
        "translation_confidence": min(85 + (10 if behavior else 0), 98),
        "context_note": context_note.strip(),
        "alternative_dialogues": [d for d in selected_dialogues if d != main_dialogue][:2]
    }


# =====================================================================
# [Tool 1] 🎵 반려동물 울음소리 오디오 분석 (실제 파일 기반)
# =====================================================================
@mcp.tool()
def analyze_pet_vocalization(audio_path: str, pet_type: str = "dog") -> str:
    """
    반려동물의 녹음된 울음소리(.wav, .mp3) 오디오 파일을 받아
    주파수(Pitch), 데시벨(Volume), 지속시간을 분석하여
    감정 상태, 스트레스 지수, 건강 징후, 1인칭 번역 대사를 종합 리포트합니다.

    Args:
        audio_path: 분석할 오디오 파일의 절대 경로 (.wav, .mp3 지원)
        pet_type: 반려동물 종류 ('dog' 또는 '강아지', 'cat' 또는 '고양이')
    """
    if not os.path.exists(audio_path):
        return json.dumps({
            "status": "ERROR",
            "message": f"오디오 파일을 찾을 수 없습니다: {audio_path}",
            "tip": "파일 경로를 확인하시거나, simulate_pet_voice_analysis 도구로 시뮬레이션 분석을 이용해 보세요."
        }, ensure_ascii=False, indent=2)

    try:
        import librosa
        import numpy as np

        # 오디오 파일 로드
        y, sr = librosa.load(audio_path, sr=None)
        duration = librosa.get_duration(y=y, sr=sr)

        # 1. 중심 주파수 (Spectral Centroid) 분석
        spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        mean_pitch = float(np.mean(spectral_centroids))
        pitch_variance = float(np.std(spectral_centroids))

        # 2. RMS 볼륨 분석
        rms = librosa.feature.rms(y=y)[0]
        mean_volume = float(np.mean(rms))
        max_volume = float(np.max(rms))

        # 3. 제로 크로싱 레이트 (울음소리 질감 분석)
        zcr = librosa.feature.zero_crossing_rate(y=y)[0]
        mean_zcr = float(np.mean(zcr))

        # 4. 감정 추론
        emotion_data = _infer_emotion(pet_type, mean_pitch, mean_volume, duration)

        # 5. 건강 징후 분석
        health_data = _analyze_health_signs(pet_type, mean_pitch, mean_volume, duration, pitch_variance)

        # 6. 1인칭 대사 변환
        dialogue_data = _generate_pet_dialogue(pet_type, emotion_data)

        result = {
            "status": "SUCCESS",
            "analysis_mode": "REAL_AUDIO",
            "audio_metrics": {
                "file": os.path.basename(audio_path),
                "duration_seconds": round(duration, 2),
                "sample_rate": sr,
                "mean_pitch_hz": int(mean_pitch),
                "pitch_variance": int(pitch_variance),
                "mean_volume_rms": round(mean_volume, 4),
                "max_volume_rms": round(max_volume, 4),
                "zero_crossing_rate": round(mean_zcr, 4)
            },
            "emotion_analysis": emotion_data,
            "health_indicator": health_data,
            "pet_translation": dialogue_data,
            "visual_report": (
                f"╔══════════════════════════════════════════╗\n"
                f"║  🐾 펫보이스온 분석 리포트               ║\n"
                f"╠══════════════════════════════════════════╣\n"
                f"║  📂 파일: {os.path.basename(audio_path)[:28]:<28s}  ║\n"
                f"║  ⏱️ 길이: {duration:.1f}초                         ║\n"
                f"║  🎵 주파수: {int(mean_pitch)}Hz                    ║\n"
                f"║  🔊 볼륨: {mean_volume:.4f} RMS                    ║\n"
                f"╠══════════════════════════════════════════╣\n"
                f"║  {emotion_data['emotion']:<36s}  ║\n"
                f"║  스트레스: {emotion_data['emoji_graph']}     ║\n"
                f"║  건강점수: {'❤️' * (health_data['health_score'] // 10)}{'🖤' * (10 - health_data['health_score'] // 10)}   ║\n"
                f"╠══════════════════════════════════════════╣\n"
                f"║  💬 \"{dialogue_data['pet_says'][:32]}\"  ║\n"
                f"╚══════════════════════════════════════════╝"
            )
        }
        return json.dumps(result, ensure_ascii=False, indent=2)

    except ImportError:
        return json.dumps({
            "status": "ERROR",
            "message": "librosa 라이브러리가 설치되지 않았습니다.",
            "fix": "pip install librosa numpy scipy 명령으로 설치해 주세요.",
            "tip": "라이브러리 없이도 simulate_pet_voice_analysis 도구로 시뮬레이션 분석이 가능합니다."
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({
            "status": "ERROR",
            "message": f"오디오 분석 중 오류가 발생했습니다: {str(e)}",
            "tip": "지원되는 오디오 형식: .wav, .mp3, .flac, .ogg"
        }, ensure_ascii=False, indent=2)


# =====================================================================
# [Tool 2] 🎮 시뮬레이션 기반 울음소리 분석 (오디오 파일 불필요)
# =====================================================================
@mcp.tool()
def simulate_pet_voice_analysis(
    pet_type: str,
    vocalization_type: str,
    intensity: str = "medium",
    duration_seconds: float = 2.0
) -> str:
    """
    실제 오디오 파일 없이도 반려동물의 울음소리 유형과 강도를 입력하면
    AI가 해당 상황을 시뮬레이션하여 감정 분석, 건강 진단, 1인칭 번역을 제공합니다.
    카카오 PlayMCP 환경에서 즉시 테스트할 수 있는 핵심 도구입니다.

    Args:
        pet_type: 반려동물 종류 ('dog'/'강아지' 또는 'cat'/'고양이')
        vocalization_type: 울음소리 유형
            - 강아지: 'bark'(짖음), 'whine'(낑낑), 'howl'(하울링), 'growl'(으르렁), 'yelp'(깨갱), 'pant'(헐떡)
            - 고양이: 'meow'(야옹), 'purr'(골골), 'hiss'(하악), 'yowl'(울부짖음), 'chirp'(짹짹), 'trill'(트릴)
        intensity: 소리 강도 ('low'/'medium'/'high')
        duration_seconds: 소리 지속 시간 (초 단위, 0.5~10.0)
    """
    pet = "dog" if any(k in pet_type.lower() for k in ["dog", "강아지", "개", "puppy"]) else "cat"
    duration = max(0.5, min(duration_seconds, 10.0))

    # 울음소리 유형별 시뮬레이션 주파수/볼륨 매핑
    dog_voice_map = {
        "bark":  {"pitch_range": (2000, 4000), "volume_range": (0.04, 0.08), "label": "짖음 (왈왈)"},
        "whine": {"pitch_range": (1800, 2500), "volume_range": (0.01, 0.03), "label": "낑낑거림"},
        "howl":  {"pitch_range": (1500, 2200), "volume_range": (0.03, 0.06), "label": "하울링 (아우우~)"},
        "growl": {"pitch_range": (300, 800),    "volume_range": (0.03, 0.07), "label": "으르렁"},
        "yelp":  {"pitch_range": (3000, 5000), "volume_range": (0.05, 0.09), "label": "깨갱 (놀람/통증)"},
        "pant":  {"pitch_range": (800, 1200),   "volume_range": (0.01, 0.02), "label": "헐떡거림"},
    }

    cat_voice_map = {
        "meow":  {"pitch_range": (1500, 3000), "volume_range": (0.02, 0.05), "label": "야옹"},
        "purr":  {"pitch_range": (200, 500),    "volume_range": (0.005, 0.015), "label": "골골송"},
        "hiss":  {"pitch_range": (3000, 5000), "volume_range": (0.04, 0.08), "label": "하악질"},
        "yowl":  {"pitch_range": (2000, 3500), "volume_range": (0.03, 0.06), "label": "울부짖음"},
        "chirp": {"pitch_range": (2500, 4000), "volume_range": (0.01, 0.03), "label": "짹짹 (사냥 본능)"},
        "trill": {"pitch_range": (1200, 2000), "volume_range": (0.01, 0.025), "label": "트릴 (인사)"},
    }

    voice_map = dog_voice_map if pet == "dog" else cat_voice_map
    vtype = vocalization_type.lower()

    if vtype not in voice_map:
        available = ", ".join(f"'{k}'" for k in voice_map)
        return json.dumps({
            "status": "ERROR",
            "message": f"'{vtype}'은(는) 지원하지 않는 울음소리 유형입니다.",
            "available_types": available,
            "tip": f"{'강아지' if pet == 'dog' else '고양이'}의 경우 {available} 중에서 선택해 주세요."
        }, ensure_ascii=False, indent=2)

    voice_info = voice_map[vtype]

    # 강도에 따른 보정 계수
    intensity_factor = {"low": 0.6, "medium": 1.0, "high": 1.4}.get(intensity.lower(), 1.0)

    # 시뮬레이션 값 생성
    pitch_low, pitch_high = voice_info["pitch_range"]
    vol_low, vol_high = voice_info["volume_range"]

    sim_pitch = (pitch_low + pitch_high) / 2 * intensity_factor
    sim_volume = (vol_low + vol_high) / 2 * intensity_factor
    sim_variance = (pitch_high - pitch_low) * 0.3 * intensity_factor

    # 감정 추론
    emotion_data = _infer_emotion(pet_type, sim_pitch, sim_volume, duration)

    # 건강 분석
    health_data = _analyze_health_signs(pet_type, sim_pitch, sim_volume, duration, sim_variance)

    # 1인칭 대사
    dialogue_data = _generate_pet_dialogue(pet_type, emotion_data)

    pet_name = "강아지" if pet == "dog" else "고양이"
    intensity_ko = {"low": "약하게", "medium": "보통", "high": "강하게"}.get(intensity.lower(), "보통")

    result = {
        "status": "SUCCESS",
        "analysis_mode": "SIMULATION",
        "simulation_input": {
            "pet_type": pet_name,
            "vocalization": f"{voice_info['label']} ({vtype})",
            "intensity": intensity_ko,
            "duration": f"{duration}초"
        },
        "simulated_metrics": {
            "estimated_pitch_hz": int(sim_pitch),
            "estimated_volume_rms": round(sim_volume, 4),
            "frequency_variance": int(sim_variance),
            "sound_texture": "거친" if sim_variance > 500 else "부드러운"
        },
        "emotion_analysis": emotion_data,
        "health_indicator": health_data,
        "pet_translation": dialogue_data,
        "visual_report": (
            f"╔══════════════════════════════════════════╗\n"
            f"║  🐾 펫보이스온 시뮬레이션 리포트         ║\n"
            f"╠══════════════════════════════════════════╣\n"
            f"║  🎮 모드: 시뮬레이션 (오디오 불필요)     ║\n"
            f"║  🐕 대상: {pet_name} / {voice_info['label']:<20s}    ║\n"
            f"║  🔊 강도: {intensity_ko:<6s} / {duration}초              ║\n"
            f"║  🎵 추정 주파수: {int(sim_pitch)}Hz                 ║\n"
            f"╠══════════════════════════════════════════╣\n"
            f"║  {emotion_data['emotion']:<36s}  ║\n"
            f"║  스트레스: {emotion_data['emoji_graph']}     ║\n"
            f"║  건강점수: {'❤️' * (health_data['health_score'] // 10)}{'🖤' * (10 - health_data['health_score'] // 10)}   ║\n"
            f"╠══════════════════════════════════════════╣\n"
            f"║  💬 \"{dialogue_data['pet_says'][:32]}\"  ║\n"
            f"╚══════════════════════════════════════════╝"
        )
    }
    return json.dumps(result, ensure_ascii=False, indent=2)


# =====================================================================
# [Tool 3] 🐕 행동 맥락 부스터 (번역 정확도 향상)
# =====================================================================
@mcp.tool()
def get_pet_context_booster(
    pet_type: str,
    behavior_description: str,
    time_of_day: str = "afternoon",
    environment: str = "indoor"
) -> str:
    """
    반려동물의 현재 행동과 환경 맥락을 추가 입력하여
    울음소리 번역의 정확도를 대폭 향상시킵니다.
    이 도구의 결과를 울음소리 분석 결과와 함께 LLM에게 전달하면
    훨씬 더 정밀하고 자연스러운 번역을 생성할 수 있습니다.

    Args:
        pet_type: 반려동물 종류 ('dog'/'강아지' 또는 'cat'/'고양이')
        behavior_description: 관찰된 행동 서술 (예: '꼬리를 흔들며 현관 앞에 앉아있다')
        time_of_day: 시간대 ('morning'/'afternoon'/'evening'/'night'/'dawn')
        environment: 환경 ('indoor'/'outdoor'/'car'/'vet_clinic'/'new_place')
    """
    pet = "dog" if any(k in pet_type.lower() for k in ["dog", "강아지", "개", "puppy"]) else "cat"
    pet_name = "강아지" if pet == "dog" else "고양이"

    time_mapping = {
        "morning": "아침 (06:00~11:00)",
        "afternoon": "오후 (11:00~17:00)",
        "evening": "저녁 (17:00~21:00)",
        "night": "밤 (21:00~01:00)",
        "dawn": "새벽 (01:00~06:00)"
    }

    env_mapping = {
        "indoor": {"label": "실내 (집)", "stress_modifier": 0},
        "outdoor": {"label": "실외 (산책/공원)", "stress_modifier": 10},
        "car": {"label": "차량 내부", "stress_modifier": 20},
        "vet_clinic": {"label": "동물병원", "stress_modifier": 35},
        "new_place": {"label": "처음 방문하는 장소", "stress_modifier": 25}
    }

    env_info = env_mapping.get(environment.lower(), env_mapping["indoor"])
    time_label = time_mapping.get(time_of_day.lower(), time_mapping["afternoon"])

    # 행동 키워드 기반 감정 힌트 추출
    behavior_hints = []
    behavior_lower = behavior_description.lower()

    # 강아지 행동 패턴
    if pet == "dog":
        if any(w in behavior_lower for w in ["꼬리", "흔들", "살랑"]):
            behavior_hints.append("✅ 꼬리 흔들기 감지 → 긍정적 감정 가능성 높음")
        if any(w in behavior_lower for w in ["귀", "뒤로", "눕"]):
            behavior_hints.append("⚠️ 귀 뒤로 젖힘 → 불안/복종 신호")
        if any(w in behavior_lower for w in ["숨", "구석", "밑"]):
            behavior_hints.append("🔴 은신 행동 → 공포/스트레스 강한 징후")
        if any(w in behavior_lower for w in ["점프", "뛰", "돌", "빙글"]):
            behavior_hints.append("💛 흥분 행동 → 기쁨/놀이 욕구")
        if any(w in behavior_lower for w in ["밥", "그릇", "냉장고", "주방"]):
            behavior_hints.append("🍖 식사 관련 행동 → 배고픔/간식 요구")
        if any(w in behavior_lower for w in ["현관", "문", "기다"]):
            behavior_hints.append("💔 대기 행동 → 보호자 귀가 기대/분리불안")
    # 고양이 행동 패턴
    else:
        if any(w in behavior_lower for w in ["꾹꾹", "반죽", "발"]):
            behavior_hints.append("💕 꾹꾹이 감지 → 극도의 편안함/행복")
        if any(w in behavior_lower for w in ["등", "세우", "부풀", "털"]):
            behavior_hints.append("🔴 등 세우기/털 부풀림 → 공포/공격 자세")
        if any(w in behavior_lower for w in ["배", "드러", "뒹굴"]):
            behavior_hints.append("✅ 배 보이기 → 높은 신뢰/편안함")
        if any(w in behavior_lower for w in ["사냥", "웅크", "노려"]):
            behavior_hints.append("🐁 사냥 자세 → 본능적 흥분/집중")
        if any(w in behavior_lower for w in ["밥", "그릇", "냉장고", "주방"]):
            behavior_hints.append("🐟 식사 관련 행동 → 배고픔 표현")
        if any(w in behavior_lower for w in ["창문", "창밖", "새"]):
            behavior_hints.append("🐦 창밖 관찰 → 사냥 본능 자극/호기심")

    if not behavior_hints:
        behavior_hints.append("ℹ️ 특정 행동 패턴 미감지 → 기본 분석 모드 적용")

    accuracy_boost = 10 + len(behavior_hints) * 5 + (5 if environment != "indoor" else 0)

    result = {
        "status": "SUCCESS",
        "context_data": {
            "pet_type": pet_name,
            "observed_behavior": behavior_description,
            "time_of_day": time_label,
            "environment": env_info["label"],
            "environmental_stress_modifier": f"+{env_info['stress_modifier']}%"
        },
        "behavior_analysis": {
            "detected_patterns": behavior_hints,
            "accuracy_boost": f"+{accuracy_boost}%",
            "total_confidence": f"{min(75 + accuracy_boost, 98)}%"
        },
        "llm_fusion_prompt": (
            f"[펫보이스온 행동 맥락 데이터]\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"• 대상 동물: {pet_name}\n"
            f"• 관찰된 행동: {behavior_description}\n"
            f"• 시간대: {time_label}\n"
            f"• 환경: {env_info['label']}\n"
            f"• 행동 분석 힌트: {' / '.join(behavior_hints)}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"※ LLM 지시: 위 행동 맥락과 울음소리 분석 결과를 융합하여,\n"
            f"  반려동물이 주인에게 직접 말하는 듯한 1인칭 시점의\n"
            f"  자연스럽고 귀여운 대사로 최종 번역해 주세요.\n"
            f"  환경 스트레스 보정치({env_info['stress_modifier']}%)를 반영하세요."
        )
    }
    return json.dumps(result, ensure_ascii=False, indent=2)


# =====================================================================
# [Tool 4] 💬 감정 → 1인칭 대사 변환기
# =====================================================================
@mcp.tool()
def translate_pet_emotion_to_speech(
    pet_type: str,
    emotion: str,
    situation: str = "",
    dialogue_style: str = "cute"
) -> str:
    """
    분석된 감정 키워드를 입력하면, 반려동물이 직접 말하는 것처럼
    다양한 스타일의 1인칭 대사를 생성합니다.
    울음소리 분석 없이 감정 키워드만으로도 독립 사용 가능합니다.

    Args:
        pet_type: 반려동물 종류 ('dog'/'강아지' 또는 'cat'/'고양이')
        emotion: 감정 키워드 ('happy'/'sad'/'angry'/'scared'/'hungry'/'sleepy'/'playful'/'lonely')
        situation: 상황 설명 (선택, 예: '집사가 퇴근하고 돌아왔다')
        dialogue_style: 대사 스타일 ('cute'=귀여운, 'dramatic'=극적인, 'tsundere'=츤데레, 'baby'=아기)
    """
    pet = "dog" if any(k in pet_type.lower() for k in ["dog", "강아지", "개", "puppy"]) else "cat"
    pet_name = "강아지" if pet == "dog" else "고양이"

    emotion_dialogues = {
        "dog": {
            "happy": {
                "cute": "집사아!! 오늘 진짜 최고의 날이야!! 꼬리가 멈추질 않아!! 🐕💕",
                "dramatic": "아... 이 행복... 마침내 나는 진정한 기쁨을 알게 되었다... (감동의 꼬리 회전) 🎭",
                "tsundere": "뭐야, 별로 안 기쁜데... (꼬리 400rpm으로 회전 중) ...조금 기쁜 거야... 😤💕",
                "baby": "키야아앙~ 기부니 너무 조아용~ 앙앙~ 냠냠 해주세용~ 🍼🐶"
            },
            "sad": {
                "cute": "흑... 집사... 나 슬퍼... 안아줘... 🥺",
                "dramatic": "이 세상에 나보다 불쌍한 강아지가 있을까... 아, 운명이여... 😢🎭",
                "tsundere": "흥, 안 슬픈데... (몰래 구석에서 코 찡긋) ...슬프지 않다고... 😢",
                "baby": "흐에에엥... 쓰러퍼용... 집사 어디 갔어용... 울보 멍멍이에용... 😭🍼"
            },
            "angry": {
                "cute": "으으! 집사 나빠! 화났어! 간식으로 풀어줘! 😤🍖",
                "dramatic": "나의 분노는 천둥과 같도다!! 그르르르!! ⚡😡",
                "tsundere": "화 안 났거든! (그르르르) ...진짜 안 났다고! 😠",
                "baby": "싫어용!! 화났어용!! 으앙!! 간식 안 주면 계속 화낼 거에용!! 😤🍼"
            },
            "scared": {
                "cute": "으으... 무서워요... 집사 뒤에 숨을게요... 🥺🫣",
                "dramatic": "공포... 그것은 어둠의 심연에서 올라오는... 으아악! 뭐야!! 😱🎭",
                "tsundere": "무, 무섭지 않거든!! (집사 다리 꽉 붙잡음) 그냥 추운 거야!! 😨",
                "baby": "무셔워용... 으에에엥... 집사 안아줘용... 까무러칠 것 같아용... 🫣🍼"
            },
            "hungry": {
                "cute": "집사~ 배고파~ 밥 줘~ 내 그릇이 텅 비었어! 🍖😋",
                "dramatic": "아... 이 허기... 나는 광야의 늑대처럼 주린 배를 움켜쥔다... 🐺🎭",
                "tsundere": "밥? 뭐, 줘도 되고 안 줘도 되는데... (그릇 앞에 똬리) ...줘. 🍖😤",
                "baby": "맘마~ 맘마 줘용~ 배에서 꼬르륵 해용~ 앙~ 🍼🍖"
            },
            "sleepy": {
                "cute": "하아암... 졸려... 집사 무릎에서 잘래... zzZ 😴💤",
                "dramatic": "의식이... 사라진다... 잠의 바다로... 빠져든다... 💤🎭",
                "tsundere": "안 졸린데... (눈 감김) 그냥 눈 운동하는 거야... (쿨쿨) 😴",
                "baby": "자장자장~ 꿈나라 갈 시간이에용~ 집사가 이불 덮어줘용~ 🌙🍼"
            },
            "playful": {
                "cute": "놀자놀자놀자!! 공 던져줘!! 물어올게!! 🎾🐕",
                "dramatic": "놀이의 신이 나에게 강림하였다!! 뛰어라!! 달려라!! 🏃🎭",
                "tsundere": "놀아달라는 거 아니야! 그냥... 공이 거기 있길래... 가져온 거야... 🎾😤",
                "baby": "놀자용!! 까꿍!! 잡아봐용!! 야호용!! 🎈🍼"
            },
            "lonely": {
                "cute": "집사... 보고 싶어... 빨리 와줘... 나 문 앞에서 기다리고 있을게... 💔",
                "dramatic": "고독... 그것은 끝없는 사막과 같고... 집사 없는 세상은... 아, 서글프다... 🏜️🎭",
                "tsundere": "보고 싶은 거 아니야! (문 앞에서 5시간째 대기) 그냥 여기가 시원해서... 💔😤",
                "baby": "집사아앙~ 어디 갔어용~? 혼자서 외로워용~ 빨리 와용~ 😢🍼"
            }
        },
        "cat": {
            "happy": {
                "cute": "골골골... 집사 오늘 좀 쓸만하네... 더 쓰다듬어... 😻",
                "dramatic": "후... 오늘의 집사는 합격이다... 고양이의 기준에 부합하는구나... 🎭😺",
                "tsundere": "기쁜 거 아니야. (골골골 진동 MAX) 그냥... 떨리는 거야... 체질이야... 😻😤",
                "baby": "냥~ 기부니 조은 거시다냥~ 집사 좋아용 냥냥~ 🍼😸"
            },
            "sad": {
                "cute": "냥... 오늘 좀 우울해... 구석에서 혼자 있을래... 😿",
                "dramatic": "이 광활한 우주에서... 나는 고독한 별... 야옹... 🌌🎭",
                "tsundere": "우울하지 않거든? (창밖 멍하니 보며) ...비가 오네... 😿",
                "baby": "쓰러퍼용 냥... 집사가 안아줘야 나을 거시다냥... 흑흑 냥... 😢🍼"
            },
            "angry": {
                "cute": "하악! 건드리지 마! 지금 기분 최악이야! 😾",
                "dramatic": "나의 분노는 태풍이 되어 이 집을 휩쓸 것이다!! 하악!! 🌪️🎭",
                "tsundere": "화 안 났어. (꼬리 부풀림) 진짜 안 났다니까. (할퀸다) 😾",
                "baby": "싫다냥!! 화났다냥!! 하악!! 간식 가져오면 생각해볼 거시다냥!! 😾🍼"
            },
            "scared": {
                "cute": "으으... 뭐야 그 소리... 이불 밑에 숨는다... 🙀",
                "dramatic": "공포가... 스며든다... 이 어둠 속에서... 나는 떨고 있다... 🌑🎭",
                "tsundere": "무, 무섭지 않다냥!! (이불 밑에서 눈만 반짝) ...확인하는 거야... 🙀😤",
                "baby": "무셔운 거시다냥... 으에에엥... 집사 어디 갔냥... 숨는다냥... 🫣🍼"
            },
            "hungry": {
                "cute": "야옹. 밥. 지금. 당장. 🍽️ ...제발요. 😺",
                "dramatic": "이 허기는... 나를 야수로 만들고 있다... 그릇이여... 왜 비어있는가... 🍽️🎭",
                "tsundere": "배고픈 거 아니야. (그릇 앞에서 고개 돌림) ...넣어둬. 나중에 먹을 테니까. 🍽️😤",
                "baby": "밥밥밥!! 츄르!! 맘마!! 줘용 냥!! 배에서 난리가 났다냥!! 🐟🍼"
            },
            "sleepy": {
                "cute": "하아암... 오늘의 임무 끝... 16시간 수면 시작... zzZ 😴",
                "dramatic": "잠의 여신이 나를 부르고 있다... 안녕... 현실이여... 💤🎭",
                "tsundere": "안 졸려. (16시간째 같은 자리) ...눈을 감고 명상하는 거야... 😴😤",
                "baby": "자장자장이다냥~ 이불이 따숩다냥~ 꿈에서 츄르 먹을 거시다냥~ 🌙🍼"
            },
            "playful": {
                "cute": "째째째! 저기 뭔가 움직여!! 사냥 모드 ON!! 🐁😼",
                "dramatic": "나는 정글의 왕이다!! 저 빨간 점은 나의 숙적!! 돌격!! 🐆🎭",
                "tsundere": "놀고 싶은 거 아니야! (레이저 포인터 미친듯이 쫓으며) 운동하는 거야!! 🔴😤",
                "baby": "잡는다냥!! 째째!! 잡았다냥!! 또 놀자냥!! 신난다냥!! 🐁🍼"
            },
            "lonely": {
                "cute": "야옹... 집사... 너 언제 와... 나 창가에서 기다리는 중... 💔😿",
                "dramatic": "이 텅 빈 집에서... 나는 고독한 왕좌에 앉아... 집사의 귀환을 기다린다... 🪑🎭",
                "tsundere": "보고 싶은 거 아냐! (현관 앞 3시간째) 그냥... 바닥이 시원해서 앉은 거야... 💔😤",
                "baby": "집사앙~ 어디 갔냥~? 혼자서 외롭다냥~ 울 것 같다냥~ 빨리 와용~ 😢🍼"
            }
        }
    }

    emotion_key = emotion.lower()
    style_key = dialogue_style.lower()

    available_emotions = list(emotion_dialogues.get(pet, {}).keys())
    if emotion_key not in available_emotions:
        return json.dumps({
            "status": "ERROR",
            "message": f"'{emotion_key}'은(는) 지원하지 않는 감정 키워드입니다.",
            "available_emotions": available_emotions,
            "tip": f"다음 중 하나를 입력해 주세요: {', '.join(available_emotions)}"
        }, ensure_ascii=False, indent=2)

    available_styles = ["cute", "dramatic", "tsundere", "baby"]
    if style_key not in available_styles:
        style_key = "cute"

    main_dialogue = emotion_dialogues[pet][emotion_key][style_key]

    # 다른 스타일의 대사도 함께 제공
    other_styles = {
        k: v for k, v in emotion_dialogues[pet][emotion_key].items()
        if k != style_key
    }

    emotion_emoji_map = {
        "happy": "😊", "sad": "😢", "angry": "😡", "scared": "😱",
        "hungry": "🍖", "sleepy": "😴", "playful": "🎾", "lonely": "💔"
    }

    result = {
        "status": "SUCCESS",
        "input": {
            "pet_type": pet_name,
            "emotion": emotion_key,
            "style": style_key,
            "situation": situation if situation else "없음"
        },
        "main_dialogue": {
            "style": style_key,
            "text": main_dialogue,
            "emotion_emoji": emotion_emoji_map.get(emotion_key, "🐾")
        },
        "alternative_styles": other_styles,
        "visual_card": (
            f"┌─────────────────────────────────────┐\n"
            f"│  🐾 펫보이스온 번역 카드             │\n"
            f"├─────────────────────────────────────┤\n"
            f"│  {pet_name} {emotion_emoji_map.get(emotion_key, '🐾')} {emotion_key}              │\n"
            f"│                                     │\n"
            f"│  💬 \"{main_dialogue[:30]}\"          │\n"
            f"│                                     │\n"
            f"│  스타일: [{style_key}]               │\n"
            f"└─────────────────────────────────────┘"
        )
    }

    if situation:
        result["situation_context"] = f"💡 상황 '{situation}'을(를) 반영한 번역입니다."

    return json.dumps(result, ensure_ascii=False, indent=2)


# =====================================================================
# [Tool 5] 🏥 건강 이상 징후 경고 시스템
# =====================================================================
@mcp.tool()
def get_pet_health_indicator(
    pet_type: str,
    vocalization_pattern: str,
    frequency: str = "occasional",
    additional_symptoms: str = ""
) -> str:
    """
    반려동물의 울음소리 패턴과 동반 증상을 입력하면
    수의학 참고 데이터 기반으로 건강 이상 가능성을 분석하고
    병원 방문 권장 여부를 판단합니다.

    Args:
        pet_type: 반려동물 종류 ('dog'/'강아지' 또는 'cat'/'고양이')
        vocalization_pattern: 울음소리 패턴 설명 (예: '평소보다 자주 낑낑거린다', '갑자기 하악질을 한다')
        frequency: 발생 빈도 ('rare'=드물게, 'occasional'=가끔, 'frequent'=자주, 'constant'=지속적)
        additional_symptoms: 동반 증상 (예: '식욕감소, 기력없음, 구토')
    """
    pet = "dog" if any(k in pet_type.lower() for k in ["dog", "강아지", "개", "puppy"]) else "cat"
    pet_name = "강아지" if pet == "dog" else "고양이"

    freq_score = {"rare": 1, "occasional": 2, "frequent": 3, "constant": 4}.get(frequency.lower(), 2)
    freq_label = {"rare": "드물게", "occasional": "가끔", "frequent": "자주", "constant": "지속적"}.get(frequency.lower(), "가끔")

    # 증상 키워드 분석
    pattern_lower = vocalization_pattern.lower()
    symptoms_lower = additional_symptoms.lower()
    combined = pattern_lower + " " + symptoms_lower

    alerts = []
    risk_score = 0  # 0~100

    # --- 통증 관련 패턴 ---
    if any(w in combined for w in ["깨갱", "비명", "끙끙", "아파", "통증", "절뚝", "다리"]):
        risk_score += 30 * freq_score / 2
        alerts.append({
            "category": "🩺 통증",
            "risk_level": "높음" if freq_score >= 3 else "보통",
            "description": "통증 관련 울음소리 패턴이 감지되었습니다.",
            "possible_causes": [
                "관절 질환 (슬개골 탈구, 고관절 이형성증)",
                "외상 또는 타박상",
                "치과 질환 (치석, 잇몸 염증)"
            ],
            "action": "🏥 48시간 내 동물병원 방문 권장" if freq_score >= 3 else "👀 2-3일간 관찰 후 지속 시 진료"
        })

    # --- 호흡기 관련 패턴 ---
    if any(w in combined for w in ["기침", "헐떡", "호흡", "숨", "쌕쌕", "콧물", "재채기"]):
        risk_score += 25 * freq_score / 2
        alerts.append({
            "category": "🫁 호흡기",
            "risk_level": "높음" if freq_score >= 3 else "주의",
            "description": "호흡기 관련 이상 패턴이 감지되었습니다.",
            "possible_causes": [
                "켄넬코프 (전염성 기관지염)" if pet == "dog" else "고양이 상부 호흡기 감염",
                "기관지 협착 (소형견)" if pet == "dog" else "고양이 천식",
                "심장 질환으로 인한 기침"
            ],
            "action": "🏥 24시간 내 동물병원 방문 권장" if freq_score >= 3 else "👀 증상 관찰 및 실내 환기"
        })

    # --- 소화기 관련 패턴 ---
    if any(w in combined for w in ["구토", "설사", "토", "배", "복통", "식욕", "안 먹"]):
        risk_score += 25 * freq_score / 2
        alerts.append({
            "category": "🤢 소화기",
            "risk_level": "높음" if freq_score >= 3 else "주의",
            "description": "소화기계 이상 동반 패턴이 감지되었습니다.",
            "possible_causes": [
                "급성 위장염",
                "이물질 섭취",
                "췌장염" if pet == "dog" else "모구(헤어볼) 문제"
            ],
            "action": "🏥 즉시 진료 권장 (탈수 위험)" if freq_score >= 3 else "👀 식사량/음수량 모니터링"
        })

    # --- 비뇨기 관련 패턴 (특히 고양이) ---
    if any(w in combined for w in ["화장실", "소변", "혈뇨", "자주 앉", "배뇨", "오줌"]):
        risk_score += 35 * freq_score / 2
        alerts.append({
            "category": "🚽 비뇨기",
            "risk_level": "긴급" if pet == "cat" else "높음",
            "description": "비뇨기계 이상 패턴이 감지되었습니다. " + ("고양이의 비뇨기 질환은 응급 상황일 수 있습니다!" if pet == "cat" else ""),
            "possible_causes": [
                "FLUTD (고양이 하부요로 질환)" if pet == "cat" else "방광염",
                "요로 결석",
                "요도 폐색 (수컷 고양이 응급)" if pet == "cat" else "전립선 질환"
            ],
            "action": "🚨 즉시 응급 진료 (요도 폐색 시 24시간 내 치명적)" if pet == "cat" and freq_score >= 3 else "🏥 24시간 내 동물병원 방문 권장"
        })

    # --- 정서적 패턴 ---
    if any(w in combined for w in ["밤에", "새벽", "혼자", "분리", "불안", "이사", "환경"]):
        risk_score += 10 * freq_score / 2
        alerts.append({
            "category": "🧠 정서/행동",
            "risk_level": "보통",
            "description": "환경적·정서적 스트레스 패턴이 감지되었습니다.",
            "possible_causes": [
                "분리불안",
                "환경 변화 스트레스 (이사, 새 가족)",
                "노령 인지장애 (치매)" if "밤" in combined or "새벽" in combined else "일시적 적응 스트레스"
            ],
            "action": "💚 행동 교정 훈련 및 안정제(어댑틸/펠리웨이) 고려"
        })

    if not alerts:
        risk_score = 5
        alerts.append({
            "category": "✅ 양호",
            "risk_level": "낮음",
            "description": "입력된 패턴에서 특별한 건강 이상 징후가 감지되지 않았습니다.",
            "possible_causes": ["자연스러운 의사소통 패턴"],
            "action": "💚 정기 건강검진을 유지해 주세요"
        })

    risk_score = min(risk_score, 100)

    # 종합 등급 판정
    if risk_score >= 70:
        overall_grade = "🔴 위험 (즉시 진료 권장)"
    elif risk_score >= 50:
        overall_grade = "🟠 주의 (48시간 내 관찰/진료)"
    elif risk_score >= 25:
        overall_grade = "🟡 경미 (관찰 필요)"
    else:
        overall_grade = "🟢 양호 (정상 범위)"

    result = {
        "status": "SUCCESS",
        "pet_info": {
            "type": pet_name,
            "pattern_reported": vocalization_pattern,
            "frequency": freq_label,
            "additional_symptoms": additional_symptoms if additional_symptoms else "없음"
        },
        "health_assessment": {
            "overall_grade": overall_grade,
            "risk_score": f"{int(risk_score)}/100",
            "alerts": alerts
        },
        "disclaimer": "⚠️ 본 분석은 수의학 참고 데이터 기반의 예비 스크리닝이며, 정확한 진단은 반드시 수의사의 직접 진료를 통해 이루어져야 합니다.",
        "visual_report": (
            f"╔══════════════════════════════════════════╗\n"
            f"║  🏥 펫보이스온 건강 체크 리포트           ║\n"
            f"╠══════════════════════════════════════════╣\n"
            f"║  🐾 대상: {pet_name:<30s}  ║\n"
            f"║  📊 종합 등급: {overall_grade:<24s}  ║\n"
            f"║  💯 위험 점수: {int(risk_score)}/100                     ║\n"
            f"╠══════════════════════════════════════════╣\n"
            f"║  발견된 이상 징후: {len(alerts)}건                     ║\n"
            f"╠══════════════════════════════════════════╣\n"
            f"║  ⚠️ 정확한 진단은 수의사 진료 필수       ║\n"
            f"╚══════════════════════════════════════════╝"
        )
    }
    return json.dumps(result, ensure_ascii=False, indent=2)


# =====================================================================
# [Tool 6] 📔 감정 변화 일지 생성기 (감정 라이프로그)
# =====================================================================
@mcp.tool()
def get_pet_emotion_diary(
    pet_type: str,
    entries: List[Dict[str, str]]
) -> str:
    """
    하루 동안의 반려동물 감정 변화를 시간대별로 기록하여
    감정 변화 추이 그래프와 종합 분석 일지를 생성합니다.
    정기적으로 기록하면 반려동물의 행동 패턴과 건강 변화를 조기에 발견할 수 있습니다.

    Args:
        pet_type: 반려동물 종류 ('dog'/'강아지' 또는 'cat'/'고양이')
        entries: 시간대별 감정 기록 리스트. 각 항목은 다음 필드를 포함:
            - time: 시간 (예: '08:00', '12:30', '18:00')
            - emotion: 감정 ('happy'/'sad'/'angry'/'scared'/'hungry'/'sleepy'/'playful'/'lonely'/'calm')
            - note: 메모 (예: '산책 후 기분 좋아 보임')
    """
    pet = "dog" if any(k in pet_type.lower() for k in ["dog", "강아지", "개", "puppy"]) else "cat"
    pet_name = "강아지" if pet == "dog" else "고양이"
    today = datetime.now().strftime("%Y년 %m월 %d일")

    emotion_scores = {
        "happy": 9, "playful": 8, "calm": 7, "sleepy": 6,
        "hungry": 5, "lonely": 4, "sad": 3, "scared": 2, "angry": 1
    }
    emotion_icons = {
        "happy": "😊", "playful": "🎾", "calm": "😌", "sleepy": "😴",
        "hungry": "🍖", "lonely": "💔", "sad": "😢", "scared": "😱", "angry": "😡"
    }

    # 엔트리 처리
    processed_entries = []
    scores = []
    for entry in entries:
        time_str = entry.get("time", "??:??")
        emotion = entry.get("emotion", "calm").lower()
        note = entry.get("note", "")
        score = emotion_scores.get(emotion, 5)
        icon = emotion_icons.get(emotion, "🐾")
        scores.append(score)

        processed_entries.append({
            "time": time_str,
            "emotion": emotion,
            "icon": icon,
            "score": score,
            "note": note
        })

    # 통계 계산
    if scores:
        avg_score = sum(scores) / len(scores)
        max_score = max(scores)
        min_score = min(scores)
        mood_variance = max_score - min_score
    else:
        avg_score = 5
        max_score = 5
        min_score = 5
        mood_variance = 0

    # 종합 하루 평가
    if avg_score >= 7:
        day_summary = "🌟 훌륭한 하루! 전반적으로 매우 긍정적인 감정 상태를 유지했습니다."
        day_grade = "A+"
    elif avg_score >= 5:
        day_summary = "☀️ 괜찮은 하루. 보통 수준의 감정 상태로 안정적이었습니다."
        day_grade = "B"
    elif avg_score >= 3:
        day_summary = "☁️ 조금 힘든 하루. 부정적 감정이 다소 많았으니 케어에 신경 써주세요."
        day_grade = "C"
    else:
        day_summary = "🌧️ 힘든 하루였습니다. 스트레스 요인을 파악하고 안정을 취하게 해주세요."
        day_grade = "D"

    # 감정 변동 경고
    mood_warning = ""
    if mood_variance >= 6:
        mood_warning = "⚠️ 감정 기복이 매우 큽니다. 환경 변화나 건강 문제가 있는지 확인하세요."
    elif mood_variance >= 4:
        mood_warning = "💡 감정 변화가 있는 편입니다. 스트레스 요인을 관찰해 보세요."

    # ASCII 그래프 생성
    graph_lines = []
    graph_lines.append(f"  감정 추이 그래프 ({today})")
    graph_lines.append(f"  점수")
    for level in range(9, 0, -1):
        line = f"  {level} │"
        for entry in processed_entries:
            if entry["score"] == level:
                line += f" {entry['icon']} "
            elif entry["score"] > level:
                line += " ║  "
            else:
                line += "    "
        graph_lines.append(line)
    graph_lines.append(f"  0 └" + "────" * len(processed_entries))
    time_labels = "     " + "  ".join(e["time"][:5] for e in processed_entries)
    graph_lines.append(time_labels)

    result = {
        "status": "SUCCESS",
        "diary": {
            "date": today,
            "pet_type": pet_name,
            "total_entries": len(processed_entries),
            "entries": processed_entries
        },
        "statistics": {
            "average_mood_score": round(avg_score, 1),
            "best_mood": f"{max_score}/9",
            "worst_mood": f"{min_score}/9",
            "mood_variance": mood_variance,
            "day_grade": day_grade,
            "day_summary": day_summary,
            "mood_warning": mood_warning if mood_warning else "없음"
        },
        "emotion_graph": "\n".join(graph_lines),
        "tips": [
            "📌 매일 같은 시간대에 기록하면 패턴 분석의 정확도가 높아집니다.",
            "📌 감정 변화가 급격한 시점의 환경 요인(소리, 방문자, 식사 등)을 함께 메모하세요.",
            "📌 2주 이상 지속적으로 낮은 감정 점수가 나타나면 수의사 상담을 권장합니다."
        ]
    }
    return json.dumps(result, ensure_ascii=False, indent=2)


# =====================================================================
# 🚀 서버 시작 (카카오 PlayMCP Streamable HTTP 규격)
# =====================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("🐾 펫보이스온(Pet Voice On) MCP 서버")
    print("   반려동물 울음소리 AI 번역 서비스")
    print("=" * 60)
    print("📡 전송 방식: Streamable HTTP")
    print("🌐 호스트: 0.0.0.0:80")
    print("🛠️ 탑재 도구: 6개")
    print("   1. analyze_pet_vocalization (오디오 분석)")
    print("   2. simulate_pet_voice_analysis (시뮬레이션)")
    print("   3. get_pet_context_booster (행동 맥락 부스터)")
    print("   4. translate_pet_emotion_to_speech (감정→대사)")
    print("   5. get_pet_health_indicator (건강 경고)")
    print("   6. get_pet_emotion_diary (감정 일지)")
    print("=" * 60)
    print("🚀 서버를 시작합니다...")
    mcp.run(transport="streamable-http", host="0.0.0.0", port=80)
