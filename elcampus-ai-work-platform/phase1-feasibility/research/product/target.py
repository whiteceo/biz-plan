# 상품안별 재무(사내 인력 포함 월 흑자·회수·최대 적자). 단위 만 원/월.
# white님 희망 수준(월 매출 2억 원, 영업이익률 10%)은 참고 열로만 계산한다. 역산 목표로 쓰지 않는다(white 2026-11-05).
# CAC 정의: reverse2.py와 같이 매달 3곳까지(기존 채널)는 온보딩 비용만, 그 이상은 1곳당 CAC. 검토 문서 5장·BM 15장(model_v6)은 매달 N곳 모두 CAC 없음.
# 한계: 고객 200곳까지 Stage 1 조직(영업·CS 리더 없음)을 유지한다(reverse2.py 가정).
# 기반: research/bm/reverse2.py의 조직 단계·단가·CAPEX를 그대로 쓰고 상품안별 입력값만 바꾼다. 모든 상품 입력값은 자리표시자.
import math
DEV, UX, PM = 775, 516, 610
OTHER1 = 797.5
STAGE = {  # 고객 상한, 사내 인력 포함 월 고정비(reverse2.py 출력: 3,474 / 8,656 / 16,650)
 1: (200, 3473.5), 2: (1000, 8656), 3: (10**9, 16650)}
CAPEX_BASE = 27965          # 출시 전 투자(사내 인력 포함), 검토 문서 3.10
EXT = 2066 + 610            # 개발이 늘어나는 달마다 기존 사내 개발·UIX(2,066)와 PM(610)도 계속 든다(BM 스레드 지적, 2026-11-05)
DEV_MONTHS = 9
CH = 0.02; ONB = 65
TARGET_REV, TARGET_MARGIN = 20000, 0.10

def stage_of(n):
    for s, (cap, F) in STAGE.items():
        if n <= cap: return s, F

OPT = {  # 주의: 여기 arpu는 상품안의 낙관(상단) 가격이다. 기본(중간) 가격은 scen.py의 SC를 쓴다(레드팀 R1).
 # name: arpu, var(고객당 월 변동비), add_fixed(조직 위에 더하는 월 고정비), add_dev(개발 개월 추가), add_once(일회 투자 추가), cac(기존 채널 밖 신규 1곳), base_free(기존 채널 월 유치, CAC 없이 온보딩만)
 'E 현행 구상': dict(arpu=80, var=29, add_fixed=0, add_dev=0, add_once=0, cac=850),
 'B 조직 AI 업무 플랫폼 + 안전 기본형(D+)': dict(arpu=107.5, var=37.5, add_fixed=1.5*DEV+300, add_dev=5, add_once=1500, cac=850),
 'C 현장·사무 통합 플랫폼(현장형)': dict(arpu=125, var=44, add_fixed=2.0*DEV+300+600, add_dev=6, add_once=1800, cac=850),
 'D 현장형 + 100~299인 확장': dict(arpu=174, var=55.5, add_fixed=2.0*DEV+300+600+1200, add_dev=6, add_once=1800, cac=1012),
}
# A 서비스형(플랫폼 없음)은 구조가 달라 아래 별도 계산.

def run(o, N, months=180, base_free=3, churn=CH, arpu=None):
    a = arpu or o['arpu']; dm = DEV_MONTHS + o['add_dev']
    cum = -(CAPEX_BASE + o['add_once'] + (o['add_fixed'] + EXT) * o['add_dev']); low = cum
    n = 0; be = hit = pay = None; last_neg = 0; info = None
    for m in range(1, months + 1):
        n = n * (1 - churn) + N
        s, F = stage_of(n); F += o['add_fixed']
        rev = n * a
        op = rev - n * o['var'] - F - N * ONB - max(0, N - base_free) * o['cac']
        cum += op; low = min(low, cum)
        if op < 0: last_neg = m
        ok = rev >= TARGET_REV and op >= TARGET_MARGIN * rev
        if ok and hit is None: hit = m; info = dict(n=round(n), stage=s, F=round(F), op=round(op), rev=round(rev))
        if not ok: hit = None; info = None   # 이후 다시 깨지면 지속 도달로 보지 않음
        if pay is None and cum >= 0: pay = m
    be = last_neg + 1 if last_neg < months else None
    f = lambda x: (x + dm) if x else None
    return dict(be=f(be), hit=f(hit), pay=f(pay), low=round(-low / 1e4, 1), info=info, ss=round(N / churn))

def ym(m):
    if m is None: return '–'
    y, mm = divmod(m, 12); return f"{y}년 {mm}개월" if y and mm else (f"{y}년" if y else f"{mm}개월")

