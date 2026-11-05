# 16장: 유치 가정을 '고정 월 N곳'에서 성장 곡선으로 바꾼 계산. 단위 만 원/월, 사내 인력 포함(white 2026-11-05 기준 = 지속 월 흑자).
# 상품안 입력은 상품기획팀 research/product/target.py의 OPT를 그대로 가져온다(모두 가정).
# 정의(레드팀 I2·I3 통일): 착수 후 = 개발 기간 + 출시 후 개월(시장 검증 기간 별도 없음). 기존 채널 월 floor곳까지 CAC 0, 그 위는 CAC.
#   추가 개발 개월에는 기존 사내 인력(2,066)+PM(610)과 상품안 추가 고정비가 함께 든다.
import math, sys, contextlib, io
sys.path.insert(0, '../product')
with contextlib.redirect_stdout(io.StringIO()):
    from target import OPT, stage_of, ONB, CAPEX_BASE, DEV_MONTHS
K = 63782 * 0.05   # 시장 상한(가정): 30인 이상 중소+중견 63,782곳(산업통상부 2024 기본통계) × 점유 5%. 곡선을 꺾는 장치일 뿐 근거 있는 상한이 아니다

# 성장 곡선: 출시 후 개월 t의 '순 고객 증가율' g(t). ChartMogul SaaS Growth Report 2023(2,200여 곳, 첫 유료 고객 기준)의 월 MRR 성장률을 고객 수 증가율로 옮겼다
# (가정: ARPU 고정, 확장 매출 없음 → MRR 성장보다 보수적). 2024 보고서: 연 매출 100만 달러 미만 자력 성장 기업의 신규 매출은 전년 대비 −9%(2024 1분기).
CURVES = {
 '성공 사례(상위 사분위)': lambda t: 0.06 if t <= 24 else (0.04 if t <= 48 else 0.02),   # 처음 월 5~7%, 이후 3~5%
 '중간 사례(중앙값)':      lambda t: 0.0225 if t <= 60 else 0.015,                         # 생애 내내 월 2~2.5%
 '가속 없음':             lambda t: 0.0,                                                   # 기존 채널 floor만(선형)
}
def run(o, curve, floor=3, churn=0.02, cac=None, sales_cost=0, months=240, arpu=None):
    """floor: 기존 채널(교육 고객) 월 유치(CAC 0). sales_cost: 기존 채널 1곳당 교육 영업 시간 비용(레드팀 I4)."""
    a = arpu or o['arpu']; c = o['cac'] if cac is None else cac; dm = DEV_MONTHS + o['add_dev']
    cum = -(CAPEX_BASE + o['add_once'] + (o['add_fixed'] + 2066 + 610) * o['add_dev']); low = cum
    n = 0.0; last_neg = 0; pay = None; hit = None; n_be = None; adds5 = []
    for t in range(1, months + 1):
        g = curve(t) * max(0.0, 1 - n / K)
        v = max(floor, (g + churn) * n)                 # 총 신규 = 기존 채널 floor 또는 (순증 + 해지 보충) 중 큰 값
        n = n * (1 - churn) + v
        s, F = stage_of(n); F += o['add_fixed']
        rev = n * a
        op = rev - n * o['var'] - F - v * ONB - max(0, v - floor) * c - min(v, floor) * sales_cost
        cum += op; low = min(low, cum)
        if op < 0: last_neg = t; n_be = None
        elif n_be is None: n_be = round(n)
        if pay is None and cum >= 0: pay = t
        if hit is None and rev >= 20000: hit = t
        if t in (12, 24, 36, 60, 84): adds5.append((t, round(v, 1), round(n)))
    be = last_neg + 1 if last_neg < months else None
    f = lambda x: x + dm if x else None
    return dict(be=f(be), pay=f(pay), low=round(-low / 1e4, 1), hit=f(hit), n_be=n_be, path=adds5)
