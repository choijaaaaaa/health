# 나레이션 공백 제외 글자수·예상 길이 확인용 임시 도구. WHY: 목표 400~440자
# 밴드를 문단별로 맞추려면 문단 단위 분포까지 봐야 조정 지점을 찾을 수 있다.
import re, sys
for p in sys.argv[1:]:
    s = open(p, encoding='utf-8').read()
    paras = [x.strip() for x in s.split('\n\n') if x.strip()]
    tot = 0
    for i, para in enumerate(paras, 1):
        n = len(re.sub(r'\s', '', para))
        tot += n
        print(f'  P{i}: {n}')
    print(f'{p}: total={tot}  sec={tot/5.5:.1f}  paras={len(paras)}')
