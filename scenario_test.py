import json
import sys

# Windows cp949 인코딩 에러 방지
sys.stdout.reconfigure(encoding='utf-8')

from server import (
    analyze_pet_vocalization,
    get_pet_context_booster,
    capture_live_audio_translation
)

def run_tests():
    print("🐾 [테스트 시작] 펫보이스온 MCP 서버 통합 테스트 🐾")
    
    # 1. 기존 오디오 파일 분석 도구 테스트 (Stub 동작 확인)
    print("\n[Test 1] analyze_pet_vocalization 테스트")
    res1 = analyze_pet_vocalization(audio_path="dummy.wav")
    print(res1)
    
    # 2. 행동 맥락 부스터 테스트
    print("\n[Test 2] get_pet_context_booster 테스트")
    res2 = get_pet_context_booster(pet_type="강아지", behavior_description="현관문 앞에서 서성거림")
    print(res2)
    
    # 3. 새로운 실시간 마이크 수집 및 번역 도구 테스트 (시뮬레이션 모드)
    print("\n[Test 3] capture_live_audio_translation (강아지 시뮬레이션 모드)")
    res3 = capture_live_audio_translation(pet_type="강아지", capture_seconds=3.0, simulate_if_no_mic=True)
    parsed_res3 = json.loads(res3)
    
    print("\n📊 실시간 라이브 분석 JSON 결과:")
    print(json.dumps(parsed_res3, ensure_ascii=False, indent=2))
    
    print("\n📊 실시간 라이브 분석 비주얼 리포트:")
    print(parsed_res3.get("visual_report"))
    
    # 4. 실시간 마이크 수집 및 번역 도구 테스트 (고양이 시뮬레이션 모드)
    print("\n[Test 4] capture_live_audio_translation (고양이 시뮬레이션 모드)")
    res4 = capture_live_audio_translation(pet_type="고양이", capture_seconds=3.0, simulate_if_no_mic=True)
    parsed_res4 = json.loads(res4)
    
    print("\n📊 실시간 라이브 분석 비주얼 리포트:")
    print(parsed_res4.get("visual_report"))

if __name__ == "__main__":
    run_tests()
