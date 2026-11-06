# 기술운영팀: SaaS 구축·운영 비용 산정 → 그레이드 구조 재무 재계산. 단위 만 원/월.
# 근거: research/saas-build-ops-cost.md. 시뮬레이터·가격·믹스는 상품기획팀 round4.py 그대로(기준 가정표: 매달 3곳 CAC 0, 해지 2%).
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'product'))
from target import DEV, ym, OPT
from scen import run
import round4 as R
FX = 1400; H = 730
def krw(usd): return usd * FX / 1e4
# ---- 1. 인프라 원가(AWS 서울 ap-northeast-2 온디맨드, AWS Price List API 2026-11-06 조회) ----
RDS = {'t4g.small': (0.051, 0.102), 't4g.medium': (0.102, 0.203), 'm6g.large': (0.221, 0.441)}  # (Single-AZ, Multi-AZ) $/h
GP3_RDS = (0.131, 0.262); SNAP = 0.095; EC2 = {'t4g.small': 0.0208, 't4g.medium': 0.0416, 'm6g.large': 0.094}
ALB_H, LCU_H, NAT_H, NAT_GB, EBS = 0.0225, 0.008, 0.059, 0.059, 0.0912
pool_prod = (RDS['m6g.large'][1]*H + 100*GP3_RDS[1] + 100*SNAP      # 공용 DB 다중 AZ, 100GB, 백업 100GB
             + 2*EC2['m6g.large']*H + 2*30*EBS                       # 앱 서버 2대
             + ALB_H*H + 2*LCU_H*H + 2*NAT_H*H + 100*NAT_GB          # 로드밸런서, NAT 2개(AZ별)
             + 22 + 11 + 30 + 20 + 10 + 25 + 25 + 5)                 # WAF·공인 IP·로그·GuardDuty·KMS/비밀·전송·캐시·S3 [가정 사용량]
staging = RDS['t4g.small'][0]*H + EC2['t4g.medium']*H + ALB_H*H + 2*LCU_H*H + NAT_H*H + 20
devci = 50
g3_shared = (RDS['t4g.small'][1]*H + 50*GP3_RDS[1] + 50*SNAP + 2*EC2['t4g.small']*H + 10 + 3)   # 전용 DB(다중 AZ) + 전용 앱 2개, 공용 계정·LB
g3_silo = (RDS['t4g.medium'][1]*H + 50*GP3_RDS[1] + 50*SNAP + 2*EC2['t4g.medium']*H + 2*10*EBS
           + ALB_H*H + 2*LCU_H*H + NAT_H*H + 15 + 7 + 15 + 10 + 3)                               # 고객별 계정·VPC 완전 분리
INFRA = dict(pool_prod=krw(pool_prod), staging=krw(staging), devci=krw(devci), g3_shared=krw(g3_shared), g3_silo=krw(g3_silo))

# ---- 2. 개발 공수(1명·월, 플랫폼·운영 범위) ----
ITEMS = [  # (항목, 기본, 낮음, 높음)
 ('테넌트 데이터 분리·격리 시험', 2.0, 1.5, 3.0), ('인증·조직·권한', 1.25, 1.0, 2.0), ('그레이드 기능 권한·한도', .75, .5, 1.0),
 ('빌링(정기결제·계좌이체 대사·세금계산서·일할·연/월·파일럿·독촉·크레딧)', 2.5, 2.0, 3.5), ('운영 콘솔·지원 도구', 1.25, 1.0, 2.0),
 ('개설·해지·반출·파기 확인서·다운셀 읽기 전용', 1.25, 1.0, 1.75), ('AI 사용량 계측·상한', 1.0, .75, 1.5), ('감사 로그·접속기록', .5, .5, .75),
 ('관측·알림·상태 페이지', .5, .5, .75), ('배포 파이프라인·IaC·스테이징', 1.0, .75, 1.5), ('백업·DR·회사 단위 복구', .75, .5, 1.0),
 ('보안 강화', .75, .5, 1.0), ('독립 그레이드 스택·일괄 업데이트·공용→전용 이관', 1.75, 1.25, 2.5), ('엑셀 일괄 업로드', .5, .25, .75),
 ('부하·간섭 시험', .25, .25, .5)]