if __name__ == '__main__':
    for k, o in OPT.items():
        print(f"\n## {k} | 월 매출/곳 {o['arpu']}")
        for N in (3, 4, 5, 6, 8, 10, 15):
            r = run(o, N)
            i = r['info']
            print(f"  매달 {N}곳(정상상태 {r['ss']}곳): 월 흑자 {ym(r['be'])} · 회수 {ym(r['pay'])} · 최대 누적 적자 {r['low']}억 · 참고: 희망 수준 지속 도달 {ym(r['hit'])}")
    print('\n## 해지율 민감도(C, 매달 6곳): 1% / 1.5% / 2% / 3%')
    for ch in (0.01, 0.015, 0.02, 0.03):
        r = run(OPT['C 현장·사무 통합 플랫폼(현장형)'], 6, churn=ch); print(f"  {ch:.1%}: 참고 희망 수준 {ym(r['hit'])}, 흑자 {ym(r['be'])}, 적자 {r['low']}억")

# ---- 추가: 가격 하단 경우와 A 서비스형 ----
LOW = {'B 조직 AI 업무 플랫폼 + 안전 기본형(D+)': 87.5,   # 플랫폼 인상 없이 애드온만(BM 15.4)
       'C 현장·사무 통합 플랫폼(현장형)': 107.5,          # 현장 좌석 0.5만 원(세이프로 1인 5,000원 기준)
       'D 현장형 + 100~299인 확장': 140}                  # 100~299인 비중 15%
def table():
    print('\n## 비교표(사내 인력 포함): 상품안 × 가격 × 매달 유치')
    for k, o in OPT.items():
        for a in ([o['arpu']] + ([LOW[k]] if k in LOW else [])):
            for N in (3, 4, 6):
                r = run(o, N, arpu=a)
                print(f"{k} | ARPU {a} | 매달 {N} | 월 흑자 {ym(r['be'])} | 회수 {ym(r['pay'])} | 최대 적자 {r['low']}억 | 참고: 희망 수준 {ym(r['hit'])}")
# A 서비스형: 플랫폼 개발 없음. 컨설턴트 1명당 운영 40곳은 [가정](비교: 검토 문서 3.7 지원 1명당 30~60곳, Gainsight 2022 저접촉 144곳). 고객 명의 공급사 좌석 + 도입 컨설팅(일회) + 운영 대행(월). 모든 값 가정.
def service(N, seats=15, fee=1.0, consult=300, months=120):
    # 컨설턴트 1명 월 600, 1명이 운영 고객 40곳 + 월 신규 2곳 도입 처리(가정). PM 0.5명분 305, 마케팅·도구 100.
    n = 0; cum = -500; low = cum; be = None; last_neg = 0; pay = None
    for m in range(1, months + 1):
        n = n * (1 - CH) + N
        cons = max(1, math.ceil(max(n / 40, N / 2)))
        rev = n * seats * fee + N * consult
        op = rev - cons * 600 - 305 - 100 - N * consult * 0.2 - max(0, N - 3) * 300
        cum += op; low = min(low, cum)
        if op < 0: last_neg = m
        if pay is None and cum >= 0: pay = m
    return dict(be=last_neg + 1 if last_neg < months else None, pay=pay, low=round(-low/1e4, 2), n=round(n), rev=round(rev), op=round(op))
if __name__ == '__main__':
    table()
    print('\n## A 서비스형(개발 없음): 매달 유치별, 10년 뒤 고객·월 매출·월 영업이익')
    for N in (2, 3, 4, 6, 10):
        r = service(N); print(f"  매달 {N}: 월 흑자 {ym(r['be'])} · 회수 {ym(r['pay'])} · 최대 적자 {r['low']}억 · 10년 뒤 {r['n']}곳, 월 매출 {r['rev']:,}, 영업이익 {r['op']:,}")
    print('  참고: 월 매출 2억 원에 필요한 고객(월 대행료 15만 원 기준)', math.ceil(20000/15), '곳')
if __name__ == '__main__':
    E = run(OPT['E 현행 구상'], 4)
    print('\n## 매달 4곳에서 월 흑자 시점과 회수가 모두 E 이상이 되는 월 매출/곳')
    for k in list(OPT)[1:]:
        for a10 in range(800, 3000, 5):
            a = a10 / 10; r = run(OPT[k], 4, arpu=a)
            if r['pay'] and r['pay'] <= E['pay'] and r['be'] and r['be'] <= E['be']:
                print(f"  {k}: {a} (흑자 {ym(r['be'])}, 회수 {ym(r['pay'])}, 적자 {r['low']}억)"); break
