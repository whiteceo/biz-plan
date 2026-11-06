# 라운드 4 보완(2026-11-06): 레드팀 9장 완전성 보완 묶음 위에 상품팀 조정을 얹는다. 기준 함수는 레드팀 redteam-completeness.py의 sim과 같은 구조.
# 상품팀 조정 [가정]: (1) 표준 도입 범위를 "방문 1회 + 원격 4주"로 줄여 도입 +35(레드팀 +60), 8주 현장 정착은 유료 패키지(서비스 매출, 마진 0으로 둠)
#   (2) 60일 유료 파일럿(정가 50%): 전환율 60% → 계약 1곳당 파일럿 1.67곳, 파일럿 매출 = 1.67 × 월 가격, 미전환 0.67곳의 영업·도입 비용은 손실
#   (3) 확장 매출: 1년 넘은 고객의 매출이 연 5% 증가(G1→G2 업셀, 인원 구간 상향) → NRR 약 83%(해지 2% 기준)
#   (4) 가격 연 1회 조정 조항(12.9): 임금 3%·가격 3%를 실질 기준과 같은 결과로 본다.
from round4 import *
from target import EXT, CAPEX_BASE, DEV_MONTHS, stage_of, OPT
def sim(o, N, a, v, ch, wage=0, price=0, addF=0, ch1=None, months=180, onb=65, pilot=None, sales=0, exp=0, shock=None):
    dm = DEV_MONTHS + o['add_dev']; cum = -(CAPEX_BASE + o['add_once'] + (o['add_fixed'] + EXT) * o['add_dev']); low = cum
    co = []; last = 0
    for m in range(1, months + 1):
        y = (m - 1) // 12
        c_ch = ch if not (shock and m > shock[0]) else shock[1]
        pr = a * (1 + price) ** y * (1 - (shock[2] if shock and m > shock[0] else 0))
        co = [(g + 1, c * (1 - (ch1 if (ch1 and g < 12) else c_ch)), r * ((1 + exp) ** (1 / 12) if g >= 12 else 1)) for g, c, r in co] + [(0, N, 1.0)]
        n = sum(c for _, c, _ in co); rev = sum(c * r for _, c, r in co) * pr
        s, F = stage_of(n); F = (F + o['add_fixed'] + addF) * (1 + wage) ** y
        acq = N * (onb + sales)
        if pilot:  # 전환율 p: 파일럿 N/p곳, 매출 N/p × 월 가격(2개월 × 50%), 미전환분 영업·도입 손실
            p = pilot; acq = N / p * (onb + sales); rev += N / p * pr
        op = rev - n * v - F - acq; cum += op; low = min(low, cum)
        if op < 0: last = m
    return (ym(last + 1 + dm) if last < months else '15년 안에 없음'), round(-low / 1e4, 1), round(op)
P = '가치가(자리표시자)'
cases = {'현행 구상(E) + 운영 1.0명, 80만': (dict(OPT['E 현행 구상'], add_fixed=DEV), 80, 29, 0),
         '그레이드 구조, 하단 가정가': (G,) + mixed(PRICE['하단 가정가'], MIX['기본']),
         '그레이드 구조, 가치가[자리표시자]': (G,) + mixed(PRICE[P], MIX['기본'])}
RT = dict(addF=960, ch1=.035)
if __name__ == '__main__':
    print('구조 | 레드팀 보완 | +도입 범위 축소(+35) | +유료 파일럿(전환 60%) | +확장 연 5% | +임금·가격 3% | 참고: 공급사 무료 기능 충격(4년 차부터 해지 3%, 가격 -15%)')
    for k, (o, a, v, g3) in cases.items():
        rt = sim(o, 3, a, v, .02, onb=65 + 60 + g3, sales=150, **RT)
        s1 = sim(o, 3, a, v, .02, onb=65 + 35 + g3, sales=150, **RT)
        s2 = sim(o, 3, a, v, .02, onb=65 + 35 + g3, sales=150, pilot=.6, **RT)
        s3 = sim(o, 3, a, v, .02, onb=65 + 35 + g3, sales=150, pilot=.6, exp=.05, **RT)
        s4 = sim(o, 3, a, v, .02, onb=65 + 35 + g3, sales=150, pilot=.6, exp=.05, wage=.03, price=.03, **RT)
        s5 = sim(o, 3, a, v, .02, onb=65 + 35 + g3, sales=150, pilot=.6, exp=.05, wage=.03, price=.03, shock=(48, .03, .15), **RT)
        print(k, '|', ' | '.join(f"{x[0]}/{x[1]}억" for x in (rt, s1, s2, s3, s4, s5)))
    print('\n파일럿 전환율 민감도(그레이드 가치가, 조정 전부 적용):', ' · '.join(f"{p:.0%} {sim(G, 3, *mixed(PRICE[P], MIX['기본'])[:2], .02, onb=65 + 35 + 5, sales=150, pilot=p, exp=.05, wage=.03, price=.03, **RT)[0]}" for p in (.3, .45, .6, .8)))
    print('영업비 민감도(같은 조건):', ' · '.join(f"{sv}만 {sim(G, 3, *mixed(PRICE[P], MIX['기본'])[:2], .02, onb=65 + 35 + 5, sales=sv, pilot=.6, exp=.05, wage=.03, price=.03, **RT)[0]}" for sv in (75, 150, 200)))
