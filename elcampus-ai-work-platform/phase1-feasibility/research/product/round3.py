# 반복 라운드 3 (2026-11-06): 상품 재설계. 결론 기준·정의·채널 가정은 scen.py·baseline-assumptions.md와 같다(매달 3곳까지 CAC 0, 해지 2%).
# 레버: 1 공용(멀티테넌트) 기본형 + 전용 클라우드 상위 옵션(BM 13.4)  2 업무 맥락 AI를 상한 있게 가격에 포함
#       3 인원 구간 과금  4 최소 판매 가능 범위  5 교육 이수 기록·도입 지원을 상품 안 차별점으로.
# 모든 상품 입력값은 [가정]. 비교 기준은 product-offer.md 11장 표.
from target import DEV, OPT, ym
from scen import run, SC

# AI 원가 [계산]: Claude Haiku 5.5 입력 $0.10, 출력 $0.50 / 100만 토큰(claude-api 스킬 가격표, 2026-10-06 캐시).
#   1회 = 입력 3,000 + 출력 500 토큰 -> $0.00055 ≈ 0.77원(환율 1,400원 가정). 상위 모델(Sonnet 5.5 $2/$10)은 1회 ≈ 15.4원.
#   50인 × 하루 20회 × 22일 = 22,000회, 상위 모델 10% 혼합 -> 약 4.9만 원/월. 상한(회사당 월 2.2만 회)을 두면 AI 원가 ≤ 약 5만 원.
#   기본 3만 원(실사용 60%), 스트레스·보수 6만 원(상한 근접 + 재시도).
def per_call(inp, out, pin, pout, fx=1400): return (inp * pin + out * pout) / 1e6 * fx
HAIKU = per_call(3000, 500, .10, .50); SONNET = per_call(3000, 500, 2, 10)
AI_CAP = 22000 * (.9 * HAIKU + .1 * SONNET) / 1e4   # 만 원

# 구간 가격(만 원/월): 30~49인 79, 50~99인 119. 전국 30~49인 29,151곳 : 50~99인 18,395곳(market-size-national.md) -> 61:39.
W = 29151 / (29151 + 18395); LIST = W * 79 + (1 - W) * 119
ADDON, ADDON_VAR = 15, 7     # 안전 AI 애드온 월 15만 원, 원가 AI 5만 + 지원 2만(BM 14.2 업종 특화형과 같음)
OPTION, OPTION_VAR = 20, 9   # 전용 클라우드 옵션 월 20만 원, 원가 9만 원(전용 인프라 17만 - 공용 5만 + 운영 자동화 전제 [가정])
MT_VAR = 17                  # 공용형 고객당 변동비(BM 13.4: 29 -> 약 17)

def price(disc, addon_rate, opt_rate, ai):
    a = LIST * (1 - disc) + ADDON * addon_rate + OPTION * opt_rate
    v = MT_VAR + ai + ADDON_VAR * addon_rate + OPTION_VAR * opt_rate
    return round(a, 1), round(v, 1)

F_OPT = {
 # F0: 현행 E를 공용형으로만 바꾼 기준선(가격 그대로, 개발 +2개월).
 'F0 현행 공용형': dict(add_fixed=0, add_dev=2, add_once=0, cac=850),
 # F1: 공용형 + 업무 맥락 AI 포함 + 안전 기본형 + 교육 이수 연계·도입 지원. 개발 +5개월(공용 2, AI 1, 안전 2),
 #     월 고정 + AI 개발 0.5명분(388) + 외부 안전보건 전문가 0.5명분 300, 일회 1,500(콘텐츠·법률 검토 1,000 + 보안 점검 500).
 'F1 공용형 AI 포함 + 안전 기본형': dict(add_fixed=0.5 * DEV + 300, add_dev=5, add_once=1500, cac=850),
 # F2: F1에서 안전 기능·전문가를 빼 최소 범위(공용 + AI 포함 + 교육 연계). 개발 +3개월, 일회 500.
 'F2 최소 범위형(공용 + AI 포함)': dict(add_fixed=0.5 * DEV, add_dev=3, add_once=500, cac=850),
}
F_SC = {
 'F0 현행 공용형': {'낙관': (80, 17, 4, .02), '기본': (80, 17, 3, .02), '스트레스': (80, 17, 3, .03), '보수': (80, 17, 2, .03)},
 'F1 공용형 AI 포함 + 안전 기본형': {
    '낙관': (*price(0, .5, .10, 3), 4, .02), '기본': (*price(.05, .3, .05, 3), 3, .02),
    '스트레스': (*price(.05, .3, .05, 6), 3, .03), '보수': (*price(.15, .15, 0, 6), 2, .03)},
 # F2는 안전 애드온이 없고 30~49인 69 / 50~99인 109로 10만 원 낮다(안전 기본형 제외분).
 'F2 최소 범위형(공용 + AI 포함)': {},
}
L2 = W * 69 + (1 - W) * 109
def p2(disc, opt_rate, ai): return round(L2 * (1 - disc) + OPTION * opt_rate, 1), round(MT_VAR + ai + OPTION_VAR * opt_rate, 1)
F_SC['F2 최소 범위형(공용 + AI 포함)'] = {'낙관': (*p2(0, .10, 3), 4, .02), '기본': (*p2(.05, .05, 3), 3, .02),
                                       '스트레스': (*p2(.05, .05, 6), 3, .03), '보수': (*p2(.15, 0, 6), 2, .03)}

