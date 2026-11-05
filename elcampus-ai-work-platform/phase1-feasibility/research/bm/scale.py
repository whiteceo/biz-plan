# 규모별 BM 효과 (단위: 만 원). 고객 수 105·190·440·1,000곳 스냅샷 + 단계별 성장 경로 시뮬레이션
from bm_model import BASE, scen, ym
AI = 35          # AI 포함형 채택 고객 1곳당 월 AI 원가(50인 14~65 중 35, 추정)
print('=== 1. 규모별 연간 AI 사용 총액(원가)과 마진')
for C in (105, 190, 440, 1000):
    for att in (0.5, 1.0):
        spend = C * att * AI * 12
        mk = spend * 0.20 - spend * 1.2 * 0.02           # 마크업 20%, 대손 2%
        print(f"{C}곳 채택 {att:.0%} | AI 원가 연 {spend/1e4:.1f}억 (월 {spend/12:,.0f}만, 범위 {C*att*14*12/1e4:.1f}~{C*att*65*12/1e4:.1f}억) | 마크업 20% 공헌 연 {mk/1e4:.2f}억 | 할인 10% 시 +{spend*0.1/1e4:.2f}억, 20% +{spend*0.2/1e4:.2f}억")
print('=== 2. 할인 손익분기: 연 비용 X를 할인율 d로 상쇄하려면 필요한 연 AI 원가 = X / d')
for X in (1000, 2000):
    for d in (0.05, 0.10, 0.20):
        need = X / d; cust = need / (AI * 12)
        print(f"연 비용 {X}만, 할인 {d:.0%}: AI 원가 연 {need/1e4:.1f}억 = AI 포함 고객 약 {cust:.0f}곳")
need = 14000; print('약정 할인 기준(가정) 연 약 14억 원(100만 달러) → AI 포함 고객', round(need/(AI*12)), '곳 (채택 50%면 전체', round(2*need/(AI*12)), '곳)')
print('=== 3. 인프라 약정 할인: 서버·DB 월 4.5만에 30~40% → 고객당 월 1.35~1.8만')
for C in (105, 190, 440, 1000):
    print(C, '곳: 월', round(C*4.5*0.3), '~', round(C*4.5*0.4), '만 / 연', round(C*4.5*0.3*12/1e4,2), '~', round(C*4.5*0.4*12/1e4,2), '억')

print('=== 4. 단계별 성장 경로 시뮬레이션')
def path(bm, cac, scale_disc=False, months=120):
    p = dict(BASE); s = scen(1)
    capex_incl = p['once_cash'] + p['pm'] * 9 + 2066 * 9; capex_cash = p['once_cash'] + p['pm'] * 9
    res = {}
    for incl in (True, False):
        n = 0; cum = -(capex_incl if incl else capex_cash); pay = None; low = cum; yr = []; R = OP = 0; BMp = 0
        for m in range(1, months + 1):
            base_new, sales_new = (3, 0) if m <= 12 else ((3, 5) if m <= 36 else (3, 27))   # Stage1 3 / Stage2 8 / Stage3 30
            new = base_new + sales_new
            n = n * 0.98 + new
            arpu, var = 80, 29; onb = 65; add = 0
            if bm in ('S1', 'S2'): onb = 65 - s['S1_onetime_gain']
            if bm == 'S2':
                d = 0.10 if (scale_disc and n * 0.5 >= 400) else 0.0       # AI 포함 고객 400곳(연 원가 약 17억) 넘으면 약정 할인 10%(가정)
                ai_m = 0.5 * AI * (0.20 + d) - 0.5 * AI * 1.2 * 0.02
                inf_m = s['inf_rev'] - s['inf_var']
                add = ai_m + inf_m
            if scale_disc and n >= 150: var -= 4.5 * 0.3                       # 고객 150곳 넘으면 서버·DB 약정 30%
            fixed = p['fixed_cash'] + p['pm'] + (2066 if incl else 0)
            pr = n * (arpu - var + add) - fixed - new * onb - sales_new * cac
            BMp += n * add
            cum += pr; low = min(low, cum); R += n * (arpu + (add if bm=='S2' else 0)); OP += pr
            if pay is None and cum >= 0: pay = m
            if m % 12 == 0: yr.append((round(n), round(OP / 1e4, 2), round(BMp / 1e4, 2))); OP = BMp = 0
        res[incl] = (ym(pay + 9) if pay else '착수 후 10년 9개월 안에 못 함', round(-low / 1e4, 2), yr)
    return res
for cac in (450, 1920):
    for bm, sd in (('S0', False), ('S1', False), ('S2', False), ('S2', True)):
        r = path(bm, cac, sd)
        a, b = r[True], r[False]
        print(f"CAC {cac} | {bm}{' +규모 할인' if sd else ''} | 회수 포함 {a[0]} 현금 {b[0]} | 최대적자 포함 {a[1]}억 현금 {b[1]}억 | 연말 고객·연 손익(포함)·그중 AI·인프라 몫:", a[2][:6])
