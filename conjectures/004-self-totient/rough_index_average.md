# 고정된 소인수 개수에서의 상대밀도 1 토션트 수렴

대상: 004의 원래 수열 $a_1=1$,
$a_n=\#\{k<n:\gcd(a_k,n)=1\}$.
원래 요청은 v0.10의 모든 정수에 대한 점별 수렴이다.
이 파일에서는 같은 수열의 고정 $r$-거의소수에 대한 더 약한 상대밀도 결론을 증명한다.
작성: Codex, 2026-10-28.
**아래 부분 정리는 증명됨 · 자체 검토 완료(독립 검토 미수행).**
Lean 형식화는 수행하지 않았다. 본 추측 004 전체는 여전히 미증명이다.

## 1. 정확한 부분 정리

$\Omega(n)$은 소인수를 **중복 포함**하여 센 개수이고,
$A_r(X)=\#\{n\le X:\Omega(n)=r\}$라 하자.
모든 **고정된** 정수 $r\ge1$과 모든 $\varepsilon>0$에 대해

$$
\boxed{\frac{\#\{n\le X:\Omega(n)=r,
\ |a_n/\varphi(n)-1|>\varepsilon\}}{A_r(X)}\longrightarrow0.}
$$

즉 $r$-거의소수 안에서 상대밀도 의미로 토션트 비율이 1에 수렴한다.
특히 소수 두 개의 곱인 수들에서 성립한다. **모든** $r$-거의소수에서의
점별 수렴을 증명하는 것은 아니다. $r$이 $X$와 함께 증가하는 주장도 아니다.

$r=1$은 L2의 정확한 등식이다. $r\ge2$에서는 아래 증명으로, 고정된
$0<\varepsilon<1$에 대해 위 분율의 상계

$$
O_{r,\varepsilon}\!\left(\frac{\log\log\log X}{\log\log X}\right)
$$

도 얻는다. 이는 충분히 큰 $X$에 대한 점근 상계이며 명시적 시작점은 계산하지 않았다.

## 2. 무조건 큰 소수 손실 합산

정수 $X\ge3$과 실수 $y>1$에 대해

$$
L_y(n)=\#\{k<n:\text{어떤 소수 }q>y\text{가 }a_k\text{와 }n\text{을 모두 나눈다}\}
$$

로 두자. 모든 $2\le n\le X$에서 정의하며, 겹치는 소수는 한 항을 한 번만 세게 한다.
또 $C_q(X)=\#\{k<X:q\mid a_k\}$라 두면

$$
\tag{1}\boxed{\sum_{2\le n\le X}L_y(n)
\le\frac{X^2\log X}{y\log y}.}
$$

*증명.* 합집합 상계와 합 순서 교환으로 왼쪽은

$$
\sum_{q>y}\sum_{\substack{k<X\\q\mid a_k}}
\left(\left\lfloor\frac Xq\right\rfloor-
\left\lfloor\frac kq\right\rfloor\right)
\le\sum_{q>y}\left\lfloor\frac Xq\right\rfloor C_q(X)
\le\frac Xy\sum_{q>y}C_q(X)
$$

이하이다. L1에 의해 $1\le a_k<X$이다. $a_k$가 $y$보다 큰 서로 다른
소수를 $s$개 가지면 $y^s\le a_k<X$이므로 $s\le\log X/\log y$이다.
따라서 $\sum_{q>y}C_q(X)\le X\log X/\log y$이며 (1)이 따른다. □

여기서는 특정 $q$에 대한 등분포도, 반복 횟수의 상계도 가정하지 않았다.
한 소수에서 손실이 클 가능성은 남아 있지만, 큰 소수들을 공유하는
인덱스들에 대한 손실의 합은 위 부등식으로 제한된다.

## 3. 작은 소인수가 없는 인덱스에서 예외를 센다

$P^-(n)$을 $n\ge2$의 최소 소인수라고 하자. $P^-(n)>y$이면
원래 점화식에서 **정확히**

$$
\tag{2}a_n=n-1-L_y(n).
$$

또 곱의 기본 부등식으로, $n\le X$이고 $P^-(n)>y$일 때

$$
\tag{3}0\le1-\frac{\varphi(n)}n
\le\sum_{q\mid n}\frac1q\le\frac{\log X}{y\log y}.
$$

충분히 큰 $X$에서
$h=X/(\log X)^2$, $y=(\log X)^4$로 선택한다.
(3)의 오른쪽은 0으로 가므로, 고정 $0<\varepsilon<1$에 대해
$P^-(n)>y$인 모든 $n\le X$에서 $a_n/\varphi(n)>1+\varepsilon$은
충분히 큰 $X$에서 불가능하다. 실제로 $a_n<n$이고
$n/\varphi(n)\le(1-\log X/(y\log y))^{-1}\to1$이다.

반대로 $n\ge h$이고 $a_n/\varphi(n)<1-\varepsilon$이면

$$
L_y(n)=n-1-a_n>\varepsilon n-1\ge\varepsilon h/2
$$

이다. 마지막 부등식은 충분히 큰 $X$에서 성립한다. 따라서 (1)과 마르코프 부등식으로

$$
\tag{4}\#\{h\le n\le X:P^-(n)>y,
\ |a_n/\varphi(n)-1|>\varepsilon\}
\le\frac{2X^2\log X}{\varepsilon h y\log y}
\ll_\varepsilon\frac{X}{\log X\log\log X}.
$$

