# 연 1,000곳(월 약 83곳) 시나리오. 단위 만 원.
from bm_model import BASE, scen, ym
s = scen(1); AI = 35
def run(bm, cac, ramp, org=3000, disc=False, months=120):
    out = {}
    for incl in (True, False):
        cap = BASE['once_cash'] + BASE['pm'] * 9 + (2066 * 9 if incl else 0)
        n = 0; cum = -cap; pay = None; low = cum; yr = []; OP = 0; be = None
        for m in range(1, months + 1):
            if ramp and m <= 12: base, sales, extra = 3, 0, 0
            else: base, sales, extra = 3, 80, org
            new = base + sales; n = n * 0.98 + new
            var = 29 - (4.5 * 0.3 if (disc and n >= 150) else 0)
            add = 0; onb = 65
            if bm in ('S1', 'S2'): onb -= s['S1_onetime_gain']
            if bm == 'S2':
                d = 0.10 if (disc and n * 0.5 >= 400) else 0
                add = 0.5 * AI * (0.20 + d) - 0.5 * AI * 1.2 * 0.02 + s['inf_rev'] - s['inf_var']
            fixed = BASE['fixed_cash'] + BASE['pm'] + extra + (2066 if incl else 0)
            pr = n * (80 - var + add) - fixed - new * onb - sales * cac
            cum += pr; low = min(low, cum); OP += pr
            if be is None and pr >= 0 and m > 1: be = m
            if pay is None and cum >= 0: pay = m
            if m % 12 == 0: yr.append((round(n), round(OP / 1e4, 1))); OP = 0
        out[incl] = (ym(pay + 9) if pay else '못 함', be, round(-low / 1e4, 1), yr[:5])
    return out
for ramp in (False, True):
    print('=== 출시 직후 83곳' if not ramp else '=== 1년 파일럿(3곳) 뒤 83곳')
    for cac in (450, 850, 1920):
        for bm, d in (('S0', False), ('S1', False), ('S2', False), ('S2', True)):
            r = run(bm, cac, ramp, disc=d); a, b = r[True], r[False]
            print(f"CAC {cac} {bm}{'+할인' if d else ''} | 회수 포함 {a[0]} 현금 {b[0]} | 월흑자 출시 후 {a[1]}개월 | 최대적자 {a[2]}억/{b[2]}억 | {a[3]}")
# 필요 조건
print('--- 조건')
print('월 영업·마케팅비(80곳 신규 영업):', {c: f"{80*c/1e4:.1f}억" for c in (450, 850, 1920)})
print('온보딩 인력: 83곳 × 1.25~4일 =', round(83*1.25), '~', round(83*4), '인일/월 →', round(83*1.25/21,1), '~', round(83*4/21,1), '명')
for C in (500, 1000, 1500):
    print(C, '곳 지원 인력(1명당 30~60곳):', round(C/60), '~', round(C/30), '명')
print('기존 교육고객 3,800곳 중 30~100인 760~1,520곳 → 기존 채널 매달 3곳(연 36곳). 연 1,000곳 = 30~100인 기존 고객 전체의', round(1000/1520*100), '~', round(1000/760*100), '%')
print('Stage 1+2 업종 31,848곳 대비 연 1,000곳 =', round(1000/31848*100,1), '% / 전국 30~99인 47,546곳 대비', round(1000/47546*100,1), '%')
# 정상 상태
print('정상 상태 고객 수(해지 2%): 83/0.02 =', round(83/0.02))