QA = 0.15
REPLACED = 6.75     # 검토 문서 최소 요건 중 이 목록이 대체하는 몫(인프라·보안·배포 약 6개월분 + 운영 콘솔·청구 0.75)
FEATURE = 6.0       # 업무 맥락 AI 2 + 안전 기본 기록 4 (상품기획팀 +1·+2개월 × 2.0명분)
RATE = 16 / 9       # 검토 문서 환산: 개발 16명·월을 9개월에(2.0명분 + 겸직 조율)
def plat(k):  # k=1 기본, 2 낮음, 3 높음
    return sum(i[k] for i in ITEMS) * (1 + QA)
def add_months(k, step=False):
    p = plat(k) - (([i for i in ITEMS if i[0].startswith('독립')][0][k] - .5) * (1 + QA) if step else 0)
    return round((p - REPLACED + FEATURE) / RATE)

# ---- 3. 출시 뒤 월 고정비(라운드 4 위에 다시 산정) ----
def fixed(case, step=False):
    ops = {'기본': .5 if step else 1.0, '낮음': .5 if step else .5, '높음': 1.0 if step else 1.5}[case]
    f = 1.0*DEV + ops*DEV + 300          # AI 개발 1.0명(상품기획팀), 운영·보안, 외부 안전보건(상품기획팀)
    f += {'기본': 70, '낮음': 50, '높음': 110}[case]                       # 운영 도구 추가분(기존 30~60만 위)
    f += {'기본': 42, '낮음': 25, '높음': 67}[case]                        # 외부 취약점 점검·모의해킹 연 500(300~800)만
    if not step: f += {'기본': 50, '낮음': 35, '높음': 80}[case]           # ISMS 간편인증 사후·갱신 심사·컨설팅 연 600(420~960)만
    if not step: f += {'기본': 50, '낮음': 0, '높음': 150}[case]           # 독립 4시간 대응 약정의 당직 추가(기존 100만 위)
    f += {'기본': 25, '낮음': 15, '높음': 40}[case]                        # 법무 상시 검토 연 300만
    f += {'기본': 30, '낮음': 20, '높음': 50}[case]                        # 세무(부가세 겸영 안분·선수수익)
    f += {'기본': 80, '낮음': 40, '높음': 120}[case]                       # 수납·대사·세금계산서·미수 관리(경영지원 0.2명분)
    return f
def once(case, step=False):
    o = 1500 + {'기본': 300, '낮음': 0, '높음': 600}[case]                 # 콘텐츠·법률 1,000 + 보안 점검 500 + 약관·DPA·재위탁 추가
    o += {'기본': 700, '낮음': 500, '높음': 1500}[case]                    # 출시 전 회사 간 격리 모의해킹
    if not step: o += {'기본': 3000, '낮음': 2000, '높음': 4500}[case]     # ISMS 간편인증 준비·심사
    return o
G3 = {'기본': ('g3_shared', .75, 200), '낮음': ('g3_shared', .5, 100), '높음': ('g3_silo', 1.5, 350)}  # 인프라 방식, 월 운영 일수, 개설
PRICE = {'가치가': {'G1': (69, 89), 'G2': (99, 129), 'G3': (159, 189)},     # 상품기획팀 12.2 가치가(자리표시자)
         '하단 가정가': {'G1': (49, 69), 'G2': (79, 109), 'G3': (139, 169)}}  # 상품기획팀 12.2 하단(옛 이름 경쟁가)
DAY = 37            # 엔지니어 일 단가: KOSA 775만 ÷ 21일
BAD = .01           # 대손·미수 [가정]

def econ(tab, case, mix, ai=R.AI, v1=R.V1):
    p = {g: R.W * a + (1 - R.W) * b for g, (a, b) in tab.items()}
    k, d, _ = G3[case]
    v = {'G1': v1, 'G2': v1 + ai + R.SAFE_V,
         'G3': INFRA[k] + (v1 - 5) + ai + R.SAFE_V + d * DAY + (5 if k == 'g3_silo' else 0)}
    v = {g: v[g] + p[g] * (R.BILL + BAD) for g in v}
    a = sum(m * p[g] for m, g in zip(mix, p)); vv = sum(m * v[g] for m, g in zip(mix, v))
    return round(a, 1), round(vv, 1), mix[2] * G3[case][2], v

