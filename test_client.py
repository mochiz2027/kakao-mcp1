"""
🐾 펫보이스온 (Pet Voice On) MCP 서버 - 로컬 통합 테스트 클라이언트

MCP 서버를 실행하지 않고도 내부 도구 함수들의 비즈니스 로직을
직접 호출하여 JSON 출력 형식과 정상 작동 여부를 빠르게 검증합니다.

실행 방법:
    python test_client.py
"""

import json
import sys

# 서버 모듈에서 MCP 도구 함수들을 직접 임포트
from server import (
    analyze_pet_vocalization,
    simulate_pet_voice_analysis,
    get_pet_context_booster,
    translate_pet_emotion_to_speech,
    get_pet_health_indicator,
    get_pet_emotion_diary,
)


def print_separator(title: str):
    print("\n" + "=" * 70)
    print(f"  🧪 테스트: {title}")
    print("=" * 70)


def run_test(title: str, func, *args, **kwargs):
    """도구 함수를 실행하고 결과를 출력합니다."""
    print_separator(title)
    try:
        result = func(*args, **kwargs)
        parsed = json.loads(result)
        print(json.dumps(parsed, ensure_ascii=False, indent=2))

        # 비주얼 리포트가 있으면 추가 출력
        for key in ["visual_report", "visual_card", "emotion_graph"]:
            if key in parsed:
                print(f"\n📊 [{key}]:")
                print(parsed[key])

        status = parsed.get("status", "UNKNOWN")
        print(f"\n✅ 결과: {status}")
        return True
    except Exception as e:
        print(f"\n❌ 오류 발생: {str(e)}")
        return False


def main():
    print("🐾" * 35)
    print("  펫보이스온 (Pet Voice On) MCP 서버 통합 테스트")
    print("🐾" * 35)

    total_tests = 0
    passed_tests = 0

    # ─────────────────────────────────────────────
    # [Test 1] 오디오 분석 (파일 없음 → 에러 핸들링 확인)
    # ─────────────────────────────────────────────
    total_tests += 1
    if run_test(
        "[1/6] 오디오 분석 (파일 미존재 에러 핸들링)",
        analyze_pet_vocalization,
        audio_path="/tmp/nonexistent_bark.wav",
        pet_type="dog"
    ):
        passed_tests += 1

    # ─────────────────────────────────────────────
    # [Test 2] 시뮬레이션 분석 - 강아지 짖음
    # ─────────────────────────────────────────────
    total_tests += 1
    if run_test(
        "[2/6] 시뮬레이션 분석 - 강아지 짖음 (bark, high)",
        simulate_pet_voice_analysis,
        pet_type="강아지",
        vocalization_type="bark",
        intensity="high",
        duration_seconds=1.5
    ):
        passed_tests += 1

    # ─────────────────────────────────────────────
    # [Test 3] 시뮬레이션 분석 - 고양이 골골송
    # ─────────────────────────────────────────────
    total_tests += 1
    if run_test(
        "[3/6] 시뮬레이션 분석 - 고양이 골골송 (purr, low)",
        simulate_pet_voice_analysis,
        pet_type="고양이",
        vocalization_type="purr",
        intensity="low",
        duration_seconds=5.0
    ):
        passed_tests += 1

    # ─────────────────────────────────────────────
    # [Test 4] 행동 맥락 부스터
    # ─────────────────────────────────────────────
    total_tests += 1
    if run_test(
        "[4/6] 행동 맥락 부스터 - 강아지 현관 대기",
        get_pet_context_booster,
        pet_type="강아지",
        behavior_description="꼬리를 살랑살랑 흔들며 현관 앞에서 기다리고 있다",
        time_of_day="evening",
        environment="indoor"
    ):
        passed_tests += 1

    # ─────────────────────────────────────────────
    # [Test 5] 감정→대사 변환 (4가지 스타일)
    # ─────────────────────────────────────────────
    total_tests += 1
    if run_test(
        "[5/6] 감정→대사 변환 - 고양이 배고픔 (tsundere 스타일)",
        translate_pet_emotion_to_speech,
        pet_type="고양이",
        emotion="hungry",
        situation="집사가 퇴근하고 돌아왔다",
        dialogue_style="tsundere"
    ):
        passed_tests += 1

    # ─────────────────────────────────────────────
    # [Test 6] 건강 이상 징후 분석
    # ─────────────────────────────────────────────
    total_tests += 1
    if run_test(
        "[6/6] 건강 이상 징후 - 고양이 비뇨기 의심",
        get_pet_health_indicator,
        pet_type="고양이",
        vocalization_pattern="화장실 근처에서 자주 날카롭게 운다",
        frequency="frequent",
        additional_symptoms="소변량 감소, 식욕 저하"
    ):
        passed_tests += 1

    # ─────────────────────────────────────────────
    # [Bonus Test] 감정 일지
    # ─────────────────────────────────────────────
    total_tests += 1
    if run_test(
        "[BONUS] 감정 일지 - 강아지 하루 기록",
        get_pet_emotion_diary,
        pet_type="강아지",
        entries=[
            {"time": "08:00", "emotion": "happy", "note": "아침 산책 후 기분 좋음"},
            {"time": "12:00", "emotion": "hungry", "note": "밥그릇 앞에서 대기"},
            {"time": "14:00", "emotion": "sleepy", "note": "소파에서 낮잠"},
            {"time": "17:00", "emotion": "playful", "note": "공놀이 시간"},
            {"time": "19:00", "emotion": "happy", "note": "저녁 산책"},
            {"time": "22:00", "emotion": "calm", "note": "집사 옆에서 휴식"},
        ]
    ):
        passed_tests += 1

    # ─────────────────────────────────────────────
    # 최종 결과 요약
    # ─────────────────────────────────────────────
    print("\n" + "🐾" * 35)
    print(f"  📊 테스트 결과: {passed_tests}/{total_tests} 통과")
    if passed_tests == total_tests:
        print("  🎉 모든 테스트 통과! 서버 배포 준비 완료!")
    else:
        print(f"  ⚠️ {total_tests - passed_tests}개 테스트 실패. 코드를 확인해 주세요.")
    print("🐾" * 35)

    sys.exit(0 if passed_tests == total_tests else 1)


if __name__ == "__main__":
    main()
