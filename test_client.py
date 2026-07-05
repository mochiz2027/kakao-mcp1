"""
🐾 펫보이스온 (Pet Voice On) MCP 서버 - 로컬 통합 테스트 클라이언트 (최종 고도화 버전)

MCP 서버를 실행하지 않고도 내부 도구 함수들의 비즈니스 로직을
직접 호출하여 JSON 출력 형식과 정상 작동 여부를 빠르게 검증합니다.
"""

import json
import sys

# Windows cp949 인코딩 에러 방지
sys.stdout.reconfigure(encoding='utf-8')

from server import (
    analyze_pet_vocalization,
    get_pet_context_booster,
    capture_live_audio_translation
)

def print_separator(title: str):
    print("\n" + "=" * 75)
    print(f"  🧪 테스트: {title}")
    print("=" * 75)

def run_test(title: str, func, *args, **kwargs):
    """도구 함수를 실행하고 결과를 출력합니다."""
    print_separator(title)
    try:
        result = func(*args, **kwargs)
        parsed = json.loads(result)
        print(json.dumps(parsed, ensure_ascii=False, indent=2))
        
        # 비주얼 카드 및 리포트 별도 출력으로 가독성 향상
        if "visual_report" in parsed:
            print("\n📊 [visual_report]:")
            print(parsed["visual_report"])
        elif "visual_card" in parsed:
            print("\n📊 [visual_card]:")
            print(parsed["visual_card"])
            
        status = parsed.get("status", "UNKNOWN")
        print(f"\n✅ 결과: {status}")
        return status == "SUCCESS"
            
    except Exception as e:
        print(f"\n❌ 오류 발생: {str(e)}")
        return False

def main():
    print("🐾" * 40)
    print("  펫보이스온 (Pet Voice On) MCP 서버 통합 테스트 - 최종 고도화 버전")
    print("🐾" * 40)

    total_tests = 0
    passed_tests = 0

    # ─────────────────────────────────────────────
    # [Test 1] 오디오 분석 (가상 시뮬레이션 및 실제 지원 겸용)
    # ─────────────────────────────────────────────
    total_tests += 1
    if run_test(
        "[1/3] 오디오 분석 도구 호출 (analyze_pet_vocalization)",
        analyze_pet_vocalization,
        audio_path="nonexistent.wav",
        pet_type="강아지"
    ):
        passed_tests += 1

    # ─────────────────────────────────────────────
    # [Test 2] 행동 맥락 부스터 (NLP 분석 적용)
    # ─────────────────────────────────────────────
    total_tests += 1
    if run_test(
        "[2/3] 행동 맥락 부스터 호출 (get_pet_context_booster)",
        get_pet_context_booster,
        pet_type="고양이",
        behavior_description="집사 품에서 눈을 지긋이 감고 골골골하며 꾹꾹이를 함"
    ):
        passed_tests += 1

    # ─────────────────────────────────────────────
    # [Test 3] 실시간 라이브 분석 (질감 & 변화 추세 포함)
    # ─────────────────────────────────────────────
    total_tests += 1
    if run_test(
        "[3/3] 실시간 마이크 수집 및 번역 호출 (capture_live_audio_translation)",
        capture_live_audio_translation,
        pet_type="강아지",
        capture_seconds=3.0,
        simulate_if_no_mic=True
    ):
        passed_tests += 1

    # ─────────────────────────────────────────────
    # 최종 결과 요약
    # ─────────────────────────────────────────────
    print("\n" + "🐾" * 40)
    print(f"  📊 최종 테스트 결과: {passed_tests}/{total_tests} 통과")
    if passed_tests == total_tests:
        print("  🎉 모든 최종 테스트 완벽 통과! 공모전 등록 제출용 준비 완료!")
    else:
        print(f"  ⚠️ {total_tests - passed_tests}개 테스트 실패. 코드를 확인해 주세요.")
    print("🐾" * 40)

    sys.exit(0 if passed_tests == total_tests else 1)

if __name__ == "__main__":
    main()