SCN = {'기본': (3, .02, {}), '스트레스': (3, .03, dict(ai=R.AI_S, v1=23)), '보수': (2, .03, dict(ai=R.AI_S, v1=23))}
def table(price='가치가'):
    rows = []
    for case in ('기본', '낮음', '높음'):
        for step, mix in ((False, R.MIX['기본']), (True, (.55, .45, 0))):
            o = dict(add_fixed=fixed(case, step), add_dev=add_months(1 if case == '기본' else 2 if case == '낮음' else 3, step),
                     add_once=once(case, step), cac=850)
            res = {}
            for sn, (N, ch, kw) in SCN.items():
                a, vv, g3, _ = econ(PRICE[price], case, mix, **kw)
                r = run(o, N, a, vv, ch, onb=65 + g3); res[sn] = r
            rows.append((case, '단계 출시' if step else '세 그레이드 동시', o, a, vv, res))
    return rows

if __name__ == '__main__':
    print('인프라(만 원/월):', {k: round(v, 1) for k, v in INFRA.items()})
    for k, n in ((1, '기본'), (2, '낮음'), (3, '높음')):
        print(f'플랫폼 공수 {n}: {plat(k):.1f}명·월(QA 포함) → 개발 +{add_months(k)}개월 / 단계 출시 +{add_months(k, True)}개월')
    for price in ('가치가', '하단 가정가'):
        print(f'\n[{price}] 산정 | 출시 | 월 고정 추가 | 개발 + | 일회 | 월 매출/곳 | 변동비/곳 | 기본 | 스트레스 | 보수 | 기본 최대 적자')
        for case, st, o, a, vv, res in table(price):
            print(f"{case} | {st} | {o['add_fixed']:.0f} | {o['add_dev']} | {o['add_once']} | {a} | {vv} | "
                  f"{ym(res['기본']['be'])} | {ym(res['스트레스']['be'])} | {ym(res['보수']['be'])} | {res['기본']['low']}억")
    # 비교: 상품기획팀 잠정(round4)
    a, vv, g3 = R.mixed(PRICE['가치가'], R.MIX['기본']); r = run(R.G, 3, a, vv, .02, onb=65 + g3)
    a2, vv2, _ = R.mixed(PRICE['가치가'], (.55, .45, 0)); r2 = run(R.G_STEP, 3, a2, vv2, .02)
    print('상품기획팀 현재 입력:', R.G, R.G_STEP)
    print(f"\n비교: 상품기획팀 잠정 가치가 기본 {ym(r['be'])}({r['low']}억), 단계 출시 {ym(r2['be'])}({r2['low']}억)")
    # 민감도(가치가, 기본 산정, 단계 출시)
    base = dict(add_fixed=fixed('기본', True), add_dev=add_months(1, True), add_once=once('기본', True), cac=850)
    a, vv, _, _ = econ(PRICE['가치가'], '기본', (.55, .45, 0))
    def be(**kw):
        o = dict(base); oa, ov = a, vv
        if 'dfix' in kw: o['add_fixed'] += kw['dfix']
        if 'ddev' in kw: o['add_dev'] += kw['ddev']
        if 'dvar' in kw: ov += kw['dvar']
        return ym(run(o, 3, oa, ov, .02)['be'])
    print('\n민감도(가치가·단계 출시·기본 산정):', '기준', be(),
          '| 공용 인프라 실측 1.5만(−3.5)', be(dvar=-3.5), '| 운영·보안 1.0명', be(dfix=DEV*.5),
          '| 운영·보안 0명(MSP 전담)', be(dfix=-DEV*.5), '| 개발 +3개월', be(ddev=3), '| 개발 −2개월', be(ddev=-2),
          '| 경영지원·법무·세무 0', be(dfix=-135))
    # 독립 그레이드 1곳 공헌(가치가 50~99인 189만)
    for case in ('기본', '높음'):
        _, _, _, v = econ(PRICE['가치가'], case, R.MIX['기본'])
        print(f'독립(G3) 1곳 변동비 {case}: {v["G3"]:.1f}만 (상품기획팀 잠정 {R.grade_econ(R.PRICE["가치가(자리표시자)"])[1]["G3"]:.1f}만)')
