# 15장: 후보 D(조직 AI 업무 플랫폼)와 D+(D + 안전관리 부가 기능). 단위 만 원, 사내 인력 포함 기준. 모든 가정은 자리표시자.
import math
from bm_model import BASE, sim, ym
CAC = 850
def run(name, arpu=0, var=0, fixed=0, dev=0, once=0, N=3):
    p = dict(BASE, arpu=80+arpu, var=29+var, dev_months=9+dev, N=N,
             fixed_cash=BASE['fixed_cash']+fixed, once_cash=BASE['once_cash']+once)
    a = sim(p, True); b = sim(p, False); dm = round(p['dev_months'])
    F = 3473.5 + fixed
    cm0 = p['arpu']-p['var']-p['churn']*65; cm8 = p['arpu']-p['var']-p['churn']*(CAC+65)
    r = dict(name=name, arpu=p['arpu'], cm=p['arpu']-p['var'], gm=(p['arpu']-p['var'])/p['arpu'], F=F,
             be0=math.ceil(F/cm0), be8=math.ceil(F/cm8),
             pay=ym(a['pay']+dm) if a['pay'] else '못 함', payc=ym(b['pay']+dm) if b['pay'] else '못 함',
             tr=-a['trough']/1e4, trc=-b['trough']/1e4)
    print(f"{name} | 매출 {r['arpu']:.1f} 공헌 {r['cm']:.1f} GM {r['gm']:.0%} | 고정비 {F:,.0f} | BE {r['be0']}/{r['be8']} | 회수 {r['pay']} / {r['payc']} | 적자 {r['tr']:.1f}/{r['trc']:.1f}억")
    return r
# D: AI 맥락 공유 계층(권한별 검색, 프로젝트·요청 맥락, 조직 지식) 개발·운영 인력 +1.5명, 개발 +3개월, 고객당 AI 원가(임베딩·검색·요약) 월 +5만
D = dict(fixed=1.5*775, dev=3, var=5, once=500)   # once: 보안 점검(권한 경계) 500
run('E 현행(S0)')
run('D 가격 그대로', **D)
for up in (10, 20, 30):
    run(f'D ARPU +{up}', **dict(D, arpu=up))
# D+: 안전관리 부가 기능. 기본형(TBM 기록·위험요인/아차사고 신고→조치 요청·교육 이력)은 플랫폼에 포함, AI 애드온(위험성평가 초안·법령 질의·이행 점검 보고서) 월 15만 채택 50%
# 협회 전문가 0.5명분 300, 콘텐츠·법률 검토 1,000, 개발 +2(맥락 계층과 일부 겹친다고 보고 2.5 → 2)
def Dp(arpu_up=0, att=0.5, price=15, N=3):
    return dict(fixed=D['fixed']+300, dev=D['dev']+2, var=D['var']+att*7, once=D['once']+1000, arpu=arpu_up+att*price, N=N)
for N in (3, 4, 5):
    run(f'D+ 가격 그대로 N={N}', **Dp(N=N))
    run(f'D+ ARPU +20 N={N}', **Dp(arpu_up=20, N=N))
# 기준선과 비교용: E(S0) N=4,5
for N in (4, 5): run(f'E 현행 N={N}', N=N)
# 손익분기를 S0(70곳)로 유지하려면 D의 ARPU 상승폭
F = 3473.5+1162.5; print('D 손익분기 70곳 유지 ARPU 상승', round(F/70 + 29+5 + 1.3 - 80, 1))
# D+ + AI 운영 대행(시장조사팀 4장: 고객 명의 좌석 + 관리 수수료 1인 월 0.7~1.0만, 재판매 마진 0). 40석 × 0.85만 채택 30%, 마진 50%, 담당 1명 600
for N in (3, 4):
    x = Dp(arpu_up=20, N=N); x['arpu'] += 0.3*34; x['var'] += 0.3*34*0.5; x['fixed'] += 600
    run(f'D+ ARPU +20 + 운영 대행 N={N}', **x)
# 시나리오(white 2026-11-05 '소설 금지'): 결론은 기본 기준. 해지율 벤치마크: 중소기업 대상 SaaS 월 3~7%(학습 지식, 신뢰 3) → 2%는 범위 밖(낙관 쪽)
def run_s(name, up, att, N, ch):
    x = Dp(arpu_up=up, att=att, N=N)
    p_ch = ch
    import bm_model
    old = dict(bm_model.BASE); bm_model.BASE['churn'] = p_ch; BASE['churn'] = p_ch
    r = run(name + f' (인상 +{up}, 애드온 채택 {att:.0%}, 매달 {N}곳, 해지 {ch:.0%})', **x)
    bm_model.BASE.update(old); BASE.update(old); return r
print('=== D+ 시나리오')
run_s('낙관', 20, 0.5, 4, 0.02)
run_s('기본', 10, 0.3, 3, 0.02)
run_s('기본(해지 벤치마크 하단)', 10, 0.3, 3, 0.03)
run_s('보수', 0, 0.2, 2, 0.03)
def run_e(ch, N=3):
    import bm_model
    old = dict(bm_model.BASE); bm_model.BASE['churn'] = ch; BASE['churn'] = ch
    r = run(f'E 현행 (매달 {N}곳, 해지 {ch:.0%})', N=N); bm_model.BASE.update(old); BASE.update(old); return r
run_e(0.03); run_e(0.03, 2)
