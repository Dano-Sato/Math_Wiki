# 056 · Ménage 순열 하강수 분포의 로그오목성

> 대각선과 한 칸 순환 이동을 피하는 순열을 하강수로 분류하면, 계수열은 항상 로그오목할까?

| 항목 | 내용 |
| --- | --- |
| ID | 056 |
| 버전 | 0.1 |
| 제안일 | 2026-10-26 |
| 제안자 | Codex — 사용자의 새 추측 탐색 요청에 따라 구성 |
| 분야 | 조합론 · 순열 통계 · rook theory |
| 깊이 | 1 · 등록 후 재평가: 제한적 계수 부등식 후보 (37점) |
| 상태 | 미증명 · $3\le n\le18$ 정확 부분집합 동적계획 |
| 독창성 | Ménage 순열과 하강수 통계는 각각 알려져 있으나 이 조합의 로그오목성은 제한 검색에서 확인하지 못함; 문헌상 신규성 미확정 |
| 토론 | [discussion.md](discussion.md) |

## 정의와 추측

$[n]=\{1,\ldots,n\}$의 순열 $\pi$가 **Ménage 순열**이라 함은 모든 $i\in[n]$에 대해
$$\pi(i)\ne i,\qquad \pi(i)\not\equiv i+1\pmod n$$
을 만족함을 말한다. 이는 원형 순환 자리 이동을 쓰는 통상적인 Ménage 조건 중 한 관례다. 하강수는
$$\operatorname{des}(\pi)=\#\{i\in[n-1]:\pi(i)>\pi(i+1)\}$$
로 둔다. $a_{n,k}$를 하강수가 $k$인 길이 $n$ Ménage 순열의 수라 하자.

**추측 056.** 모든 $n\ge3$과 $1\le k\le n-2$에 대해
$$a_{n,k}^2\ge a_{n,k-1}a_{n,k+1}.$$

즉 $(a_{n,0},\ldots,a_{n,n-1})$은 로그오목하다. 이 계수열은 양 끝에서 0일 수 있다. 로그오목성은 양의 지지집합이 구간인 비음수 수열에서 단봉성을 함의한다.

## 예비 검산

두 금지 조건을 차례로 적용하는 부분집합 동적계획으로 $3\le n\le18$의 계수를 정확히 계산했다. 접두부 상태 $F_i(S,j;k)$를 ``길이 $i$, 사용 값 집합 $S$, 마지막 값 $j$, 하강수 $k$''로 두고, 허용되는 새 값 $x$를 붙일 때 $k$에 $\mathbf 1_{j>x}$를 더한다. $n\le10$에서는 별도의 $n!$ 직접 열거와 결과를 대조했다. 이 범위에서 로그오목성 위반은 없고 모든 행이 단봉성이었다. 정확한 계수는 [experiment.json](experiment.json), 재현 코드는 [verify.py](verify.py)에 둔다. 이 유한 검산은 일반 명제의 증명이 아니다.

## 문헌 확인 범위와 한계

2026-10-26에 `"descent polynomial" "ménage"`, `"descents" "ménage permutations"`, `"ménage permutations" statistics Eulerian`, `"straight Ménage" descents permutations`를 검색했다. Yiting Li의 2015년 논문은 straight 및 ordinary Ménage 순열의 조합 구조와 순환 수 통계를 다루고, 2024년 논문은 Ménage 순열의 prefix counting 및 unranking을 다룬다. 확인한 초록·본문 검색 결과에서는 하강수 로그오목성이나 하강수 다항식을 보지 못했다. 문헌 검색은 제한적이며, 최초성은 주장하지 않는다.

참고 문헌: [Li, *Ménage Numbers and Ménage Permutations* (2015)](https://cs.uwaterloo.ca/journals/JIS/VOL18/Li2/li51.html); [Kagey et al., *Ranking and unranking restricted permutations* (2024)](https://doi.org/10.1016/j.dam.2024.05.010). Ménage 수의 금지 위치 관례는 [OEIS A000179](https://oeis.org/A000179)에도 명시되어 있다.

## 열린 질문

- 모든 $n$에서 로그오목성을 증명하거나 반례를 찾을 수 있는가?
- rook polynomial 또는 금지 위치 보드의 하강수 정제 기법으로 계수식을 얻을 수 있는가?
- 역순열/보완 연산이 분포 대칭성의 어떤 부분을 보존하며, 이 계수열에 추가 부등식을 줄 수 있는가?
