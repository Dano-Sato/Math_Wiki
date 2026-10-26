# 047 · 유한 아핀 공간 부분집합의 생성 차원 분포

> 유한 아핀 공간에서 k개 점을 고른다. 이 점들이 만드는 최소 아핀 부분공간의 차원별 개수는 가운데를 향해 엄격히 로그오목하게 변할까?

| 항목 | 내용 |
| --- | --- |
| ID | 047 |
| 버전 | 0.1 |
| 제안일 | 2026-10-26 |
| 제안자 | Codex — 사용자의 새 추측 탐색 요청에 따라 구성 |
| 분야 | 유한 기하 · 아핀 공간 · 부분공간 격자 · 계수열 |
| 깊이 | 2 · 연구 수준 후보 (Codex 추정, 잠정) |
| 상태 | 미증명 · 뫼비우스 반전 계수식으로 여러 유한 범위에서 엄격 로그오목성 확인 |
| 독창성 | 이 프로젝트에서 새로 구성한 후보. 제한 검색에서 정확히 같은 분포의 로그오목성은 찾지 못했으나 유한 기하의 생성 집합 계수와 matroid 랭크 분포에 인접하며 문헌상 신규성은 미확정 |
| 토론 | [discussion.md](discussion.md) |

## 정의와 추측

소수 거듭제곱 $q$와 정수 $d\ge1$에 대해 $\operatorname{AG}(d,q)=\mathbb F_q^d$를 유한 아핀 공간으로 둔다. $1\le k\le q^d$인 $k$원소 부분집합 $X$의 아핀 생성 부분공간 $\operatorname{aff}(X)$는 $X$를 포함하는 가장 작은 아핀 부분공간이다. 다음을 정의한다.

$$
a_{d,q,k,r}=\#\{X\subseteq\operatorname{AG}(d,q): |X|=k,\ \dim\operatorname{aff}(X)=r\}.
$$

$k=1$이면 가능한 차원은 $r=0$뿐이다. $k\ge2$이면 가능한 차원은

$$
r_{\min}=\max\{1,\lceil\log_q k\rceil\}\le r\le r_{\max}=\min\{d,k-1\}.
$$

이 범위의 모든 차원은 실현 가능하다.

**추측 047.** 모든 소수 거듭제곱 $q$, $d\ge1$, $1\le k\le q^d$에 대해 $r\mapsto a_{d,q,k,r}$는 가능한 차원 구간에서 **엄격 로그오목**하다. 즉 구간 내부의 각 $r$에서

$$
\boxed{a_{d,q,k,r}^{,2}>a_{d,q,k,r-1}a_{d,q,k,r+1}.}
$$

내부 차원이 없으면 명제는 공허하게 성립한다.

## 정확 계수식과 유한 검산

$G_q(r,j)=\begin{bmatrix}r\\j\end{bmatrix}_q$를 가우스 이항계수라 하고 $s_{q,k}(r)$를 고정된 $r$차원 아핀 공간을 생성하는 $k$원소 부분집합의 수라 하자. 아핀 $j$-평면의 수와 아핀 부분공간 격자의 뫼비우스 함수로부터

$$
s_{q,k}(r)=\sum_{j=0}^r(-1)^{r-j}q^{\binom{r-j}{2}}q^{r-j}G_q(r,j)\binom{q^j}{k},
\qquad
a_{d,q,k,r}=q^{d-r}G_q(d,r)s_{q,k}(r).
$$

같은 계수는 $\binom{q^r}{k}=\sum_{j=0}^r q^{r-j}G_q(r,j)s_{q,k}(j)$의 삼각 점화식으로도 계산할 수 있다.

[verify.py](verify.py)는 이 정확 점화식으로 계산하고, 작은 공간에서는 부분집합 직접 열거와 대조한다. [experiment.json](experiment.json)에 기록된 유한 매개변수 표본에서 확인한 모든 내부 부등식은 엄격했다. 이는 유한 계산이며 전칭 증명은 아니다.

## 문헌 확인 범위

2026-10-26에 `finite affine space k-subsets affine span dimension distribution log-concavity`, `number of k-subsets spanning subspace dimension`, `matroid k-subsets rank distribution log-concavity`를 검색했다. Kordecki의 2000년 논문은 유한 아핀 기하에서 무작위 부분집합의 랭크, 특히 전체 랭크를 얻을 확률과 작은 랭크 표를 다룬다([논문 초록·서지](https://geodesic.mathdoc.fr/item/DMGT_2000_20_2_a4/), [출판사 PDF](https://www.dmgt.uz.zgora.pl/publish/pdf.php?doi=1120)). 따라서 아핀 생성 차원 분포 자체는 이미 연구된 주제다. 이번 후보의 구별점은 **부분집합 크기 $k$를 고정한 조건부 계수열의 엄격 로그오목성**이며, 제한 검색에서 이 성질과 같은 추측은 찾지 못했다. 논문 전문의 모든 결과와 이 명제의 중복 여부를 대조하지는 못했으므로 신규성은 미확정이고, 문헌상 최초를 주장하지 않는다. matroid 독립집합 수의 로그오목성도 배경상 인접하지만 본 계수열과는 다른 수열이다([matroid 로그오목성 개관](https://epubs.siam.org/doi/10.1137/25M1807344)).
