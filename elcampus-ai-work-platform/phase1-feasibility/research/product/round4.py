# 반복 라운드 4 (2026-11-06): white 결정 "공용형 기본, 독립 클라우드는 상위 그레이드". 기준 가정은 scen.py와 같다(매달 3곳 CAC 0, 해지 2%).
# 그레이드: G1 공용 기본 / G2 공용 상위(업무 맥락 AI·안전 포함) / G3 독립 클라우드. 모든 상품 입력값은 [가정], 근거는 product-offer.md 12장.
from target import DEV, OPT, ym
from scen import run

W = 29151 / (29151 + 18395)          # 30~49인 비중(전국). 제조·건설 62:38로도 차이 작음(11.2)
BILL = 0.0                          # 결제 수수료: 현행 구상(E)과 같은 방식(세금계산서·계좌이체)으로 맞춰 따로 넣지 않음(레드팀 8장). 카드면 3.4%(토스페이먼츠)
# 고객 1곳 월 변동비(만 원)
V1 = 17                              # 공용형(BM 13.4). 스트레스 23(BM 17장)
AI, AI_S = 3, 6                      # 업무 맥락 AI 원가(11.2), 스트레스 6
SAFE_V = 2                           # 안전 기본 기록 지원 [가정]
G3_INFRA, G3_OPS = 17, 12.5          # 독립: 전용 인프라 17(BM 13.4), 운영 0.5일/월 × 일 25만(패치·배포·점검) [가정]
G3_ONCE = 100                        # 독립 1곳 개설: 2일(IaC 템플릿) + 보안 점검 2일 [가정] → 온보딩에 더함
PRICE = {  # (30~49인, 50~99인) 만 원/월
 '참고: 경쟁가': {'G1': (26, 33), 'G2': (45, 55), 'G3': (139, 169)},   # 사무직 좌석 경쟁 조합(11.4: 플로우 15석 33, + 안전 48~63). G3는 하단 가정가와 같게 둠
 '하단 가정가': {'G1': (49, 69), 'G2': (79, 109), 'G3': (139, 169)},
 '가치가(자리표시자)': {'G1': (69, 89), 'G2': (99, 129), 'G3': (159, 189)},
}
def grade_econ(tab, ai=AI, v1=V1):
    p = {g: W * a + (1 - W) * b for g, (a, b) in tab.items()}
    v = {'G1': v1, 'G2': v1 + ai + SAFE_V, 'G3': G3_INFRA + (v1 - 5) + ai + SAFE_V + G3_OPS}  # 공용 17 중 인프라 5를 전용 17로 대체
    v = {g: v[g] + p[g] * BILL for g in v}
    return p, v
MIX = {'상위 쏠림': (.30, .60, .10), '기본': (.50, .45, .05), '하위 쏠림': (.70, .28, .02)}
def mixed(tab, mix, **kw):
    p, v = grade_econ(tab, **kw)
    a = sum(m * p[g] for m, g in zip(mix, p)); vv = sum(m * v[g] for m, g in zip(mix, v))
    return round(a, 1), round(vv, 1), mix[2] * G3_ONCE
# 고정비·개발: [현실 산정] AI 개발 1.0명 + 운영·보안 엔지니어 1.0명(두 환경 동시 운영, 당직) + 외부 안전보건 전문가 300 + 운영 도구(모니터링·로그·백업) 100 + ISMS 간편인증 사후심사·유지 연 1,000 → 83
FIX = 1.0 * DEV + 1.0 * DEV + 300 + 83   # 운영 도구 100은 검토 문서 3.10(야간 대응 100, MSP 150)과 겹쳐 뺌(레드팀 8장)
# 개발 추가 개월: 공용형 데이터·권한 4 + 운영 관리 환경 2(테넌트 개설·해지, 그레이드 권한·요금, 사용량·AI 상한 모니터링, 감사 로그) + 두 환경 배포 1 + AI 1 + 안전 2 = 10, 병렬로 8 [가정]
# 운영 관리 환경은 검토 문서 3.6(운영 콘솔·일괄 업데이트·모니터링·청구, 출시 전 투자에 포함)과 겹친다. 새로 생기는 범위(회사 개설·해지, 그레이드 권한, 플랜 전환, 회사별 AI 상한)만 +1개월 [가정]
DEVM = 7
ONCE = 1500 + 3000 + 700             # 콘텐츠·법률 검토 1,000 + 보안 점검 500 / ISMS 간편인증 준비·심사 3,000 / 격리 침투 시험 700
G = dict(add_fixed=FIX, add_dev=DEVM, add_once=ONCE, cac=850)
# 단계 출시: 독립 그레이드(G3)를 공용 고객 100곳 이후로 미룸 → 두 환경 배포 1개월·ISMS·운영 0.5명분을 출시 전 비용에서 뺌
G_STEP = dict(add_fixed=1.0 * DEV + 0.5 * DEV + 300, add_dev=6, add_once=1500 + 700, cac=850)
G_LOW = dict(add_fixed=0.5 * DEV + 300, add_dev=5, add_once=1500, cac=850)   # 11장 F1 수준의 가벼운 산정(비교용)

