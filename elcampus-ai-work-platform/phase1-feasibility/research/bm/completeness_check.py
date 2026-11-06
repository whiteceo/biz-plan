# 레드팀 9장 완전성 보완 묶음 독립 재계산과 BM팀 조정안. 시뮬레이터는 레드팀 것과 따로 썼다(코호트별 첫해 해지, 15년).
# 단위 만 원/월. 기준 가정표: 매달 3곳(CAC 0 몫), 해지 2%, EXT 포함, 계산 기간 15년.
import sys, contextlib, io
sys.path.insert(0, '../product')
with contextlib.redirect_stdout(io.StringIO()):
    from round4 import PRICE, MIX, mixed, G, G_STEP, DEV
    from target import OPT, stage_of, ym, CAPEX_BASE, DEV_MONTHS
EXT = 2066 + 610
def sim(o, a, v, N=3, ch=.02, ch1=None, addF=0, sales=0, onb=65, wage=0, price=0, labor=0.8, months=180):
    """ch1: 가입 12개월 이내 코호트의 월 해지율. sales: 기존 채널 1곳당 별도 영업비. wage·price: 연 인상률.
    임금 인상은 고정비의 labor 비율과 변동비의 고객 지원 인건비 12만 원에만 적용(나머지는 고정)."""
    dm = DEV_MONTHS + o['add_dev']
    cum = -(CAPEX_BASE + o['add_once'] + (o['add_fixed'] + EXT) * o['add_dev']); low = cum
    co = []; last = 0; op = 0
    for m in range(1, months + 1):
        y = (m - 1) // 12; wf = (1 + wage) ** y; pf = (1 + price) ** y
        co = [(age + 1, c * (1 - (ch1 if (ch1 is not None and age < 12) else ch))) for age, c in co] + [(0, N)]
        n = sum(c for _, c in co)
        F0 = stage_of(n)[1] + o['add_fixed'] + addF
        F = F0 * (labor * wf + (1 - labor))
        vv = v + 12 * (wf - 1)
        op = n * a * pf - n * vv - F - N * (onb + sales) * wf
        cum += op; low = min(low, cum)
        if op < 0: last = m
    be = ym(last + 1 + dm) if last < months else '15년 안에 없음'
    return be, round(-low / 1e4, 1), round(op)
E1 = dict(OPT['E 현행 구상'], add_fixed=DEV)          # 현행 구상 + 운영·보안 1.0명(상품기획팀 라운드 4 공정 비교)
PV = [k for k in PRICE if k.startswith('가치가')][0]; PL = '하단 가정가'
CASES = {'현행 구상(E) + 운영 1.0명, 80만': (E1, 80, 29, 0),
         '그레이드 구조, 하단 가정가': (G,) + mixed(PRICE[PL], MIX['기본']),
         '그레이드 구조, 가치가': (G,) + mixed(PRICE[PV], MIX['기본']),
         '그레이드 단계 출시, 가치가': (G_STEP,) + mixed(PRICE[PV], (.55, .45, 0))}
RT = dict(addF=960, sales=150, onb_add=60, ch1=.035)           # 레드팀 묶음
# BM 조정안: CS·고객 성공 0.5명(250)은 변동비 안 '고객 지원 인건비 12만 원/곳'(검토 문서 3장, 지원 담당 신규 채용)과 중복 → 뺀다.
#   보험·사무 150 → 100(개인정보 배상책임보험은 사업 매출 규모상 연 수백만 원 수준으로 봄, 학습 지식·신뢰 2). 나머지는 유지.
BM = dict(addF=360 + 200 + 100, sales=150, onb_add=35, ch1=.035)  # 기준 가정표 5장: 도입 +35(+60은 범위)
def run_pk(o, a, v, g3, pk, **kw):
    return sim(o, a, v, onb=65 + g3 + pk.get('onb_add', 0), addF=pk.get('addF', 0), sales=pk.get('sales', 0), ch1=pk.get('ch1'), **kw)
if __name__ == '__main__':
    print('구조 | 기준 | 레드팀 묶음 | BM 조정안 | BM 조정안 + 임금 3%·가격 2% | BM 조정안 + 임금 3%·가격 3% | BM 조정안, 영업비 75')
    for k, (o, a, v, g3) in CASES.items():
        r = [run_pk(o, a, v, g3, {}), run_pk(o, a, v, g3, RT), run_pk(o, a, v, g3, BM),
             run_pk(o, a, v, g3, BM, wage=.03, price=.02), run_pk(o, a, v, g3, BM, wage=.03, price=.03), run_pk(o, a, v, g3, dict(BM, sales=75))]
        print(f"{k}({a}) | " + ' | '.join(f"{x[0]}({x[1]}억)" for x in r))
    print('--- 항목별 단독 영향(가치가 그레이드, 기준 대비)')
    o, a, v, g3 = CASES['그레이드 구조, 가치가']
    for lab, pk in [('사업 책임자 0.3명 360', dict(addF=360)), ('G&A 0.25명 200', dict(addF=200)), ('CS 0.5명 250', dict(addF=250)), ('보험·사무 100', dict(addF=100)),
                    ('영업비 150/곳', dict(sales=150)), ('도입 +35', dict(onb_add=35)), ('첫해 해지 3.5%', dict(ch1=.035))]:
        print(' ', lab, run_pk(o, a, v, g3, pk))
    print('--- BM 조정안에서 지속 흑자가 착수 후 7년 / 5년이 되는 월 매출/곳(가격·임금 고정, 가치가 믹스 비율 유지)')
    for k, (o, a, v, g3) in CASES.items():
        out = []
        for lim in (84, 60):
            for a10 in range(int(a * 10), 3000, 5):
                be = run_pk(o, a10 / 10, v, g3, BM)[0]
                if be != '15년 안에 없음':
                    y, mo = (int(be.split('년')[0]) if '년' in be else 0), (int(be.split('년')[-1].replace('개월', '').strip() or 0) if '개월' in be else 0)
                    if y * 12 + mo <= lim: out.append(f"{lim // 12}년 {a10 / 10}"); break
        print(' ', k, out)
