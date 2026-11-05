# 상품안 × 시나리오(낙관·기본·스트레스·보수). 결론 기준 = 사내 인력 포함 지속 월 흑자(white 2026-11-05 결정). 회수·희망 수준은 참고.
# 정의: 착수 후 = 개발 기간 포함, 시장 검증 3개월 제외(검토 문서 5장·model_v6와 같음).
#       확보 비용: 매달 4곳까지는 기존 교육 고객 채널(검토 문서 5.2의 상단)로 보고 온보딩 비용만, 4곳을 넘는 몫은 1곳당 CAC.
#       조직: 고객 200곳까지 Stage 1, 1,000곳까지 Stage 2(BM 11.2). 모든 상품 입력값은 [가정], 비교 기준은 product-offer.md 5장.
import math
from target import EXT, OPT, STAGE, CAPEX_BASE, DEV_MONTHS, ONB, TARGET_REV, TARGET_MARGIN, stage_of, ym

def run(o, N, arpu, var, churn, months=180, free=4, onb=ONB):
    dm = DEV_MONTHS + o['add_dev']
    cum = -(CAPEX_BASE + o['add_once'] + (o['add_fixed'] + EXT) * o['add_dev']); low = cum
    n = 0; last_neg = 0; pay = None; hit = None
    for m in range(1, months + 1):
        n = n * (1 - churn) + N
        s, F = stage_of(n); F += o['add_fixed']
        rev = n * arpu
        op = rev - n * var - F - N * onb - max(0, N - free) * o['cac']
        cum += op; low = min(low, cum)
        if op < 0: last_neg = m
        ok = rev >= TARGET_REV and op >= TARGET_MARGIN * rev
        if ok and hit is None: hit = m
        if not ok: hit = None
        if pay is None and cum >= 0: pay = m
    be = last_neg + 1 if last_neg < months else None
    f = lambda x: x + dm if x else None
    return dict(be=f(be), pay=f(pay), hit=f(hit), low=round(-low / 1e4, 1), n=round(n), op=round(op), mg=op / rev if rev else 0)

SC = {  # 상품안: {시나리오: (월 매출/곳, 변동비/곳, 매달 신규, 월 해지)}
 'E 현행 구상': {'낙관': (80, 29, 4, .02), '기본': (80, 29, 3, .02), '스트레스': (80, 29, 3, .03), '보수': (80, 29, 2, .03)},
 'B 조직 AI 업무 플랫폼 + 안전 기본형(D+)': {'낙관': (107.5, 37.5, 4, .02), '기본': (94.5, 36.1, 3, .02), '스트레스': (94.5, 36.1, 3, .03), '보수': (83, 35.4, 2, .03)},
 'C 현장·사무 통합 플랫폼(현장형)': {'낙관': (125, 44.3, 4, .02), '기본': (101, 41.4, 3, .02), '스트레스': (101, 41.4, 3, .03), '보수': (80.5, 37, 2, .03)},
 'D 현장형 + 100~299인 확장': {'낙관': (174, 55.5, 4, .02), '기본': (123.4, 47, 3, .02), '스트레스': (123.4, 47, 3, .03), '보수': (92.5, 41, 2, .03)},
}
if __name__ == '__main__':
    print('상품안 | 시나리오 | 월 매출/곳 | 매달 | 해지 | 지속 월 흑자(착수 후) | 15년 뒤 고객 | 그때 월 영업이익(이익률) | 최대 누적 적자 | 참고: 회수 | 참고: 희망 수준')
    for k, d in SC.items():
        for sn, (a, v, N, ch) in d.items():
            r = run(OPT[k], N, a, v, ch)
            print(f"{k} | {sn} | {a} | {N} | {ch:.0%} | {ym(r['be'])} | {r['n']} | {r['op']:,} ({r['mg']:.0%}) | {r['low']}억 | {ym(r['pay'])} | {ym(r['hit'])}")
    print('\n민감도: 기존 채널 고객에도 1곳당 영업 시간 비용 75만 원(교육 영업 담당 3일 × 일 25만 원, 자리표시자)을 더하면')
    for k in SC:
        a, v, N, ch = SC[k]['기본']; r = run(OPT[k], N, a, v, ch, onb=ONB + 75)
        print(f"  {k} 기본: 지속 월 흑자 {ym(r['be'])}, 월 영업이익 {r['op']:,}, 최대 적자 {r['low']}억")
    print('\n기본 시나리오에서 지속 월 흑자가 E 기본 이하로 당겨지는 월 매출/곳(매달 3곳, 해지 2%)')
    e = run(OPT['E 현행 구상'], 3, 80, 29, .02)
    for k in list(SC)[1:]:
        a0, v, N, ch = SC[k]['기본']
        for a10 in range(800, 3000, 5):
            a = a10 / 10; r = run(OPT[k], N, a, v + (a - a0) * 0, ch)
            if r['be'] and r['be'] <= e['be']: print(f"  {k}: {a} (지속 흑자 {ym(r['be'])}, 15년 뒤 월 영업이익 {r['op']:,}, 적자 {r['low']}억)"); break
    print(f"  E 기본: 지속 흑자 {ym(e['be'])}, 월 영업이익 {e['op']:,}")
