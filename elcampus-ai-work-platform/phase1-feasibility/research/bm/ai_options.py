# AI 부분 대안 3가지 (단위 만 원). 기본은 S0(구독 80, 변동비 29). 모두 자리표시자 가정, 사내 인력 포함 기준.
import math
from bm_model import BASE, sim, ym
CAC = 850
def be_n(cm, F): return math.ceil(F / cm)
OPTS = {
 'S0 기준(BYOK)': dict(arpu=0, var=0, fixed=0, onb=0, dev=0, once=0),
 '1 범용 AI 콘솔 자체 개발': dict(arpu=0.3*40*2.0, var=0.3*40*0.8 + 2, fixed=4.5*775, onb=0, dev=3, once=800),   # 채택 30%, 40좌석, 좌석 2.0만(앵커 2.0~2.8만 아래), AI 원가 좌석 0.8만, 지원 +2. 인력 +4.5명(프론트·백엔드·AI·모바일·보안), 보안 점검 +800
 '2 서비스형(좌석제 대행)': dict(arpu=0.3*25, var=0.3*25*0.5, fixed=600, onb=-(0.3*300*0.5), dev=0, once=0),       # 정착 지원 월 25만 채택 30%(마진 50%), 도입 컨설팅 300만 채택 30%(마진 50%), 컨설턴트 1명
 '3 업종 특화형(안전보건 AI)': dict(arpu=0.5*15, var=0.5*(5+2), fixed=300, onb=0, dev=2.5, once=1000),          # 모듈 월 15만(국내 안전관리 SaaS 월 5~15만 앵커) 채택 50%, AI 원가 5만+지원 2만, 협회 전문가 0.5명분, 콘텐츠·법률 검토 1,000만
}
for k, o in OPTS.items():
    p = dict(BASE, arpu=80 + o['arpu'], var=29 + o['var'], onb=65 + o['onb'], dev_months=9 + o['dev'],
             fixed_cash=BASE['fixed_cash'] + o['fixed'], once_cash=BASE['once_cash'] + o['once'])
    a = sim(p, True); b = sim(p, False); dm = round(p['dev_months'])
    F = BASE['fixed_cash'] + BASE['pm'] + 2066 + o['fixed']
    cm0 = p['arpu'] - p['var'] - 0.02 * (0 + 65); cm8 = p['arpu'] - p['var'] - 0.02 * (CAC + 65)
    gm = (p['arpu'] - p['var']) / p['arpu']
    print(f"{k} | 월 매출/곳 {p['arpu']:.1f} 공헌 {p['arpu']-p['var']:.1f} GM {gm:.0%} | 고정비(포함) {F:,.0f} | 손익분기 기존채널 {be_n(cm0,F)}곳 / CAC850 {be_n(cm8,F)}곳 | 회수 포함 {ym(a['pay']+dm) if a['pay'] else '못 함'} 현금 {ym(b['pay']+dm) if b['pay'] else '못 함'} | 최대적자 {-a['trough']/1e4:.1f}/{-b['trough']/1e4:.1f}억 | 개발 {p['dev_months']}개월")
# 민감도: 특화형 채택 30/50/70%, 가격 20/30/50
for att in (0.3, 0.5, 0.7):
    for pr in (10, 15, 20, 30):
        p = dict(BASE, arpu=80 + att*pr, var=29 + att*7, dev_months=11.5, fixed_cash=BASE['fixed_cash']+300, once_cash=BASE['once_cash']+1000)
        a = sim(p, True); print('특화형 채택', att, '가격', pr, ym(a['pay']+12) if a['pay'] else '못 함', 'BE', be_n(p['arpu']-p['var']-1.3, 3473.5+300))
# 콘솔: 채택 60%에도
for att in (0.3, 0.6, 0.9):
    p = dict(BASE, arpu=80 + att*80, var=29 + att*32 + 2, dev_months=12, fixed_cash=BASE['fixed_cash']+3487.5, once_cash=BASE['once_cash']+800)
    a = sim(p, True); print('콘솔 채택', att, ym(a['pay']+12) if a['pay'] else '못 함', 'BE', be_n(p['arpu']-p['var']-1.3, 3473.5+3487.5))