def ym(m):
    if m is None: return '20년 안에 못 함'
    y, mm = divmod(m, 12); return f"{y}년 {mm}개월" if y and mm else (f"{y}년" if y else f"{mm}개월")
if __name__ == '__main__':
    keys = list(OPT)
    print('=== 상품안 × 곡선 (해지 2%, 기존 채널 3곳/월 CAC 0, 그 위 CAC 상품안 값)')
    for k in keys:
        for cn, cv in CURVES.items():
            r = run(OPT[k], cv)
            print(f"{k} | {cn} | 월 흑자 {ym(r['be'])} ({r['n_be']}곳) | 회수 {ym(r['pay'])} | 최대 적자 {r['low']}억 | 월 매출 2억(참고) {ym(r['hit'])} | 경로(출시 후 개월, 월 신규, 고객) {r['path']}")
    print('=== 스트레스: 해지 3% / 기존 채널 2곳 / 기존 채널 영업 시간 비용 1곳 100만 / CAC 1,920')
    for k in keys:
        for cn in ('중간 사례(중앙값)', '가속 없음'):
            cv = CURVES[cn]
            r1 = run(OPT[k], cv, churn=0.03); r2 = run(OPT[k], cv, floor=2); r3 = run(OPT[k], cv, sales_cost=100); r4 = run(OPT[k], cv, cac=1920)
            print(f"{k} | {cn} | 해지3% {ym(r1['be'])} | 기존2곳 {ym(r2['be'])} | 영업비용 {ym(r3['be'])} | CAC1920 {ym(r4['be'])}")
    print('=== 해지 1%(SaaS Capital 2025 소액 계약 GRR 약 90%/년, 레드팀 인용) 참고')
    for k in keys:
        r = run(OPT[k], CURVES['가속 없음'], churn=0.01); print(k, '가속 없음 해지1%', ym(r['be']), ym(r['pay']))
    print('=== 가속분 CAC 민감도(채널·추천으로 가속이 올 때): 성공 / 중간 곡선, CAC 0 / 200 / 450 / 850')
    for k in keys:
        for cn in ('성공 사례(상위 사분위)', '중간 사례(중앙값)'):
            out = []
            for c in (0, 200, 450, 850):
                r = run(OPT[k], CURVES[cn], cac=c); out.append(f"CAC{c}: 흑자 {ym(r['be'])}/회수 {ym(r['pay'])}/적자 {r['low']}억")
            print(k, '|', cn, '|', ' · '.join(out))
    print('=== 기본 가격(상품기획팀 6.3: B 94.5/변동 36.1, C 101/41.4, D 123.4/47) × 곡선, 해지 2% / 3%')
    BASEP = {'E 현행 구상': (80, 29), 'B 조직 AI 업무 플랫폼 + 안전 기본형(D+)': (94.5, 36.1),
             'C 현장·사무 통합 플랫폼(현장형)': (101, 41.4), 'D 현장형 + 100~299인 확장': (123.4, 47)}
    for k, (a, v) in BASEP.items():
        o = dict(OPT[k], arpu=a, var=v)
        for cn, cv in CURVES.items():
            r = run(o, cv); r3 = run(o, cv, churn=0.03); r2 = run(o, cv, floor=2)
            print(f"{k} {a} | {cn} | 흑자 {ym(r['be'])}({r['n_be']}곳) 회수 {ym(r['pay'])} 적자 {r['low']}억 | 해지3% 흑자 {ym(r3['be'])} | 기존2곳 흑자 {ym(r2['be'])}")
    print('=== 기본 가격, 성공 곡선, 가속분 CAC 0/200/450')
    for k, (a, v) in BASEP.items():
        o = dict(OPT[k], arpu=a, var=v)
        print(k, a, ' · '.join(f"CAC{c} {ym(run(o, CURVES['성공 사례(상위 사분위)'], cac=c)['be'])}" for c in (0, 200, 450)))
