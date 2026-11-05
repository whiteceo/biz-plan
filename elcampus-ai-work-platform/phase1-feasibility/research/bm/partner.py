# 파트너 등급 요건 → 인건비 → 손익분기. 단위 만 원. 자리표시자 값은 시장조사팀 확인 후 교체.
import math
HOUR = 775 / 209          # 개발자 시간당 회사 부담(KOSA 775만 ÷ 월 209시간) ≈ 3.7만
P = dict(exam=17.5, study_h=30, retry=1.3, valid_y=1, turnover=0.15, prem=0.05, avg_wage=650)   # Anthropic Developer·Architect $125, 유효 12개월(공식). 학습 30시간·재응시 1.3배·이직 15%·프리미엄 5%는 자리표시자
PAWS = dict(P, exam=19.7, valid_y=3)   # AWS Associate $150(₩197,287), 유효 3년(공식)
CM = 32.7                  # Stage 1·2 기준 고객 1곳당 월 공헌(ARPU 80, CAC 850, 해지 2%)
LTV = 51 * 50              # 고객 1곳 생애 공헌(구독 기준)
def cert_cost(k, p=P, premium=False, hire=0, hire_wage=775):
    one = k * (p['study_h'] * HOUR + p['exam'] * p['retry'])                # 최초 인증
    annual = one / p['valid_y'] + k * p['turnover'] * (p['study_h'] * HOUR + p['exam'] * p['retry'])  # 갱신 + 이직 보충
    monthly = annual / 12 + (k * p['avg_wage'] * p['prem'] if premium else 0) + hire * hire_wage
    return round(one), round(annual), round(monthly, 1)
TIERS = [('Anthropic Select', 10, P), ('AWS Select(자격증 4 + 교육 4)', 8, PAWS), ('Anthropic Preferred', 100, P)]
ORGS = [('Stage 1 조직', 7), ('Stage 2 조직', 11), ('Stage 3 조직', 22)]
print('시간당', round(HOUR, 2))
for tn, k, pp in TIERS:
    for on, staff in ORGS:
        short = max(0, k - staff)
        a = cert_cost(k, pp); b = cert_cost(k, pp, premium=True); c = cert_cost(min(staff, k), pp, premium=True, hire=short)
        print(f"{tn} {k}명 | {on} {staff}명, 부족 {short} | 기존+사내 타 부서 인증: 최초 {a[0]} 연 {a[1]} 월 {a[2]} → 손익분기 +{math.ceil(a[2]/CM)}곳 | 프리미엄 5% 포함 월 {b[2]} → +{math.ceil(b[2]/CM)}곳 | 부족분 채용 월 {c[2]} → +{math.ceil(c[2]/CM)}곳")
AWS_FEE = 2500 * 1400 / 1e4 / 12   # 연 $2,500 → 월
print('AWS 연회비 월', round(AWS_FEE, 1))
# 마진으로 상쇄: 연 비용 / 마진 = 필요 연 AI 원가, ÷ 고객당 연 AI 원가 420만
for lab, mon in (('Select 기존 인력, 프리미엄 없음 + AWS', cert_cost(10)[2] + cert_cost(8, PAWS)[2] + AWS_FEE), ('Select·AWS 프리미엄 5%', cert_cost(10, premium=True)[2] + cert_cost(8, PAWS)[2] + AWS_FEE), ('Select 3명 채용', cert_cost(7, premium=True, hire=3)[2] + cert_cost(8, PAWS)[2] + AWS_FEE)):
    yr = mon * 12
    row = []
    for m in (0.0, 0.05, 0.10, 0.15):
        if m == 0: row.append('상쇄 불가'); continue
        spend = yr / m; row.append(f"{m:.0%}: AI 원가 연 {spend/1e4:.1f}억 = AI 포함 고객 {spend/420:.0f}곳(채택 50%면 {2*spend/420:.0f}곳)")
    print(f"{lab}: 월 {mon:.0f}, 연 {yr:.0f} | " + ' | '.join(row) + f" | 디렉터리로 얻는 고객 연 {yr/LTV:.2f}곳이면 LTV로 상쇄")
# 인증 교육 상품화: 수강료 x, 마진 50%
for lab, mon in (('기존 인력', cert_cost(10)[2] + cert_cost(8, PAWS)[2] + AWS_FEE), ('프리미엄 5%', cert_cost(10, premium=True)[2] + cert_cost(8, PAWS)[2] + AWS_FEE)):
    yr = mon * 12
    print(lab, {price: math.ceil(yr / (price * 0.5)) for price in (30, 50, 100)}, '명/년 (수강료 만 원: 필요 수강생)')
# 개발 1명 채용 vs 비교
print('채용 1명(775) 손익분기 영향 +', math.ceil(775 / CM), '곳')
