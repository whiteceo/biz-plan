# 역산 v2: 인력 구성을 명시한 계단식 고정비. 단위 만 원/월. 사내 인력 포함 기준(white 2026-11-05 결정)
import math
DEV, UX, PM = 775, 516, 610           # KOSA 2026 시장 단가(회사 부담 총액), 경력 PM
DEV_IN, UX_IN = 450, 350              # 검토 문서 3.10 사내 인건비 가정
OTHER1 = 797.5                         # AWS 공용·MSP 월정액·마케팅·도구·PC·보험·장애 대응(검토 문서 3.10)
# (이름, 고객 상한, 인력 dict(역할: (인원FTE, 월 단가, 기존 사내 인력 여부)), 기타 현금)
ORG = {
 'Stage 1 조직': (200, {'개발(사내 4명×50%)': (2.0, DEV, True), 'UIX(사내 2명×50%)': (1.0, UX, True), 'PM': (1, PM, False)}, OTHER1),
 'Stage 2 조직': (1000, {'개발(사내 4명 전담)': (4.0, DEV, True), 'UIX(사내 2명 중 1.5명분)': (1.5, UX, True), 'PM': (1, PM, False),
                        '사업 책임자(SaaS 경력)': (1, 1200, False), '클라우드 운영·보안': (1, DEV, False), '마케팅 리더': (1, 600, False), 'CS 리더': (1, 500, False)}, OTHER1 + 300),
 'Stage 3 조직': (10**9, {'개발(사내 4 + 신규 4)': (8.0, DEV, 'half'), 'UIX': (2.0, UX, True), 'PM': (2, PM, False), '사업 책임자': (1, 1200, False),
                        '클라우드 운영·보안': (3, DEV, False), '데이터': (1, DEV, False), '마케팅': (2, 600, False), 'CS 리더': (1, 500, False), '재무·법무': (1, 600, False)}, OTHER1 + 800),
}
def org_cost(name, rate='market', cash=False):
    cap, staff, other = ORG[name]; tot = other; eng = 0
    for role, (fte, r, internal) in staff.items():
        if internal is True or internal == 'half':
            if cash: 
                if internal == 'half': tot += fte / 2 * r; eng += fte / 2 * r   # 신규 채용분만 현금
                continue
            rr = r if rate == 'market' else (DEV_IN if r == DEV else UX_IN)
            if internal == 'half': c = fte / 2 * rr + fte / 2 * r
            else: c = fte * rr
        else: c = fte * r
        tot += c
        if r in (DEV,) or role.startswith('UIX'): eng += c
    return tot, eng
for nm in ORG:
    t, e = org_cost(nm); ti, ei = org_cost(nm, 'internal'); tc, _ = org_cost(nm, cash=True)
    print(f"{nm}: 포함(시장 단가) {t:,.0f} (엔지니어·디자인 {e:,.0f}, {e/t:.0%}) | 포함(사내 단가) {ti:,.0f} | 현금 {tc:,.0f}")
CH = 0.02; ONB = 65
def var_of(a): return 29 if a <= 100 else 41
def cm(a, cac, ch=CH): return a - var_of(a) - ch * (cac + ONB)
def be(a, cac, F, ch=CH):
    c = cm(a, cac, ch); return math.ceil(F / c) if c > 0 else None
POPS = [('Stage 1 업종', 23927), ('Stage 1+2 업종', 31848), ('전국 30~99인', 47546), ('30인 이상 중소+중견', 63782)]
print('=== 조직별 손익분기 유지 고객 수 (사내 인력 포함, 시장 단가) [CAC 850 기준, 괄호 450~1,920]')
for nm in ORG:
    F, _ = org_cost(nm); Fi, _ = org_cost(nm, 'internal'); Fc, _ = org_cost(nm, cash=True)
    for a in (65, 80, 100, 130):
        b = be(a, 850, F); lo = be(a, 450, F); hi = be(a, 1920, F)
        print(f"{nm} ARPU {a}: {b} ({lo}~{hi}) | 사내 단가 {be(a,850,Fi)} | 현금 참고 {be(a,850,Fc)} | 점유 " + ', '.join(f"{p[0]} {b/p[1]*100:.2f}%" for p in POPS if b))
