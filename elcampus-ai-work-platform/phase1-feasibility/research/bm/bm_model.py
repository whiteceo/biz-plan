# BM 조합별 재무 계산 (단위: 만 원). model_v6.py(검토 문서 5장 모델)를 그대로 쓰고 입력값만 바꾼다.
import sys, os
_here = os.path.dirname(os.path.abspath(__file__))
for _p in (os.path.join(_here, '..', '..', 'model'), '/mnt/project-files/reviews/round5'):  # 저장소 model/ 또는 공유 폴더
    if os.path.exists(os.path.join(_p, 'model_v6.py')): sys.path.insert(0, _p); break
from model_v6 import P, sim, ym, solve

BASE = dict(P)  # ARPU 80, 변동비 29, 온보딩 65, 해지 2%, 매달 3곳

def scen(level):
    """level: 0=낮게, 1=중간, 2=높게. 각 수익원의 가정값(추정)을 반환"""
    L = lambda a, b, c: (a, b, c)[level]
    s = {}
    # S1 서비스 결합: 일회성 매출(신규 1곳당)
    onb_fee = L(0.3, 0.5, 0.7) * 100                     # 월 계약 고객만 온보딩 100만 원 유상(연간 계약은 면제)
    custom = L(0.10, 0.20, 0.30) * 750 * L(0.30, 0.35, 0.40)  # 맞춤 구축 500~1,000만(중간 750) 채택률 × 마진(외주 수행)
    gov = L(0.10, 0.20, 0.30) * 300 * 0.5                 # AI 거버넌스 도입 컨설팅 300만(자리표시자) 채택률 × 마진 50%
    s['S1_onetime_gain'] = onb_fee + custom + gov
    s['S1_onetime_rev'] = onb_fee + L(0.10, 0.20, 0.30) * 750 + L(0.10, 0.20, 0.30) * 300
    # S2 AI 종량 재과금(포함형 선택) + 인프라 옵션
    ai_attach, ai_cost, ai_mk = L(0.3, 0.5, 0.7), 35, L(0.10, 0.20, 0.40)  # AI 원가 50인 14~65만 중 35만, 마크업
    s['ai_rev'] = ai_attach * ai_cost * (1 + ai_mk)
    s['ai_var'] = ai_attach * ai_cost + 0.02 * s['ai_rev']  # 미수·대손 2%
    inf_attach = L(0.1, 0.2, 0.3)
    s['inf_rev'], s['inf_var'] = inf_attach * 20, inf_attach * 9   # 전용 네트워크·장기 보관 등 옵션 월 20만, 원가 9만
    # S3 파트너 채널
    s['p_extra'] = L(0.5, 1.0, 2.0)          # 파트너가 데려오는 매달 추가 고객
    s['p_margin'] = L(0.30, 0.25, 0.20)      # 리셀러 마진(구독료의 %)
    s['p_fixed'] = L(650, 550, 300)          # 파트너 담당·자료 월 고정비(현금)
    return s

def build(name, level=1, N=3):
    s = scen(level); p = dict(BASE, N=N)
    arpu, var, onb = 80, 29, 65
    if name in ('S1', 'S2', 'S3'):
        onb = 65 - s['S1_onetime_gain']
    if name in ('S2', 'S3'):
        arpu += s['ai_rev'] + s['inf_rev']; var += s['ai_var'] + s['inf_var']
        p['once_cash'] += 200              # AI·클라우드 약관 법률 검토 추가
        p['dev_months'] += 0.5             # 사용량 집계·청구·한도 기능(약 1.5개월분 작업 ÷ 개발 2.0명분 ≈ 0.75 → 보수적으로 0.5개월 연장 + 나머지는 출시 후)
    if name == 'S3':
        tot = N + s['p_extra']
        arpu -= (s['p_extra'] / tot) * 80 * s['p_margin']   # 파트너 고객은 구독료의 마진만큼 덜 받음
        p['N'] = tot; p['fixed_cash'] += s['p_fixed']
    p.update(arpu=arpu, var=var, onb=onb)
    return p

def summary(p):
    a, b = sim(p, True), sim(p, False)
    dm = p['dev_months']
    st = lambda r: ym(r['pay'] + round(dm)) if r['pay'] else '출시 후 10년 안에 못 함'
    y3 = a['yr'][2]
    return dict(arpu=p['arpu'], cm=p['arpu'] - p['var'], onb=p['onb'],
                be_incl=a['be'], be_cash=b['be'], pay_incl=st(a), pay_cash=st(b),
                trough_incl=-a['trough'] / 1e4, trough_cash=-b['trough'] / 1e4,
                y3_margin_incl=y3['op'] / y3['rev'], y3_op_incl=y3['op'] / 1e4)

def need_cm(N, years, incl=True):
    """기본(S0) 대비 고객 1곳당 월 공헌이익을 얼마나 더 남겨야 착수 후 years년 안에 회수하나"""
    p = dict(BASE, N=N)
    def ok(q, i):
        r = sim(q, i); return r['pay'] is not None and r['pay'] + q['dev_months'] <= years * 12
    return solve(p, ok, incl) - 80

if __name__ == '__main__':
    LV = ['낮게', '중간', '높게']
    for nm in ('S0', 'S1', 'S2', 'S3'):
        for lv in (0, 1, 2):
            if nm == 'S0' and lv != 1: continue
            r = summary(build(nm, lv))
            print(f"{nm} {LV[lv]} | 월매출/곳 {r['arpu']:.1f} 공헌 {r['cm']:.1f} 온보딩순비용 {r['onb']:.1f} | "
                  f"월흑자(포함) {r['be_incl']} (현금) {r['be_cash']} | 회수 착수후 포함 {r['pay_incl']} / 현금 {r['pay_cash']} | "
                  f"최대적자 포함 {r['trough_incl']:.2f}억 현금 {r['trough_cash']:.2f}억 | 3년차 영업이익률(포함) {r['y3_margin_incl']:.0%} {r['y3_op_incl']:.2f}억")
    print('--- 회수 목표별 추가로 필요한 고객 1곳당 월 공헌이익(S0 대비, 만 원)')
    for N in (2, 3, 4):
        print(N, '곳 | 포함 5년', round(need_cm(N, 5)), '4년', round(need_cm(N, 4)), '| 현금 3년', round(need_cm(N, 3, False)), '2년', round(need_cm(N, 2, False)))
    print('--- 중간값 기준, 매달 신규별')
    for N in (2, 3, 4):
        for nm in ('S0', 'S1', 'S2', 'S3'):
            r = summary(build(nm, 1, N))
            print(N, nm, r['pay_incl'], '/', r['pay_cash'], f"최대적자 {r['trough_incl']:.2f}/{r['trough_cash']:.2f}")
