# 상품기획팀 반복 라운드 3(product/round3.py) 독립 재계산. 시뮬레이터는 growth.run(BM 쪽 구현), 입력값만 round3에서 가져온다.
# 기준 가정표: 고정 유치, 매달 3곳까지 CAC 0, 해지 2%, 개발 연장 EXT 포함. 단위 만 원/월.
import sys, contextlib, io
sys.path.insert(0, '../product')
with contextlib.redirect_stdout(io.StringIO()):
    from growth import run, ym, OPT
    from round3 import F_OPT, F_SC, DEV
FLAT = lambda t: 0.0
def go(o, a, v, N, ch, **kw):
    r = run(dict(o, arpu=a, var=v), FLAT, floor=N, churn=ch, free=3, **kw)
    return r
rows = {'E 현행 구상': (OPT['E 현행 구상'], {'기본': (80, 29, 3, .02), '스트레스': (80, 29, 3, .03), '보수': (80, 29, 2, .03), '낙관': (80, 29, 4, .02)})}
for k in F_OPT: rows[k] = (F_OPT[k], F_SC[k])
print('상품안 | 시나리오 | 매출/곳 | 변동비 | 매달 | 해지 | 지속 월 흑자 | 그때 고객 | 회수(참고) | 최대 적자')
for k, (o, sc) in rows.items():
    for sn in ('낙관', '기본', '스트레스', '보수'):
        a, v, N, ch = sc[sn]; r = go(o, a, v, N, ch)
        print(f"{k} | {sn} | {a} | {v} | {N} | {ch:.0%} | {ym(r['be'])} | {r['n_be']} | {ym(r['pay'])} | {r['low']}억")
print('--- 검토 지점 민감도(기본 시나리오, 지속 월 흑자 / 최대 적자)')
for k in F_OPT:
    o = F_OPT[k]; a, v, N, ch = F_SC[k]['기본']
    out = []
    out.append(('공용형 변동비 17→23(인프라 절감 절반)', go(o, a, v + 6, N, ch)))
    out.append(('AI 원가 3→6', go(o, a, v + 3, N, ch)))
    if k != 'F0 현행 공용형':
        out.append(('AI 맥락 인력 0.5→1.5명분', go(dict(o, add_fixed=o['add_fixed'] + DEV), a, v, N, ch)))
    out.append(('공용형 전환 개발 +2→+5개월', go(dict(o, add_dev=o['add_dev'] + 3), a, v, N, ch)))
    out.append(('운영·보안 1명 추가(멀티테넌트 격리)', go(dict(o, add_fixed=o['add_fixed'] + DEV), a, v, N, ch)))
    out.append(('위 다섯 개 동시', go(dict(o, add_fixed=o['add_fixed'] + (2 if k != 'F0 현행 공용형' else 1) * DEV, add_dev=o['add_dev'] + 3), a, v + 9, N, ch)))
    print(k, ' | '.join(f"{n}: {ym(r['be'])}/{r['low']}억" for n, r in out))
