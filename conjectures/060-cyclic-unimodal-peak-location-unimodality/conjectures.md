# 060 · 순환 단봉 순열의 꼭대기 위치 분포 단봉성

> 길이 $n$인 순환 단봉 순열에서 최대 원소의 위치별 개수는 위치에 따라 단봉을 이룰까?

| 항목 | 내용 |
| --- | --- |
| ID | 060 |
| 버전 | 0.1 |
| 제안일 | 2026-10-26 |
| 제안자 | Codex — 사용자의 새 추측 탐색 요청에 따라 구성 |
| 분야 | 조합론 · 순열 · Lyndon 단어 · 모듈러 부분집합 합 |
| 깊이 | 1 · 기존 계수열의 단봉성 퍼즐·소정리 후보 (ChatGPT 재평가) |
| 상태 | 미증명 · 기존 점화식으로 $3\le n\le150$ 확인; 직접 순열 전수열거 $3\le n\le9$ 대조 |
| 독창성 | 위치별 계수 자체와 공식은 기존 문헌에 있음. 그 계수열의 단봉성은 2026-10-26 제한 검색에서 확인하지 못했으며, 문헌상 최초를 주장하지 않음 |
| 토론 | [discussion.md](discussion.md) |

## 정의와 추측

순열 $\pi\in S_n$를 한 줄 표기로 썼을 때, 어떤 $p$에 대해
$\pi_1<\cdots<\pi_p>\pi_{p+1}>\cdots>\pi_n$이면 단봉 순열이라 하자. 순열을 함수로 보아 하나의 길이 $n$ 순환을 이루면 **순환 단봉 순열**이라 한다. $T(n,p)$를 순환 단봉 순열 중 최대 원소 $n$이 위치 $p$에 있는 순열의 수로 정의한다.

**추측 060.** 모든 $n\ge3$에 대해 $(T(n,1),T(n,2),\ldots,T(n,n))$은 단봉 수열이다. 즉 어떤 $m=m(n)$이 있어
$$T(n,1)\le\cdots\le T(n,m)\ge\cdots\ge T(n,n).$$

이 추측은 위치별 계수의 모양에 관한 것이며, 각 순열이 단봉이라는 정의를 되풀이하는 명제가 아니다. 수열이 대칭이 아닌 경우도 포함한다. 예를 들어 $n=10$ 행은 $(0,1,3,9,13,12,8,4,1,0)$이다.

## 알려진 점화식과 예비 검산

Archer–Lauderdale은 $L_2(n,k)$를 길이 $n$, 1의 개수 $k$인 이진 Lyndon 단어의 수로 두고,
$$L_2(n,k)=\frac1n\sum_{d\mid\gcd(n,k)}\mu(d)\binom{n/d}{k/d}$$
를 기록한다. 그들의 Lemma 4.4에 따르면 $T(n,i)+T(n,i+1)=L_2(n,i)$이다. 단, $n$이 짝수이고 $n+i\equiv2\pmod4$이면 우변에 $L_2(n/2,i/2)$가 더해진다. 또한 $T(n,1)=0$이다. 따라서 기존 결과로 모든 계수를 정확히 계산할 수 있지만, 이 점화식만으로 행의 단봉성이 자동으로 성립한다고 단정하지 않는다.

이 점화식을 정수 산술로 계산해 $3\le n\le150$을 확인했고, 모든 행이 단봉이었다. 별도로 순열을 직접 열거하여 하나의 순환인지, 한 번 증가한 뒤 감소하는지 검사한 $3\le n\le9$에서도 점화식 값과 모든 위치별 계수가 일치했다. 재현 코드는 [verify.py](verify.py), 출력 요약은 [experiment.json](experiment.json)에 있다. 유한 계산은 일반 증명이 아니다.

## 문헌 확인 범위와 한계

Archer–Lauderdale, [“Enumeration of cyclic permutations in vector grid classes”](https://intlpress.com/site/pub/files/_fulltext/journals/joc/2020/0011/0001/JOC-2020-0011-0001-a009.pdf), §4.2와 Lemma 4.3–4.6은 $T(n,k)$의 점화식·명시식, 그리고 $n\not\equiv2\pmod4$일 때의 대칭성을 다룬다. OEIS [A303979](https://oeis.org/A303979)는 같은 삼각형의 정의와 공식을 수록한다. 최근의 Dougherty-Bliss–Elizalde, [“Necklaces, subset sums, and cyclic permutations”](https://arxiv.org/abs/2603.15830)는 이를 원시 이진 목걸이 및 특정 나머지류 합을 갖는 부분집합과 연결한다.

2026-10-26에 `cyclic unimodal permutations peak position unimodal`, `A303979 unimodal rows`, `cyclic V-shaped permutations minimum position unimodal` 및 관련 문구를 검색했다. 확인한 논문과 OEIS 항목에는 위치별 계수와 대칭성은 있었지만, 각 행의 단봉성 주장은 찾지 못했다. 검색은 제한적이며 이 관찰의 독창성을 보증하지 않는다.

## 열린 질문

- 점화식과 $L_2(n,k)$의 성질만으로 모든 행의 단봉성을 증명할 수 있는가?
- $n\equiv2\pmod4$인 비대칭 행에서도 단봉성이 성립하는 핵심 이유는 무엇인가?
- 순환 V형 순열의 최솟값 위치별 계수, 또는 고정된 여러 단조 블록을 갖는 순환 순열로 확장되는가?