if __name__ == '__main__':
    print(f"AI 1회 원가: Haiku 5.5 {HAIKU:.2f}원, Sonnet 5.5 {SONNET:.1f}원 / 50인 상한 월 원가 {AI_CAP:.1f}만 원")
    print(f"구간 가격 가중 평균: F1 {LIST:.1f}만 원, F2 {L2:.1f}만 원 (30~49인 비중 {W:.0%})\n")
    print('상품안 | 시나리오 | 월 매출/곳 | 변동비/곳 | 매달 | 해지 | 지속 월 흑자(착수 후) | 15년 뒤 고객 | 그때 월 영업이익(이익률) | 최대 누적 적자 | 참고: 회수 | 참고: 희망 수준')
    allopt = {**OPT, **F_OPT}; allsc = {'E 현행 구상': SC['E 현행 구상'], 'B 조직 AI 업무 플랫폼 + 안전 기본형(D+)': SC['B 조직 AI 업무 플랫폼 + 안전 기본형(D+)'], **F_SC}
    for k, d in allsc.items():
        for sn, (a, v, N, ch) in d.items():
            r = run(allopt[k], N, a, v, ch)
            print(f"{k} | {sn} | {a} | {v} | {N} | {ch:.0%} | {ym(r['be'])} | {r['n']} | {r['op']:,} ({r['mg']:.0%}) | {r['low']}억 | {ym(r['pay'])} | {ym(r['hit'])}")
    print('\n참고: 해지 1% (기본)')
    for k in F_SC:
        a, v, N, ch = F_SC[k]['기본']; r = run(F_OPT[k], N, a, v, .01)
        print(f"  {k}: 지속 월 흑자 {ym(r['be'])}, 15년 뒤 {r['n']}곳, 월 영업이익 {r['op']:,}, 최대 적자 {r['low']}억")
    print('\n기본 시나리오에서 E 기본(3년 6개월) 이하가 되는 월 매출/곳 (변동비 고정)')
    e = run(OPT['E 현행 구상'], 3, 80, 29, .02)
    for k in F_SC:
        a0, v, N, ch = F_SC[k]['기본']
        for a10 in range(500, 2000, 5):
            a = a10 / 10; r = run(F_OPT[k], N, a, v, ch)
            if r['be'] and r['be'] <= e['be']: print(f"  {k}: {a} (기본 {a0}, 지속 흑자 {ym(r['be'])})"); break
    print('\n매달 신규 민감도(기본 가격, 해지 2%; 3곳 넘는 몫은 CAC 850만 원): 지속 월 흑자 / 최대 적자')
    for k in ['E 현행 구상'] + list(F_SC):
        a, v, _, ch = allsc[k]['기본']
        print('  ' + k + ': ' + ' · '.join(f"{N}곳 {ym(run(allopt[k], N, a, v, ch)['be'])}/{run(allopt[k], N, a, v, ch)['low']}억" for N in (2, 3, 4, 6, 10)))
    print('\n채널 참고(기대치 높을 수 있음): CAC 0 범위가 매달 6곳·10곳이면 (기본 가격, 해지 2%)')
    for k in ['E 현행 구상'] + list(F_SC):
        a, v, _, ch = allsc[k]['기본']
        print('  ' + k + ': ' + ' · '.join(f"{N}곳 {ym(run(allopt[k], N, a, v, ch, free=N)['be'])}/{run(allopt[k], N, a, v, ch, free=N)['low']}억/15년 뒤 월 {run(allopt[k], N, a, v, ch, free=N)['op']:,}" for N in (6, 10)))
