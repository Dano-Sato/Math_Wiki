# 평균 절댓값 근사에서 고정 약수의 배수 밀도로

대상: 004 v0.9의 원래 수열 $a_1=1$, $a_n=\#\{k<n:(a_k,n)=1\}$.
작성: Codex, 2026-10-27. **조건부 정리의 증명 · 자체 검토 완료(독립 검토 미수행).**
Lean 형식화는 수행하지 않았다. 본 추측 004와 아래 가정 (A)는 여전히 미증명이다.

## 정리

L15의 평균 절댓값 근사 조건

$$
\tag{A}\sum_{k\le N}|a_k-\varphi(k)|=o(N^2)
$$

를 가정하면, 모든 고정된 제곱인수 없는 정수 $d\ge1$에 대해

$$
\boxed{\#\{k\le N:d\mid a_k\}=\frac Nd+o_d(N).}
$$

따라서 004-2가 성립한다. 또한 소인수가 고정된 유한 집합 $S$ 안에만 있는
$n\to\infty$에 대해서는 $a_n/\varphi(n)\to1$이다.

여기서 배수 밀도란 $d\mid a_k$의 빈도를 뜻한다. $a_k$의 모든 잔여류가
동일한 빈도로 나타난다는 더 강한 주장은 하지 않는다.

## 1. 배수 인덱스에서 합을 뒤집는 무조건 항등식

$b_k=\varphi(a_k)/a_k$라 두자. L1에 의해 $a_k\ge1$이므로 정의된다.
모든 고정 정수 $m\ge1$에 대해

$$
\tag{1}
\sum_{\substack{n\le N\\m\mid n}}a_n
=\mathbf1_{m=1}
+\frac1m\sum_{k<N}(N-k)b_k\mathbf1_{(a_k,m)=1}
+O_m(N^{3/2}).
$$

실제로 $n\ge2$에서 원래 점화식을 합하고 합 순서를 바꾼다.
$(a_k,m)>1$인 항은 $m\mid n$인 어떤 $n$과도 서로소가 아니다.
$(a_k,m)=1$이면 $n=m\ell$에 대해 $(a_k,n)=1$과 $(a_k,\ell)=1$이 동치다.
따라서 정확히

$$
\tag{2}
\sum_{\substack{n\le N\\m\mid n}}a_n-\mathbf1_{m=1}
=\sum_{\substack{k<N\\(a_k,m)=1}}\sum_{e\mid a_k}\mu(e)
\left(\left\lfloor\frac{N}{me}\right\rfloor
-\left\lfloor\frac{k}{me}\right\rfloor\right).
$$

바닥함수를 주항으로 바꾸면 안쪽 합은 $(N-k)b_k/m$이고,
오차는 항별로 $\tau(a_k)$ 이하이다. $a_k<k$($k\ge2$), $a_1=1$,
$\tau(u)\le2\sqrt u$로 전체 오차가 $O(N^{3/2})$임을 얻는다.
$\mathbf1_{m=1}$은 점화식을 적용하지 않는 초기항 $a_1$을 따로 센 것이다.

## 2. (A)가 결정하는 토션트 가중 밀도

$c=6/\pi^2=1/\zeta(2)$와
$c_m=c\prod_{p\mid m}p/(p+1)$라 두자. 표준적인 토션트 합 계산은

$$
\tag{3}
\sum_{\substack{n\le N\\m\mid n}}\varphi(n)
=\frac{c_m}{2m}N^2+O_m(N\log N)
$$

을 준다. 필요한 계산을 직접 적으면, $\varphi(n)=n\sum_{e\mid n}\mu(e)/e$에서
$m$과 $e$의 최소공배수 $L=[m,e]$를 써서

$$
\sum_{\substack{n\le N\\m\mid n}}\varphi(n)
=\sum_{e\le N}\frac{\mu(e)}e
\left(\frac{N^2}{2[m,e]}+O(N)\right).
$$

오차합은 $O(N\log N)$이고, 주항의 계수는

$$
\frac1m\sum_{e\ge1}\frac{\mu(e)(e,m)}{e^2}
=\frac1m\prod_{p\mid m}(1-1/p)\prod_{p\nmid m}(1-1/p^2)
=\frac{c_m}{m}.
$$

무한합으로 늘린 꼬리의 영향은 $O_m(N)$이다.
이 부분은 기존 Möbius 공식과 Euler 곱의 직접 적용이다.

(A)는 (3)의 $\varphi(n)$을 $a_n$으로 바꿀 때의 오차도 $o(N^2)$로 제어한다.
(1)에 대입하면

$$
\sum_{k<N}(N-k)b_k\mathbf1_{(a_k,m)=1}
=\frac{c_m}{2}N^2+o_m(N^2).
$$

$B_m(t)=\sum_{k\le t}b_k\mathbf1_{(a_k,m)=1}$는 단조 증가하고,
왼쪽은 $\sum_{t<N}B_m(t)$이다. L14와 같은 단조성 논증을 적용하면

$$
\tag{4}
\frac1N\sum_{k\le N}b_k\mathbf1_{(a_k,m)=1}\longrightarrow c_m.
$$

구체적으로 $N$과 $(1+\varepsilon)N$에서 누적합의 차이를 취하면
$\limsup B_m(N)/N\le c_m(1+\varepsilon/2)$이고,
$(1-\varepsilon)N$과 $N$의 차이를 취하면
$\liminf B_m(N)/N\ge c_m(1-\varepsilon/2)$이다.
$\varepsilon\downarrow0$으로 보내면 (4)가 따른다.

제곱인수 없는 $d$에 대해 유한 포함배제를 적용하면

$$
\tag{5}
\frac1N\sum_{\substack{k\le N\\d\mid a_k}}b_k
\longrightarrow\sum_{m\mid d}\mu(m)c_m
=c\prod_{p\mid d}\frac1{p+1}.
$$

이것은 아직 가중 밀도다. $b_k$를 양의 상수로 대체하거나, 가중치를
무턱대고 나누면 안 된다. $b_k$에는 균일한 양의 하한이 없기 때문이다.

## 3. 유한 Euler 곱으로 가중치를 제거한다

$z\ge2$, $P_z=\prod_{p\le z}p$,
$b_z(u)=\prod_{\substack{p\le z\\p\mid u}}(1-1/p)$,
$w_{z,k}=b_k/b_z(a_k)$라 두자. 그러면 **모든 $k$에서**

$$
0<w_{z,k}\le1.
$$

(4)와 (5)를 조합하면 $P_z$를 나누는 각 소수의 가분성 패턴 $T$에 대한
$b_k$ 가중 밀도는

$$
c\prod_{p\in T}\frac1{p+1}
\prod_{\substack{p\le z\\p\notin T}}\frac{p}{p+1}
$$

이다. 패턴 $T$에서 $b_z(a_k)^{-1}=\prod_{p\in T}p/(p-1)$이므로,
유한 개의 패턴을 합하여

$$
\tag{6}
\frac1N\sum_{k\le N}w_{z,k}\longrightarrow
M_z:=c\prod_{p\le z}(1-p^{-2})^{-1}
=\prod_{p>z}(1-p^{-2}).
$$

특히 $M_z\uparrow1$이다. 같은 유한 패턴 계산에서 $d\mid P_z$이면

$$
\tag{7}
\frac1N\sum_{\substack{k\le N\\d\mid a_k}}w_{z,k}
\longrightarrow\frac{M_z}{d}.
$$

각 $p\mid d$에서, 전체 국소 인자 $p^2/(p^2-1)$ 대신
가분인 경우의 인자 $p/(p^2-1)$만 남기므로 정확히 $1/p$씩 곱해진다.
마지막으로 $0\le1-w_{z,k}\le1$에서

$$
0\le\frac{\#\{k\le N:d\mid a_k\}}N
-\frac1N\sum_{\substack{k\le N\\d\mid a_k}}w_{z,k}
\le1-\frac1N\sum_{k\le N}w_{z,k}.
$$

고정된 $d$의 모든 소인수를 포함하도록 $z$를 고르면 (6), (7)에 의해

$$
\frac{M_z}{d}\le\liminf_{N\to\infty}\frac{\#\{k\le N:d\mid a_k\}}N
\le\limsup_{N\to\infty}\frac{\#\{k\le N:d\mid a_k\}}N
\le\frac{M_z}{d}+1-M_z.
$$

이제 **$N\to\infty$를 먼저 취한 뒤** $z\to\infty$로 보내면 배수 밀도 $1/d$가 나온다.
움직이는 법 $d=d(N)$에 대한 균일 오차를 이 논증에서 얻은 것은 아니다.

고정된 유한 소수 집합 $S$에 대해 $P=\prod_{p\in S}p$라 하자.
$R\mid P$ 각각에서 포함배제로

$$
F_R(x):=\#\{k<x:(a_k,R)=1\}=\frac{\varphi(R)}R x+o_R(x)
$$

이다. $\operatorname{rad}(n)=R$이면 $a_n=F_R(n)$이고
$\varphi(n)/n=\varphi(R)/R$이다. $P$의 약수는 유한 개이므로
소인수가 $S$에만 있는 모든 $n\to\infty$에서 원하는 비율이 1로 간다. □

## 출처·검증·한계

기반은 원래 점화식, L1, L14의 합 순서 교환·단조성 논증,
[표준 토션트/Möbius 항등식](https://dlmf.nist.gov/27.2)과 $\zeta(2)$의 Euler 곱이다.
추가한 논증은 배수 인덱스의 평균을 이용한 (4), 그리고 (6)–(7)의 가중치 제거다.
별도의 소수 표본 점근식이나 독립성 가정을 사용하지 않는다.
문헌상 최초라는 주장은 하지 않는다. 수열에 관해서는
[OEIS A096216](https://oeis.org/A096216) 및 해당 번호를 이용한 검색을 확인했으며,
그 항목에 본 점근 추측이나 증명은 없었다. 이것은 완전한 문헌 조사가 아니다.

[재현 코드](weighted_residue_bridge.py)는 원래 점화식을 정수 포함배제로 계산하고
초기 구간을 정의의 최대공약수 계산과 대조한다. (2)의 정수 항등식과 (1)의
유한 오차 상계, 유한 패턴의 가중치 전개를 점검한다. 실행 범위와 관측값은
[결과](weighted_residue_bridge_100k.json)에 있다. 유한 계산으로 (A)나 극한을
검증했다고 해석하지 않는다.

**여전히 남은 문제:** (A)를 실제 점화식에서 증명하지 못했다. 또 위 결론은
고정된 유한 소수 집합에 대한 것이므로 $n$과 함께 변하는 큰 소인수와
포함배제 오차를 통제하지 않는다. 따라서 본 추측 004의 전체 증명이 아니다.
