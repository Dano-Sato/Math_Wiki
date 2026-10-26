# 050 · Dyck 경로의 최고점 봉우리 수 분포 단조성

> Dyck 경로에서 가장 높은 봉우리가 여러 개 나타날수록, 그런 경로의 수는 줄어들까?

| 항목 | 내용 |
| --- | --- |
| ID | 050 |
| 버전 | 0.1 |
| 제안일 | 2026-10-26 |
| 제안자 | Codex — 사용자의 새 추측 탐색 요청에 따라 구성 |
| 분야 | 조합론 · 격자 경로 · Dyck 경로 · 패턴 회피 순열 |
| 깊이 | 1 · 등록 후 재평가: 제한적 계수 부등식 후보 (36점) |
| 상태 | 미증명 · 반길이 $n\le12$의 모든 Dyck 경로 정확 열거 |
| 독창성 | 이 프로젝트에서 새로 구성한 계수 부등식 후보. 관련 통계의 생성함수는 문헌에 있으나 이 계수 단조성은 제한 검색에서 확인하지 못함; 문헌상 신규성 미확정 |
| 토론 | [discussion.md](discussion.md) |

## 정의와 추측

반길이 $n$의 Dyck 경로 $P$는 $U=(1,1)$과 $D=(1,-1)$로 이루어지고, 시작점 $(0,0)$에서 끝점 $(2n,0)$까지 가며 x축 아래로 내려가지 않는다. **봉우리**는 연속한 두 단계 $UD$이고, 그 높이는 $U$ 단계가 끝나는 점의 높이다. $H(P)$를 경로의 최대 높이라 하고, $m(P)$를 높이 $H(P)$에 있는 봉우리의 수라 하자. $b_{n,m}$은 $m(P)=m$인 반길이 $n$의 Dyck 경로 수다.

**추측 050.** 모든 $n\ge1$에서

$$b_{n,1}\ge b_{n,2}\ge\cdots\ge b_{n,n}.$$

즉, 최고 높이에 봉우리가 하나인 경로가 가장 많고, 그 봉우리 수를 늘릴수록 경로 수는 감소하거나 유지된다.

## 문헌에 있는 생성함수와 예비 검산

Elizalde의 Dyck 경로–132-회피 순열 대응에서 높이 $h$인 경로의 최대 높이 봉우리 개수는 순열의 최장 증가 부분수열 개수에 대응한다. 그는 높이 $h$ 경로를 세는 생성함수

$$H_h(u,z)=\sum_{P:\,H(P)=h}u^{m(P)}z^{|P|}
=\frac{u z^h}{V_{h-1}(z)\bigl(V_{h-1}(z)-u zV_{h-2}(z)\bigr)},$$

를 제시한다. 여기서 $V_{-1}=V_0=1$, $V_j=V_{j-1}-zV_{j-2}$이다. 따라서 $b_{n,m}=[z^nu^m]\sum_{h\ge1}H_h(u,z)$이다. 이 식과 통계 자체는 새 결과가 아니다. [Elizalde 논문/학위논문](https://math.dartmouth.edu/~sergi/papers/thesis.pdf)의 Proposition 2.4와 Theorem 5.7을 참고했다.

재현 코드로 반길이 $1\le n\le12$의 모든 Dyck 경로를 열거해 부등식을 확인했다. 이 범위에서 계수 벡터 $(b_{n,1},\ldots,b_{n,n})$는 모두 약한 감소 수열이었다. 이는 유한 검산일 뿐 일반 증명은 아니다. 코드와 정확한 표는 [verify.py](verify.py), [experiment.json](experiment.json)에 있다.

## 문헌 확인 범위와 한계

2026-10-26에 `"peaks at maximum height" unimodal Dyck path distribution`, `"number of peaks at maximum height" distribution`, `132-avoiding permutations number longest increasing subsequences distribution fixed length`를 검색했다. 높이별 생성함수, Dyck 경로의 봉우리 높이 통계, 그리고 최장 증가 부분수열이 유일한 132-회피 순열에 대한 연구를 확인했지만, 전체 계수열 $b_{n,m}$의 약한 감소를 명시한 추측이나 정리는 찾지 못했다. 검색 범위가 제한되어 문헌상 최초를 주장하지 않는다.

관련 배경: [Counting peaks at height $k$ in a Dyck path](https://arxiv.org/abs/math/0203222), [A combinatorial proof for 132-avoiding permutations with a unique longest increasing subsequence](https://arxiv.org/abs/2303.02808).

## 열린 질문

- 모든 $n$에 대한 감소 부등식을 증명하거나 반례를 찾을 수 있는가?
- 고정 최대 높이 $h$에 한정한 계수열도 같은 단조성을 갖는가?
- 132-회피 순열에서 최장 증가 부분수열의 개수에 대한 직접적인 삽입·삭제 사상이 존재하는가?
