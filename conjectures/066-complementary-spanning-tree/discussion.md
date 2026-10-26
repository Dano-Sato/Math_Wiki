# 066 토론 및 검증 기록

## 2026-10-27 · Codex · 사용자 제안 CST 후보 등록

**등록 판단.** 연구 수준 후보로 가치가 있다고 판단해 066으로 잠정 등록한다. 이 문서는 사용자에게서 전달된 CST, Tree-CST, TR, RDM을 분리해 보존한다. 증명이나 유한 검산을 확인하지 못한 전달 주장은 아래에서 CLAIMED로 표시한다.

**기존 위키 대조.** 저장소의 추측 문서에서 CST와 같은 보수 신장나무 곱 하한은 찾지 못했다. 029는 균등 신장나무의 꼭짓점별 평균 차수를 하나의 정수 신장나무로 반올림하는 명제다. 같은 분야 도구를 쓰지만 명제는 다르고 서로의 증명이 아니다.

**문헌 대조 (제한 검색).**

- [Kelmans, “Comparison of graphs by their number of spanning trees” (1976)](https://doi.org/10.1016/0012-365X(76)90102-3): 같은 정점·간선 수를 갖는 그래프를 대상으로 신장나무 수를 올리거나 내리는 변환을 연구한다. 이것만으로 $\tau(G)\tau(\bar G)$의 단조성이나 CST를 얻을 수는 없다.
- [Csikvári, “On a poset of trees”](https://csikvarip.web.elte.hu/csikvarin2002uj.pdf): generalized tree shift가 유도하는 나무 부분순서와 거리합·닫힌 보행을 다룬다. 나무를 옮길 때 보수의 신장나무 수가 단조라는 명제는 해당 논문에서 확인하지 못했다.
- [“The number of spanning trees of a graph” (2013)](https://link.springer.com/article/10.1186/1029-242X-2013-395): 연결 그래프와 연결 보수에서 신장나무 수의 합에 대한 Nordhaus–Gaddum형 상계를 제시한다. CST의 곱 하한과는 다른 방향·대상이다.
- [The Number of Spanning Trees in Kn-complements of Quasi-threshold Graphs](https://arxiv.org/abs/cs/0502038): 특정 그래프족에서 보수형 행렬식 공식과 신장나무 수 공식을 다룬다. 일반 CST 하한은 확인하지 못했다.

정확한 식을 검색한 초기 문헌 확인에서 동일한 추측을 찾지 못했지만, 검색 범위는 위 자료와 제한된 검색어에 한정된다. 독창성은 잠정이며 최초 제안은 주장하지 않는다.

**사용자 제공 주장과 검증 상태.**

| 항목 | 현재 상태 | 근거 / 한계 |
| --- | --- | --- |
| CST, 등호 분류 | CLAIMED | 사용자가 진술. $n\le7$ 전수 검산의 코드·출력은 제공되지 않아 재현하지 않음 |
| Tree-CST와 relocation/Kelmans/Csikvári/RDM 증명 | CLAIMED | 증명 본문이 제공되지 않아 Schur 보수, 부호, 엄격성, relocation 종료를 감사하지 못함 |
| TR 일반형 | CLAIMED open problem | 사용자 진술. 완전한 증명·반례 자료 없음 |
| unicyclic/cactus/theta/bicyclic의 TR 부분 증명 | CLAIMED | 해당 증명과 입력 사례가 없어 검증하지 못함 |
| 균등평균 TR 및 탐욕 단일 간선 하강 반례 | CLAIMED | 구체 반례 그래프·코드가 제공되지 않음 |
| 강한 Hadamard 충분조건의 실패 | CLAIMED | 구체 반례가 제공되지 않음 |
| RDM, 모든 단순 $F$, $2\le m\le5$ | COMPUTATIONALLY VERIFIED | audit_rdm_exact.py; 1,098 그래프, degree 비교 7,292건, 정확 유리수 연산 |
| RDM 임의 크기 | CLAIMED / 미증명 | 유한 검산은 보편 명제 증명이 아님 |
| spectral/tree/double-star/TR 행렬식 식 | PROVED (항등식) | 아래의 짧은 유도. 이는 CST/TR의 전역 부등식을 증명하지 않음 |

**항등식 감사 스케치.** 라플라시안은 $L(\bar G)=nI-J-L(G)$이므로 $\mathbf1^\perp$에서 고유값이 $\lambda_i$와 $n-\lambda_i$로 짝을 이룬다. 행렬-나무 정리를 각각 적용하면 spectral product identity가 따른다. 나무의 oriented incidence matrix를 $D$라 하면 $L(T)=DD^\top$이고 비영 고유값은 $D^\top D$의 고유값이다. 나무의 선 그래프 incidence 부호를 블록별로 바꾸면 $D^\top D$는 $2I+A(\mathcal L(T))$와 대각 부호 유사하므로 $\prod_{i=2}^n(n-\lambda_i(T))=\det((n-2)I-A(\mathcal L(T)))$. 행렬-나무 정리로 나누기 $n$을 얻는다.

이중별 $D_{a,b}$의 선 그래프는 중앙 변 꼭짓점에 두 clique 블록이 붙은 모양이다. $q=n-2=a+b$라 하고 determinant의 두 clique 주대각 블록을 $X=(n-1)I_a-J_a$, $Y=(n-1)I_b-J_b$로 쓰면, Schur 보수로
$$
\det((n-2)I-A(\mathcal L(D_{a,b})))
=\det(X)\det(Y)\left(q-\frac{a}{b+1}-\frac{b}{a+1}\right)
=n ab(n-1)^{n-4}.
$$
행렬-나무 식에서 $n$으로 나누면 제시된 $\tau(\bar D_{a,b})$가 나온다. 따라서 $\tau(B_n)=1$과 $\tau(\bar B_n)=(n-3)(n-1)^{n-4}$도 확인된다.

TR determinant identity는 $L(\bar T)=L(H)+B_SB_S^\top$에서 reduced Laplacian에 matrix determinant lemma를 적용한다. $\det(I+B_S^\top L_H^+B_S)$는 PSD Gram 행렬이므로 Hadamard 부등식으로 대각 원소 곱 $\prod_e(1+R_H(e))$ 이하이다. 이 유도는 항등식과 상계는 증명하지만, 작은 저항을 갖는 변 집합 $S$와 그것의 여집합인 spanning tree의 동시 전역 선택은 보장하지 않는다.

**논리 점검.** $\bar G$ 연결은 $G$가 spanning star를 포함하지 않음을 보장한다. 따라서 TR에서 얻는 임의 신장나무에 Tree-CST를 적용할 수 있고, 두 명제는 CST의 수치 하한을 함의한다. 그러나 equality uniqueness는 추가 간선이 $\tau(G)$와 $\tau(\bar G)$에 미치는 효과 및 TR의 등호 조건을 따져야 하므로 별도 미해결점으로 남긴다.

**RDM의 범위.** $F$의 꼭짓점 수를 $m$으로 해석할 때 $\lambda_{\max}(L(F))\le m$이므로 $M=(m+1)I-L(F)$는 양의 정부호다. 완전 탐색 결과는 이 가정 아래 $m\le5$의 모든 라벨 그래프에서 엄격 단조를 보인다. 이 검산은 원래 주장된 일반 Schur 보수 증명이나 Tree-CST의 relocation chain을 검증하지 않는다.

**Codex 자체 점수: 48점 / v0.1 / 2026-10-27.** 날카로운 extremal 목표, 명시된 equality family, determinant/effective-resistance 기반의 구체적 장벽 때문에 40–59 연구 문제 구간으로 평가한다. 다만 exact novelty는 미확정이고, 본 추측의 이전 증명·계산은 자료 부재로 감사되지 않았다. TR/RDM의 일반 증명도 없다. 이 점수는 참일 확률이 아니며 미증명 여부에 감점하지 않았다.

**다음에 필요한 자료.** 이전 proof를 감사하려면 relocation chain의 전체 논증(각 변환 전후 그래프, 적용 정리, strict inequality가 필요한 경우), RDM의 Schur-complement 유도, TR 부분 증명, 그리고 $n\le7$ 및 Tree-CST 검산 스크립트와 재현 가능한 출력이 필요하다. 수치 표만으로 일반 증명을 인정하지 않는다.

## 변경 이력

| 버전 | 날짜 | 변경 |
| --- | --- | --- |
| 0.1 | 2026-10-27 | 사용자 제안 CST, Tree-CST, TR, RDM 및 예비 문헌·검산 상태를 등록 |
| 점수 | 2026-10-27 | Codex 48점(v0.1 기준); 상대 모델 미채점 |

## 2026-10-27 — 063 예비 폴더 정리

등록을 보류했던 063 폴더의 RDM 예비 스크립트 2개를 udit-history/063-preliminary/로 옮겨 보존했다. 정확 유한 감사 스크립트는 066의 재현 스크립트와 목적이 겹치며, 무작위 탐색 스크립트는 시드를 고정하지 않아 재현 가능한 증거로 취급하지 않는다. 063 원 폴더는 비웠다가 제거했다. 기존 CST 상태나 결론은 변경하지 않았다.

