# 044 · 집합 분할의 소수 크기 블록 분포 로그오목성

> 유한 집합을 블록들로 나누고 크기가 소수인 블록의 수를 센다. 그 수별 분할 개수는 언제나 로그오목할까?

| 항목 | 내용 |
| --- | --- |
| ID | 044 |
| 버전 | 0.1 |
| 제안일 | 2026-10-26 |
| 제안자 | Codex — 사용자의 새 추측 탐색 요청에 따라 구성 |
| 분야 | 조합론 · 집합 분할 · Bell 다항식 · 소수 크기 통계 |
| 깊이 | 1 · 등록 후 재평가: 제한적 계수 부등식 후보 (34점) |
| 상태 | 미증명 · 정확 점화식으로 $1\le n\le100$ 로그오목성 확인 |
| 독창성 | 이 프로젝트에서 새로 구성한 후보. 제한 웹 검색에서 정확히 같은 로그오목성 명제는 확인하지 못했으나, 일반적인 블록 크기 표시 생성함수 연구와 인접하며 문헌상 신규성은 미확정 |
| 토론 | [discussion.md](discussion.md) |

## 정의와 추측

$[n]=\{1,\ldots,n\}$의 집합 분할 $\pi$에서 크기가 소수인 블록(크기 $2,3,5,7,\ldots$)의 수를 $q(\pi)$라 하자. $a_{n,k}$를 $q(\pi)=k$인 분할의 개수로 둔다. 크기 1인 블록은 세지 않는다.

**추측 044.** 모든 $n\ge1$에 대해

$$
\bigl(a_{n,0},a_{n,1},\ldots,a_{n,\lfloor n/2\rfloor}\bigr)
$$

은 로그오목하다. 즉 $1\le k<\lfloor n/2\rfloor$에서

$$
\boxed{a_{n,k}^{,2}\ge a_{n,k-1}a_{n,k+1}.}
$$

범위의 모든 계수는 양수다. $k$개의 서로소 2원소 블록을 먼저 두고 남은 원소를 1원소 블록들로 두면 이를 확인할 수 있다.

## 생성함수와 검산

집합 분할의 지수생성함수에 소수 크기 블록을 표시하면

$$
\sum_{n\ge0}\sum_k a_{n,k}u^k\frac{x^n}{n!}
=\exp\!\left(e^x-1+(u-1)\sum_{p\text{ prime}}\frac{x^p}{p!}\right).
$$

크기 $n$에서 블록에 원소 1이 들어 있다고 고르면 다음 정확 점화식을 얻는다.

$$
a_{n,k}=\sum_{m=1}^n {n-1\choose m-1}
\begin{cases}
a_{n-m,k-1},&m\text{이 소수},\\
a_{n-m,k},&m\text{이 소수가 아님}.
\end{cases}
$$

여기서 $a_{0,0}=1$이고 범위를 벗어난 계수는 0이다. 이 점화식으로 정확한 정수 연산을 하여 $1\le n\le100$의 모든 내부 로그오목 부등식을 확인했다. 이는 유한 검산이며 일반 증명이 아니다. 재현 코드는 [verify.py](verify.py), 결과는 [experiment.json](experiment.json)에 있다.

## 문헌 확인 범위

2026-10-26에 `prime-sized blocks set partitions`, `number of prime blocks set partition`, `Bell polynomials log-concavity selected block sizes`를 검색했다. 확인한 결과는 집합 분할의 Bell 다항식·블록 크기 표시 생성함수 및 소수의 정수 분할에 관한 자료였으며, 이 통계의 로그오목성 명제와 일치하는 결과는 찾지 못했다. 이는 제한 검색일 뿐 포괄적인 문헌 조사나 최초성 주장이 아니다. 관련 배경: [NIST DLMF §26.7](https://dlmf.nist.gov/26.7), [MathWorld: Partial Bell Polynomial](https://mathworld.wolfram.com/PartialBellPolynomial.html).
