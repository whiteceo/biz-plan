# 시장조사팀 genspark/aggregator.py(13장) 독립 재현 + v3 정합 보정(BM 개발, 2026-11-06). 안 정의는 aggregator.py에서 가져오고 루프는 따로 짰다.
import sys, os; H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, '..', 'genspark'))
import contextlib, io
with contextlib.redirect_stdout(io.StringIO()):
    import aggregator as G
def sim(p, N=3, ch1=.035, ch=.02, months=180, build_fixed=False, onb=None, sales=None):
    """build_fixed: v3처럼 구축 기간에도 관리 묶음·점검·AWS 고정을 낸다(v3 plan_G는 add_fixed를 개발 개월만큼 일회로 쌓음)."""
    once = p['once'] + ((G.MGMT + G.SEC + G.INFRA_FIX) * p['dev'] if build_fixed else 0)
    cum = -once; low = cum; ages = []; neg = 0
    acq = N * ((p['onb'] if onb is None else onb) + (p['sales'] if sales is None else sales))
    for m in range(1, months + 1):
        ages = [N] + [c * (1 - (ch1 if k < 12 else ch)) for k, c in enumerate(ages)]
        op = sum(ages) * (p['a'] - p['v']) - p['F'] - acq
        cum += op; low = min(low, cum)
        if op < 0: neg = m
    return (neg + 1 + p['dev'] if neg < months else None), round(-low / 1e4, 1), round(sum(ages))
f = lambda r: f"{G.ym(r[0])} / {r[1]}억 / {r[2]}곳"
if __name__ == '__main__':
    for p in (G.M1, G.M2):  # 리셀·도입 대행안(M3)은 white님 지시(리셀 구조 제외, 2026-11-06)로 뺐다
        print(p['name'], '| 재현', f(sim(p)), '| 스트레스', f(sim(p, ch=.03)), '| 보수', f(sim(p, N=2, ch=.03)))
    print('M1 매달 10곳', f(sim(G.M1, N=10)), '| 석 4.4만', f(sim(G.plan('x', 15, 4.4, 1.0, 4, (2,.5,.5,0), (2,.5,.5,.5)))))
    print('--- v3 정합 보정')
    for p in (G.M1, G.M2):
        print(p['name'], '구축 기간 고정비 포함', f(sim(p, build_fixed=True)), '| + 도입 100', f(sim(p, build_fixed=True, onb=100)))
    print('M1 석 4.4만 + 구축 고정 + 도입 100', f(sim(G.plan('x', 15, 4.4, 1.0, 4, (2,.5,.5,0), (2,.5,.5,.5)), build_fixed=True, onb=100)))
    print('M1 매달 10곳 + 구축 고정 + 도입 100', f(sim(G.M1, N=10, build_fixed=True, onb=100)))
