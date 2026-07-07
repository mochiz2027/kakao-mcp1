# -*- coding: utf-8 -*-
"""핵심 도구 테스트 스크립트 - 최종 고도화 검증 버전"""
import json
import sys

# Windows cp949 인코딩 에러 방지
sys.stdout.reconfigure(encoding='utf-8')

from server import (
    analyze_pet_vocalization,
    get_pet_context_booster,
    capture_live_audio_translation
)

sep = "=" * 60
passed = 0
total = 0

# ---- TEST 1 ----
total += 1
print(f"\n{sep}")
print("TEST 1/3: 녹음 오디오 분석 (analyze_pet_vocalization)")
print(sep)
res_str = analyze_pet_vocalization(audio_path="dummy.wav", pet_type="강아지")
r = json.loads(res_str)
print(f"  Status: {r['status']}")
print(f"  분석모드: {r['analysis_mode']}")
print(f"  시뮬레이션 음역 테마: {r['simulation_model']['vocal_theme']}")
print(f"  추정 주파수: {r['simulation_model']['estimated_pitch_hz']}Hz")
print(f"  감정 분석: {r['emotion_analysis']['emotion']}")
print(f"  스트레스 지수: {r['emotion_analysis']['stress_level']}%")
print(f"  번역 대사: \"{r['emotion_analysis']['says']}\"")
print(f"  케어 가이드: \"{r['emotion_analysis']['care_tip']}\"")
print("\n📊 가상 오디오 분석 비주얼 리포트:")
print(r.get("visual_report"))

if r['status'] == 'SUCCESS':
    passed += 1
    print("  >> PASS")

# ---- TEST 2 ----
total += 1
print(f"\n{sep}")
print("TEST 2/3: 행동 맥락 부스터 (get_pet_context_booster)")
print(sep)
res_str = get_pet_context_booster(pet_type="강아지", behavior_description="낯선 외부인을 보고 꼬리를 꼿꼿이 세우고 이빨을 드러냄")
r = json.loads(res_str)
print(f"  Status: {r['status']}")
print(f"  감지된 수의학 패턴:")
for pattern in r['behavior_rules_analysis']['hints']:
    print(f"    - {pattern}")
print(f"  정확도 가중치 상승: +{r['behavior_rules_analysis']['accuracy_boost_percent']}%")
print(f"  스트레스 영향 지표: {r['behavior_rules_analysis']['stress_impact_modifier']:+d}%")
print("\n🧬 행동 분석 부스터 비주얼 카드:")
print(r.get("visual_card"))

if r['status'] == 'SUCCESS':
    passed += 1
    print("  >> PASS")

# ---- TEST 3 ----
total += 1
print(f"\n{sep}")
print("TEST 3/3: 실시간 라이브 분석 (capture_live_audio_translation)")
print(sep)
res_str = capture_live_audio_translation(pet_type="강아지", capture_seconds=3.0, simulate_if_no_mic=True)
r = json.loads(res_str)
print(f"  Status: {r['status']}")
print(f"  모드: {r['capture_mode']}")
print(f"  데시벨 변화 트렌드: {r['live_metrics']['vocal_trend']}")
print(f"  평균 주파수: {r['live_metrics']['average_pitch_hz']}Hz")
print(f"  최종 판단 감정: {r['emotion_analysis']['emotion']}")
print(f"  스트레스 지수: {r['emotion_analysis']['stress_level_percent']}%")
print(f"  실시간 번역 대사: \"{r['emotion_analysis']['says_translation']}\"")
print(f"  조치 팁: \"{r['emotion_analysis']['veterinary_action_tip']}\"")
print("\n🎙️ 실시간 라이브 분석 비주얼 리포트:")
print(r.get("visual_report"))

if r['status'] == 'SUCCESS':
    passed += 1
    print("  >> PASS")

# ---- FINAL ----
print(f"\n{'🐾' * 30}")
print(f"  최종 무결성 테스트 결과: {passed}/{total} 통과")
if passed == total:
    print("  🎉 공모전 제출용 최종 무결성 테스트 완벽 통과!")
else:
    print(f"  ⚠️ {total - passed}개 실패")
print(f"{'🐾' * 30}")
