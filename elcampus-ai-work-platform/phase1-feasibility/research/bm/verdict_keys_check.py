# 레드팀 verdict-keys.md 독립 재현(BM 개발, 2026-11-06). 입력(안 정의·변동비·조직 단계)은 통일 기준 v3(model_v3)에서 가져오고,
# 시뮬레이션 루프는 따로 짰다: 가입 월령별 배열, 첫해(월령 0~11)·이후 해지, 4곳째부터 다른 확보 비용(CAC) 지원.
import sys, os; H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, '..', 'unified'))
import contextlib, io
with contextlib.redirect_stdout(io.StringIO()):
    import model_v3 as M
OK = lambda be, low: be is not None and be <= 84 and low <= 20
def sim(plan, price, var, n=3, ch1=.035, ch=.02, sales=150, sales_extra=None, onb=100, months=180):
    """var: 대손 뺀 1곳 변동비. 대손은 매출의 1%. sales_extra: 4곳째부터 1곳 확보 비용(없으면 sales)."""
    dm = M.DEV_MONTHS + plan['add_dev']
    cum = -(M.CAPEX_BASE + plan['add_once'] + (plan['add_fixed'] + M.EXT) * plan['add_dev']); low = cum
    ages = []  # ages[k] = 가입 k개월째 고객 수
    neg = 0
    acq = min(n, 3) * sales + max(0, n - 3) * (sales if sales_extra is None else sales_extra) + n * onb
    for m in range(1, months + 1):
        ages = [n] + [c * (1 - (ch1 if k < 12 else ch)) for k, c in enumerate(ages)]
        cnt = sum(ages)
        op = cnt * price * (1 - M.BAD) - cnt * var - (M.stage_of(cnt)[1] + plan['add_fixed']) - acq
        cum += op; low = min(low, cum)
        if op < 0: neg = m
    return (neg + 1 + dm if neg < months else None), round(-low / 1e4, 1)
def fmt(r): return f"{M.ym(r[0]) if r[0] else '15년 안에 없음'} / {r[1]}억{' 통과' if OK(*r) else ' 미달'}"
a72, v72, _ = M.econ_G('하단 가정가'); VG = v72 - a72 * M.BAD
T2 = lambda **k: sim(M.plan_G(), k.pop('price', 92.0), VG, **k)
E_ = lambda **k: sim(M.plan_E(), k.pop('price', 80), 29, **k)
def thr(fn, key, vals):
    for x in vals:
        r = fn(**{key: x})
        if OK(*r): return x, fmt(r)
if __name__ == '__main__':
    print('기준 T2 92:', fmt(T2()), '| E 80:', fmt(E_()))
    print('1. 키 하나 문턱')
    print('  T2 가격', thr(T2, 'price', [x / 2 for x in range(170, 300)]))
    print('  T2 첫해 해지', thr(T2, 'ch1', [x / 1000 for x in range(35, 9, -1)][::-1][::-1] and [x / 1000 for x in range(35, 9, -1)]) )
    print('  T2 매달 신규', thr(T2, 'n', [3, 4, 5]))
    print('  E 가격', thr(E_, 'price', [x / 2 for x in range(160, 260)]))
    print('  E 첫해 해지', thr(E_, 'ch1', [x / 1000 for x in range(35, 9, -1)]))
    print('  E 이후 해지', thr(E_, 'ch', [x / 1000 for x in range(20, 4, -1)]))
    print('  E 매달 4곳', fmt(E_(n=4)))
    print('2. 조합')
    print('  4.1 T2 100 + 첫해 2.5% + 이후 1.5%:', fmt(T2(price=100, ch1=.025, ch=.015)), '| 이후 3%:', fmt(T2(price=100, ch1=.025, ch=.03)))
    print('  4.2 T2 92 + 매달 5곳 + 영업 75 + 첫해 2.5%:', fmt(T2(n=5, sales=75, ch1=.025)))
    print('  4.3 E 80 + 첫해 2.5% + 이후 1.5%:', fmt(E_(ch1=.025, ch=.015)))
    print('3. 매달 신규 + 4곳째부터 CAC 850')
    for n in (4, 5, 6): print(f'  {n}곳:', fmt(T2(n=n, sales_extra=850)))
