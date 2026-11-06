# 시장조사팀 genspark-multimodel.md 8장 요청(2026-11-06): AI 원가 캐싱, 추가 크레딧 확장 매출, 동시 적용. 통일 기준 v3 입력, BM 루프.
import sys, os; H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, '..', 'unified')); sys.path.insert(0, os.path.join(H, '..', 'tech-ops')); sys.path.insert(0, os.path.join(H, '..', 'product'))
import contextlib, io
with contextlib.redirect_stdout(io.StringIO()):
    import model_v3 as M, costcalc as T, round4 as R
OK = lambda be, low: be is not None and be <= 84 and low <= 20
def sim(plan, price, var, n=3, ch1=.035, ch=.02, sales=150, onb=100, exp=0, cap=1.10, cm=.45, months=180):
    """확장: 가입 12개월 뒤부터 1곳 매출이 연 exp씩 늘고(상한 cap), 늘어난 매출은 공헌이익률 cm만 남는다(대손 1% 별도)."""
    dm = M.DEV_MONTHS + plan['add_dev']
    cum = -(M.CAPEX_BASE + plan['add_once'] + (plan['add_fixed'] + M.EXT) * plan['add_dev']); low = cum; neg = 0
    co = []; g = (1 + exp) ** (1 / 12)
    for m in range(1, months + 1):
        co = [(n, 1.0)] + [(c * (1 - (ch1 if k < 12 else ch)), min(cap, r * (g if k >= 12 else 1))) for k, (c, r) in enumerate(co)]
        cnt = sum(c for c, _ in co); up = sum(c * (r - 1) for c, r in co) * price
        rev = cnt * price + up
        op = rev * (1 - M.BAD) - cnt * var - up * (1 - cm) - (M.stage_of(cnt)[1] + plan['add_fixed']) - n * (sales + onb)
        cum += op; low = min(low, cum)
        if op < 0: neg = m
    return (neg + 1 + dm if neg < months else None), round(-low / 1e4, 1)
def fmt(r): return f"{M.ym(r[0]) if r[0] else '15년 안에 없음'} / {r[1]}억{'(통과)' if OK(*r) else ''}"
def vG(price, ai):
    a, v, _, _ = T.econ(T.PRICE[price], '기본', (.55, .45, 0), ai=ai)
    return a, v - a * M.BAD
AIS = [('기본 3만', 3), ('캐싱 5.5만', 5.5), ('캐싱 없음 11만', 11)]
if __name__ == '__main__':
    PV = [k for k in T.PRICE if k.startswith('가치가')][0]
    print('(1) AI 원가(G2 공용 상위에만 붙음, 믹스 55:45)')
    for pl in (PV, '하단 가정가'):
        print(' T2', pl, ' | '.join(f"{lab}: {fmt(sim(M.plan_G(), *vG(pl, ai)))}" for lab, ai in AIS))
    print(' E 80만(v3 변동비 29에 AI 없음):', fmt(sim(M.plan_E(), 80, 29)))
    print(' E 참고: 전 고객에 업무 AI를 붙이면', ' | '.join(f"{lab}: {fmt(sim(M.plan_E(), 80, 29 + ai))}" for lab, ai in AIS))
    print('(2) 확장(추가 크레딧, 상한 ×1.10, 공헌 45%) T2 가치가 기본 AI')
    for e in (0, .02, .05): print(f'  연 {e:.0%}:', fmt(sim(M.plan_G(), *vG(PV, 3), exp=e)), '| 하단가', fmt(sim(M.plan_G(), *vG('하단 가정가', 3), exp=e)))
    print('(3) 동시: AI 캐싱 5.5만 + 확장')
    for e in (.02, .05):
        print(f'  연 {e:.0%}: 가치가', fmt(sim(M.plan_G(), *vG(PV, 5.5), exp=e)), '| 하단가', fmt(sim(M.plan_G(), *vG('하단 가정가', 5.5), exp=e)))
    print('  참고 AI 11만 + 확장 5%: 가치가', fmt(sim(M.plan_G(), *vG(PV, 11), exp=.05)))