이 단계의 유일한 수열 관련 가정은 원래 점화식과 L1의 값 범위이다.

## 4. 거의소수 중 작은 소인수를 가진 수는 상대적으로 드물다

사용하는 기존 결과를 명시한다. 고정된 정수 $j\ge1$에 대한 Landau 정리는

$$
\tag{5}A_j(T)\sim\frac{T}{\log T}
\frac{(\log\log T)^{j-1}}{(j-1)!}.
$$

또 소수 역수 합의 Mertens 상계는
$\sum_{p\le Y}1/p=\log\log Y+O(1)$이다.
두 결과의 진술은 Paul Kinlaw,
[“Lower Bounds for Numbers with Three Prime Factors”, INTEGERS 19 (2019), #A22](https://math.colgate.edu/~integers/t22/t22.pdf)의
서론과 Lemma 2에서 확인했다. 이 고전 정리들은 여기서 새로 증명한 결과가 아니다.

$r\ge2$를 고정한다. $\Omega(n)=r$이고 $P^-(n)\le y$이면
어떤 소수 $p\le y$에 대해 $n=pm$, $\Omega(m)=r-1$이다.
중복 소인수가 있는 경우에도 이 등식은 성립한다. 따라서

$$
B_r(X,y):=\#\{n\le X:\Omega(n)=r,\ P^-(n)\le y\}
\le\sum_{p\le y}A_{r-1}(X/p).
$$

$y=(\log X)^4$에서는 $X/p\ge X/y\to\infty$이고
$\log(X/p)\sim\log X$가 이 범위에서 균일하다.
(5)의 고정 $r-1$ 상계를 적용하면

$$
\begin{aligned}
B_r(X,y)
&\ll_r\frac{X(\log\log X)^{r-2}}{\log X}
\sum_{p\le y}\frac1p\\
&\ll_r\frac{X(\log\log X)^{r-2}\log\log\log X}{\log X}.
\end{aligned}
$$

(5)로 나누면

$$
\tag{6}\frac{B_r(X,y)}{A_r(X)}
\ll_r\frac{\log\log\log X}{\log\log X}\longrightarrow0.
$$

## 5. 세 예외 집합을 합한다

$\Omega(n)=r$이고 비율 오차가 $\varepsilon$보다 큰 $n\le X$는
다음 세 집합 중 하나에 속한다.

1. $n<h$: 전체 정수 개수로도 $h=X/(\log X)^2$ 이하.
2. $P^-(n)\le y$: (6)으로 $o(A_r(X))$개.
3. $h\le n\le X$, $P^-(n)>y$: (4)로 $O_\varepsilon(X/(\log X\log\log X))$개.

첫 번째와 세 번째도 (5)에 의해 각각 $o(A_r(X))$이다.
구체적으로 $A_r(X)$로 나눈 크기는
$O_r(1/(\log X(\log\log X)^{r-1}))$와
$O_{r,\varepsilon}(1/(\log\log X)^r)$이다.
이를 합하면 1절의 정리와 명시한 점근 상계가 증명된다.
$\varepsilon\ge1$의 경우는 더 작은 양의 $\varepsilon$에 대한 결과에서 따른다. □

## 6. 검증과 남은 문제

본 명제의 전칭 범위를 고정 소인수 개수의 상대밀도 결과로 바꾼 것이 아니라,
**원래 본 명제를 그대로 두고 부분 정리를 추가**한 것이다.
예를 들어 $n=2p$인 인덱스는 2-거의소수 안에서도 상대밀도가 0이다.
그러므로 이 정리는 그 부분수열 전체의 수렴이나 $p=2$ 배수 밀도를 해결하지 못한다.
소인수 개수가 증가하는 일반 인덱스, 평균 조건 (A), D022의 반복 제곱합 상계도 미증명이다.

더욱이 (1)과 같은 논증은 원래 수열 대신 임의의 양의 정수열
$b_1=1$, $1\le b_k<k$($k\ge2$)을 놓고
$T_b(n)=\#\{k<n:(b_k,n)=1\}$로 두어도 성립한다.
즉 이번 결과는 **값 범위와 큰 소인수의 희소성**에서 나오는 부분 결과이며,
자기 참조의 핵심 균형을 새로 증명한 것으로 평가하지 않는다.

[재현 코드](rough_index_average.py)는 실제 수열에서 (1)의 합집합 상계와
이중 계수 상계를 정수로 점검하고, (2)를 작은 소인수가 없는 인덱스마다 확인한다.
또 $\Omega(n)=1,2,3,4$에서 유한 오차 비율을 보고한다.
계산용 절단값 10, 30, 100과 증명의 점근 절단값 $(\log X)^4$를 구별한다.
[첫 $10^6$항 결과](rough_index_average_1m.json)와 첫 3,000항의 정의 직접 대조는
유한 검산일 뿐 (5)나 극한의 근거를 대체하지 않는다.

자체 검토에서는 $\Omega$의 중복 포함, 초기항, 손실의 합집합 중복,
$k<n\le X$의 합 순서, 작은 소인수의 중복 계수 허용,
Landau 상계의 적용 범위 $X/p\ge X/y\to\infty$,
상대 오차의 분모와 세 예외 집합의 크기를 점검했다.
독립 검토와 Lean 형식화는 수행하지 않았다. 문헌상 최초성은 주장하지 않는다.