print('=== 고객 수별 필요 ARPU(사내 인력 포함 손익분기). 그 고객 수를 감당할 조직 적용')
def org_for(n): return 'Stage 1 조직' if n <= 200 else ('Stage 2 조직' if n <= 1000 else 'Stage 3 조직')
def need_a(n, cac, ch=CH):
    F, _ = org_cost(org_for(n)); lo, hi = 20, 2000
    for _ in range(60):
        m = (lo + hi) / 2
        if n * cm(m, cac, ch) >= F: hi = m
        else: lo = m
    return round(hi, 1)
for n in (100, 150, 200, 300, 500, 1000, 2000, 3000, 5000):
    print(n, org_for(n), {c: need_a(n, c) for c in (0, 450, 850, 1920)}, ' 해지1%/3% @850', need_a(n, 850, .01), need_a(n, 850, .03))
print('=== 필요 월 신규(총 유치) 수: N곳에 T개월 안에 도달. v = N×해지율 ÷ (1 − (1−해지율)^T)')
for N in (110, 200, 400, 1000, 2000):
    print(N, {T: round(N * CH / (1 - (1 - CH) ** T), 1) for T in (24, 36, 60)}, '| 정상상태 유지에 필요한 월 신규', round(N * CH, 1))
print('=== 인력 구성 민감도: Stage 1 조직, ARPU 80, CAC 850')
F0, _ = org_cost('Stage 1 조직')
for lab, dF in (('기준', 0), ('개발 1.0명분 감소(AI 코딩 도구 등)', -DEV), ('개발 1.0명분 증가', DEV), ('UIX 0.5명분', -UX * 0.5), ('PM 없이', -PM), ('사내 단가 적용', org_cost('Stage 1 조직','internal')[0] - F0), ('고객 지원 1명 고정 추가', 500)):
    print(lab, round(F0 + dF), be(80, 850, F0 + dF))
print('Stage 2 조직 개발 전담 4.0 → 3.0 / 6.0:', be(80, 850, org_cost('Stage 2 조직')[0] - DEV), be(80, 850, org_cost('Stage 2 조직')[0] + 2 * DEV))
print('해지율 민감도 Stage 1 ARPU 80 CAC 850: 1%', be(80, 850, F0, .01), '2%', be(80, 850, F0), '3%', be(80, 850, F0, .03))
print('=== 유치 속도별 도달 기간(사내 인력 포함 지속 월 흑자). 기존 채널 3곳은 CAC 0, 나머지 CAC 적용, 조직은 고객 200·1,000곳에서 전환')
CAPEX_INCL = 2531 + 3881 + 610 * 9 + 2066 * 9   # 외부 일회 + ... 검토 문서 CAPEX 약 2.80억과 맞춤
CAPEX_INCL = 27965; CAPEX_CASH = 9371
def run(v, a, cac, cash=False, months=240):
    n = 0; cum = -(CAPEX_CASH if cash else CAPEX_INCL); last_neg = 0; low = cum; pay = None; nbe = None
    for m in range(1, months + 1):
        n = n * (1 - CH) + v
        F = org_cost(org_for(n), cash=cash)[0]
        pr = n * (a - var_of(a)) - F - v * ONB - max(0, v - 3) * cac
        cum += pr; low = min(low, cum)
        if pr < 0: last_neg = m; nbe = None
        elif nbe is None: nbe = round(n)
        if pay is None and cum >= 0: pay = m
    b = last_neg + 1 if last_neg < months else None
    return b, nbe, pay, round(-low / 1e4, 1)
def ym(m):
    if m is None: return '20년 안에 못 함'
    y, mm = divmod(m, 12); return f"{y}년 {mm}개월" if y and mm else (f"{y}년" if y else f"{mm}개월")
for a in (65, 80, 100):
    for v in (3, 5, 10, 20, 30, 52):
        out = []
        for cac in (450, 850, 1920):
            b, nb, pay, low = run(v, a, cac)
            out.append(f"CAC {cac}: 흑자 착수 후 {ym(b+12) if b else '못 함'}({nb}곳)·회수 {ym(pay+12) if pay else '못 함'}·최대적자 {low}억")
        bc = run(v, a, 850, True)
        print(f"ARPU {a} · 매달 {v}곳 (정상상태 {round(v/CH)}곳) | " + ' | '.join(out) + f" | 현금 참고(850) 흑자 {ym(bc[0]+12) if bc[0] else '못 함'}")
