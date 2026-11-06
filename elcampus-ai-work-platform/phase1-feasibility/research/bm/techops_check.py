# 기술운영팀 산정(research/saas-build-ops-cost.md 9장, tech-ops/costcalc.py) 독립 재계산 + 19장 완전성 보완과 통합.
# 시뮬레이터: completeness_check.sim(코호트 첫해 해지, 15년). 입력값(가격·믹스·변동비·고정·개발·일회)은 costcalc에서 가져온다. 단위 만 원/월.
import sys, os, contextlib, io
sys.path.insert(0, '../tech-ops'); sys.path.insert(0, '../product')
with contextlib.redirect_stdout(io.StringIO()):
    import costcalc as C
    from completeness_check import sim
    from target import OPT, DEV
def plan(case, step):
    k = 1 if case == '기본' else 2 if case == '낮음' else 3
    return dict(add_fixed=C.fixed(case, step), add_dev=C.add_months(k, step), add_once=C.once(case, step), cac=850)
MIXES = {False: (.5, .45, .05), True: (.55, .45, 0)}
NAME = {False: '세 그레이드 동시(T3)', True: '단계 출시안(T2)'}
# 통합 보완 묶음: 19장 BM 조정안(사업 책임자 360 + G&A 200 + 보험·사무 100) 가운데 G&A는 기술운영팀의 수납 80·세무 30·법무 25(=135)와 겹쳐 잔여 65만 남김.
INT = dict(addF=360 + 65 + 100, sales=150, onb_add=60, ch1=.035)
def r(o, a, v, g3, pk=None, **kw):
    pk = pk or {}
    return sim(o, a, v, onb=65 + g3 + pk.get('onb_add', 0), addF=pk.get('addF', 0), sales=pk.get('sales', 0), ch1=pk.get('ch1'), **kw)
if __name__ == '__main__':
    print('가격 | 안 | 산정 | 고정/개발/일회 | 기술운영 값만(기본) | 스트레스(해지 3%·변동 23·AI 6) | + 19장 통합 보완 | 통합 + 임금 3%·가격 3%')
    for price in ('가치가', '하단 가정가'):
        for step in (True, False):
            for case in ('기본', '낮음', '높음'):
                o = plan(case, step)
                a, v, g3, _ = C.econ(C.PRICE[price], case, MIXES[step])
                a2, v2, _, _ = C.econ(C.PRICE[price], case, MIXES[step], ai=6, v1=23)
                x = [r(o, a, v, g3), r(o, a2, v2, g3, ch=.03), r(o, a, v, g3, INT), r(o, a, v, g3, INT, wage=.03, price=.03)]
                print(f"{price} | {NAME[step]} | {case} | {o['add_fixed']:.0f}/{o['add_dev']}/{o['add_once']} | " + ' | '.join(f"{y[0]}({y[1]}억)" for y in x))
    print('=== 현행 구상(E) 같은 기준: 공통 누락분(수납 80·세무 30·법무 25·외부 점검 42, 대손 1%, 개발 +1, 일회 1,000) + 18.2 ①(자동화 +2개월, 운영·보안 0.5명, 도구 100)')
    E = OPT['E 현행 구상']
    Ef = dict(E, add_fixed=177 + 0.5 * DEV + 100, add_dev=3, add_once=1000)
    for lab, o, v in (('검토 문서 값 + 대손 1%', E, 29.8), ('+ 공통 누락분', dict(E, add_fixed=177, add_dev=1, add_once=1000), 29.8), ('+ 18.2 ①', Ef, 29.8)):
        x = [r(o, 80, v, 0), r(o, 80, v, 0, ch=.03), r(o, 80, v, 0, INT), r(o, 80, v, 0, INT, wage=.03, price=.03)]
        print('  ' + lab + ': ' + ' | '.join(f"{y[0]}({y[1]}억)" for y in x))
    print('=== 통합 보완에서 지속 흑자 착수 후 5년이 되는 가치가 배수(단계 출시안 T2, 기본 산정)')
    o = plan('기본', True)
    for k in range(100, 200):
        t = {g: (p1 * k / 100, p2 * k / 100) for g, (p1, p2) in C.PRICE['가치가'].items()}
        a, v, g3, _ = C.econ(t, '기본', MIXES[True]); be = r(o, a, v, g3, INT)[0]
        if be != '15년 안에 없음' and ('년' not in be or int(be.split('년')[0]) * 12 + (int(be.split('년')[1].replace('개월', '').strip() or 0)) <= 60):
            print(f"  × {k/100:.2f} → 고객 1곳 월 {a}만 원: {be}"); break
