# 상품기획팀 반복 라운드 4(product/round4.py) 독립 재계산 + 현행 구상(E) 공정 비교. 시뮬레이터 growth.run(고정 유치), 입력은 round4에서 가져온다.
# 기준 가정표: 매달 3곳까지 CAC 0, 해지 2%, EXT 포함. 스트레스 = 해지 3% + 공용 변동비 23 + AI 6. 보수 = 스트레스 + 매달 2곳. 단위 만 원/월.
import sys, contextlib, io
sys.path.insert(0, '../product')
with contextlib.redirect_stdout(io.StringIO()):
    from growth import run, ym, OPT
    from round4 import PRICE, MIX, mixed, G, G_STEP, G_LOW, AI_S, DEV, G3_ONCE, G3_OPS, FIX
FLAT = lambda t: 0.0
SC = {'기본': (3, .02, {}), '스트레스': (3, .03, dict(ai=AI_S, v1=23)), '보수': (2, .03, dict(ai=AI_S, v1=23))}
def go(o, a, v, N, ch, onb=65): return run(dict(o, arpu=a, var=v), FLAT, floor=N, churn=ch, free=3, onb=onb)
print('가격 | 믹스 | 기본 흑자(적자) | 스트레스 | 보수')
for pk, tab in PRICE.items():
    for mk, mix in list(MIX.items()) + [('단계 출시 55:45:0', (.55, .45, 0))]:
        o = G_STEP if mk.startswith('단계') else G
        out = []
        for sn, (N, ch, kw) in SC.items():
            a, v, g3 = mixed(tab, mix, **kw); r = go(o, a, v, N, ch, onb=65 + g3)
            out.append(f"{ym(r['be'])}({r['low']}억)")
        print(pk, '|', mk, f'({mixed(tab, mix)[0]})', '|', ' | '.join(out))
print('=== 운영·보안 인력과 개발 개월 민감도: 가치가 기본 믹스, 기본 시나리오')
a, v, g3 = mixed(PRICE['가치가'], MIX['기본'])
for lab, o in [('산정 그대로(1.0명, +8개월)', G), ('운영·보안 0.5명', dict(G, add_fixed=G['add_fixed'] - 0.5 * DEV)), ('운영·보안 2.0명(당직 2명)', dict(G, add_fixed=G['add_fixed'] + DEV)),
               ('개발 +5개월', dict(G, add_dev=5)), ('개발 +11개월', dict(G, add_dev=11)), ('MSP 월정액 중복분 −200 가정', dict(G, add_fixed=G['add_fixed'] - 200))]:
    r = go(o, a, v, 3, .02, onb=65 + g3); print(f"  {lab}: {ym(r['be'])}, 적자 {r['low']}억")
print('=== 현행 구상(E) 공정 비교: 고객별 전용 환경 운영 관리 비용을 같은 기준으로 넣음 (80만, 기본·스트레스(해지 3%)·보수(2곳, 3%))')
E = OPT['E 현행 구상']
# 검토 문서 3장: E 변동비 29 = 전용 서버·DB 10 + 보안·통제 3 + MSP 고객별 관리비 4 + 고객 지원 12. 고정비에 MSP 월정액 150 포함. 따라서 E의 고객별 운영은 일부(4만) 이미 들어 있다.
CASES = [
 ('E 검토 문서 값', E, 29, 65),
 ('① 개설·배포 자동화 개발 +2개월 + 운영 도구 100 + 운영·보안 0.5명(MSP 감독·당직)', dict(E, add_fixed=0.5 * DEV + 100, add_dev=2), 29, 65),
 ('② ① + 운영·보안 1.0명(라운드 4와 같은 인력)', dict(E, add_fixed=DEV + 100, add_dev=2), 29, 65),
 ('③ ② + 고객별 운영 부족분 8.5(12.5 − MSP 4) + 개설 100', dict(E, add_fixed=DEV + 100, add_dev=2), 29 + 8.5, 65 + G3_ONCE),
 ('④ ③ + ISMS(준비·심사 3,000, 유지 83)', dict(E, add_fixed=DEV + 100 + 83, add_dev=2, add_once=3000), 29 + 8.5, 65 + G3_ONCE),
]
for lab, o, v, ob in CASES:
    rs = [go(o, 80, v, 3, .02, ob), go(o, 80, v, 3, .03, ob), go(o, 80, v, 2, .03, ob)]
    print(f"  {lab}: " + ' | '.join(f"{ym(r['be'])}({r['low']}억)" for r in rs))
print('  E 공정판 ②가 3년 6개월이 되는 월 매출/곳:')
o, v, ob = CASES[2][1], CASES[2][2], CASES[2][3]
base = go(OPT['E 현행 구상'], 80, 29, 3, .02)['be']
for a10 in range(800, 2000, 5):
    if go(o, a10 / 10, v, 3, .02, ob)['be'] <= base: print('   ', a10 / 10); break
print('=== 연 계약 조건(상품기획팀 12.9: 연 계약 60%, 할인 15%, 해지 2% → 1.5%). 결제 수수료는 할인 뒤 매출 기준 2.5%')
for pk in PRICE:
    for mk, mix, o in (('기본', MIX['기본'], G), ('단계 출시', (.55, .45, 0), G_STEP)):
        a, v, g3 = mixed(PRICE[pk], mix); f = 1 - .6 * .15; a2 = round(a * f, 1); v2 = round(v - a * (1 - f) * 0.025, 1)
        r0 = go(o, a, v, 3, .02, 65 + g3); r1 = go(o, a2, v2, 3, .02, 65 + g3); r2 = go(o, a2, v2, 3, .015, 65 + g3); r3 = go(o, a2, v2, 3, .025, 65 + g3)
        print(f"  {pk} {mk}: 월 정가 {a} → {a2} | 연 계약 없음 {ym(r0['be'])}({r0['low']}억) | 할인만(해지 2%) {ym(r1['be'])}({r1['low']}억) | 할인 + 해지 1.5% {ym(r2['be'])}({r2['low']}억) | 할인 + 해지 2.5% {ym(r3['be'])}")
