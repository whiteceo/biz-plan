from bm_model import *
# 1) 유상화로 전환이 줄면: S1 중간이 S0(매달 3곳)과 같아지는 매달 신규
base = sim(dict(BASE), True)['pay']
for N in (3, 2.8, 2.6, 2.5, 2.4, 2.2):
    p = build('S1', 1, N); r = sim(p, True); c = sim(p, False)
    print('S1 중간 N', N, ym(r['pay'] + 9) if r['pay'] else '-', ym(c['pay'] + 9))
for N in (3, 2.8, 2.6, 2.5, 2.4):
    p = build('S2', 1, N); r = sim(p, True); c = sim(p, False)
    print('S2 중간 N', N, ym(r['pay'] + round(p['dev_months'])) if r['pay'] else '-', ym(c['pay'] + round(p['dev_months'])))
# 2) AI 할인 마진: 할인 0/5/10/20% 시 고객 1곳당 공헌 증가(채택 50%, 원가 35)
for d in (0, .05, .10, .20):
    print('AI 할인', d, '공헌+', round(0.5 * 35 * d, 2), '/ 마크업 20%+할인', round(0.5 * 35 * (0.2 + d) - 0.02 * 0.5 * 35 * 1.2, 2))
# 3) AI 포함형이 약관상 불가 → S2에서 AI 부분 0
p = build('S2', 1); p['arpu'] -= scen(1)['ai_rev']; p['var'] -= scen(1)['ai_var']
r = sim(p, True); c = sim(p, False); print('S2-AI불가', ym(r['pay'] + round(p['dev_months'])), ym(c['pay'] + round(p['dev_months'])))
# 4) 파트너 손익분기: 파트너 추가 고객이 월 고정비 550을 덮는 데 필요한 매달 추가 고객(포함 기준 회수 S2 중간과 같게)
s2 = sim(build('S2', 1), True)['pay']
for pe in (0.25, 0.5, 0.75, 1.0, 1.5, 2.0):
    p = build('S2', 1); s = scen(1); tot = 3 + pe
    p['arpu'] -= (pe / tot) * 80 * 0.25; p['N'] = tot; p['fixed_cash'] += 550
    r = sim(p, True); c = sim(p, False)
    print('파트너 추가', pe, ym(r['pay'] + round(p['dev_months'])) if r['pay'] else '-', ym(c['pay'] + round(p['dev_months'])), round(-c['trough'] / 1e4, 2))
# 5) 고객 1곳 공헌 분해(중간)
s = scen(1)
print('S1 일회성 매출', s['S1_onetime_rev'], '이익', s['S1_onetime_gain'])
print('AI 매출', s['ai_rev'], '변동', round(s['ai_var'], 2), '공헌', round(s['ai_rev'] - s['ai_var'], 2))
print('인프라 매출', s['inf_rev'], '공헌', s['inf_rev'] - s['inf_var'])
# 6) CAC 비교: 파트너 마진의 생애 비용 vs 직접 CAC
for m in (.2, .25, .3):
    print('파트너 마진', m, '고객 1곳 생애 비용', round(80 * m * 50), '만 원 (월 구독료 × 마진 × 평균 이용 50개월)')
# 7) 시장조사팀 E 교차 확인: AI 포함, 고객 총지출 고정(구독 80 + AI 40 = 120), 매입 할인 0/10/20%
for d in (0, .1, .2):
    p = dict(BASE, arpu=120, var=29 + 40 * (1 - d) + 1); p['once_cash'] += 390 / 1  # 시장조사팀은 390을 투자에 더함
    r = sim(p, True); c = sim(p, False)
    print('E 할인', d, '공헌', 120 - p['var'], ym(r['pay'] + 9) if r['pay'] else '-', ym(c['pay'] + 9))
# 8) 시장조사팀 B 교차 확인: 인프라 별도 22만(가격 인상과 같음)
p = dict(BASE, arpu=102); r = sim(p, True); c = sim(p, False); print('B', ym(r['pay'] + 9), ym(c['pay'] + 9))
# 9) S2를 AI 크레딧 포함 100% 채택(원가 40, +20%)으로: 시장조사팀 C와 같은 AI 가정 + S1 + 인프라 옵션
p = build('S2', 1); s = scen(1); p['arpu'] += -s['ai_rev'] + 48; p['var'] += -s['ai_var'] + 41
r = sim(p, True); c = sim(p, False); print('S2(AI 전원 포함)', round(p['arpu'],1), round(p['arpu']-p['var'],1), ym(r['pay'] + round(p['dev_months'])), ym(c['pay'] + round(p['dev_months'])))
# 10) 바우처: 공급기업 부담 5~10%를 바우처 고객 구독료에서 차감(지원 기간 1년 가정은 단순화해 상시 차감으로 보수 계산), 바우처로 매달 신규 +0.5곳
for share, burden, extra in ((0.3, .1, 0.5), (0.3, .05, 0.5), (0.3, .1, 0.0)):
    p = build('S1', 1); p['arpu'] -= share * 80 * burden; p['N'] = 3 + extra
    r = sim(p, True); c = sim(p, False); print('바우처', share, burden, extra, ym(r['pay'] + 9), ym(c['pay'] + 9))