if __name__ == '__main__':
    print(f"고정 추가 {FIX:.0f}만/월, 개발 +{DEVM}개월, 일회 {ONCE}만")
    for pk, tab in PRICE.items():
        p, v = grade_econ(tab)
        print(f"\n[{pk}] 그레이드 평균 가격/변동비: " + ', '.join(f"{g} {p[g]:.1f}/{v[g]:.1f}" for g in p))
        print('믹스 | 시나리오 | 월 매출/곳 | 변동비/곳 | 지속 월 흑자 | 15년 뒤 고객 | 월 영업이익(이익률) | 최대 적자 | 참고: 회수')
        for mk, mix in MIX.items():
            a, vv, g3 = mixed(tab, mix)
            for sn, (N, ch, kw) in {'기본': (3, .02, {}), '스트레스': (3, .03, dict(ai=AI_S, v1=23)), '보수': (2, .03, dict(ai=AI_S, v1=23))}.items():
                a2, v2, _ = mixed(tab, mix, **kw)
                r = run(G, N, a2, v2, ch, onb=65 + g3)
                print(f"{mk} | {sn} | {a2} | {v2} | {ym(r['be'])} | {r['n']} | {r['op']:,} ({r['mg']:.0%}) | {r['low']}억 | {ym(r['pay'])}")
        a, vv, g3 = mixed(tab, MIX['기본']); r = run(G_LOW, 3, a, vv, .02, onb=65 + g3)
        print(f"  비교: 같은 믹스, 11장 가벼운 산정(+0.5명, 개발 +5) → {ym(r['be'])}, 적자 {r['low']}억")
        for N in (6, 10):
            r = run(G, N, a, vv, .02, free=N, onb=65 + g3)
            print(f"  채널 참고(CAC 0 매달 {N}곳): {ym(r['be'])}, 적자 {r['low']}억, 15년 뒤 월 {r['op']:,}")
    print('\n비교: E 현행 구상 기본', ym(run(OPT['E 현행 구상'], 3, 80, 29, .02)['be']))
    print('독립(G3) 1곳 공헌(하단 가정가):', round(grade_econ(PRICE['하단 가정가'])[0]['G3'] - grade_econ(PRICE['하단 가정가'])[1]['G3'], 1), '/ G2:', round(grade_econ(PRICE['하단 가정가'])[0]['G2'] - grade_econ(PRICE['하단 가정가'])[1]['G2'], 1))

    print('\n단계 출시(G1·G2만, 믹스 55:45:0) 기본/스트레스/보수')
    for pk, tab in PRICE.items():
        for sn, (N, ch, kw) in {'기본': (3, .02, {}), '스트레스': (3, .03, dict(ai=AI_S, v1=23)), '보수': (2, .03, dict(ai=AI_S, v1=23))}.items():
            a, vv, _ = mixed(tab, (.55, .45, 0), **kw); r = run(G_STEP, N, a, vv, ch)
            print(f"  {pk} {sn}: {a}/{vv} → {ym(r['be'])}, 적자 {r['low']}억, 15년 뒤 월 {r['op']:,}")
    print('\nE 기본(3년 6개월)과 같아지는 가격 배수(기본 믹스, 하단 가정가 기준)')
    e = run(OPT['E 현행 구상'], 3, 80, 29, .02)['be']
    for name, o, mix in (('전체 3그레이드', G, MIX['기본']), ('단계 출시', G_STEP, (.55, .45, 0))):
        for k in range(100, 250):
            t = {g: (a * k / 100, b * k / 100) for g, (a, b) in PRICE['하단 가정가'].items()}
            a, vv, g3 = mixed(t, mix); r = run(o, 3, a, vv, .02, onb=65 + g3)
            if r['be'] and r['be'] <= e: print(f"  {name}: 하단 가정가 × {k/100:.2f} = 월 매출/곳 {a} (G1 50~99인 {t['G1'][1]:.0f}만)"); break

    print('\n운영·보안 인원 민감도(가치가 기본 믹스): ' + ' · '.join(f"{x}명 {ym(run(dict(G, add_fixed=FIX + (x - 1) * DEV), 3, *mixed(PRICE['가치가(자리표시자)'], MIX['기본'])[:2], .02, onb=65 + MIX['기본'][2] * G3_ONCE)['be'])}" for x in (0.5, 1.0, 2.0)))
    e1 = run(dict(OPT['E 현행 구상'], add_fixed=DEV), 3, 80, 29, .02)['be']
    print('현행 구상(E) + 운영 1.0명:', ym(e1))
