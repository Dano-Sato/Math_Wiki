# 029 · 균등 신장나무 평균 차수의 정수 반올림

| 항목 | 내용 |
| --- | --- |
| ID | 029 |
| 버전 | 0.2 |
| 제안일 | 2026-10-24 |
| 분야 | 그래프 이론 · 균등 신장나무 · 차수 반올림 |
| 상태 | 미증명 · 작은 차수 그래프 전수검사 통과 |
| 독창성 | 정확한 바닥·천장 명제는 제한 검색에서 찾지 못함. 인접한 일반 차수 반올림 정리와 구분되며 문헌상 최초를 주장하지 않음 |
| 검증 | [기본 유한 탐색](floor_ceil_experiment.json), [구조적 그래프 탐색](structured_experiment.json), [밀도별 무작위 탐색](density_experiment.json) |
| 토론 | [토론 기록](discussion.md) |

## 정의 및 추측

유한 연결 단순 그래프 $G=(V,E)$에서 균등하게 뽑은 신장나무를 $T$라 하고,
$\mu_v=\mathbb E[\deg_T(v)]$라 두자. 그러면 어떤 하나의 신장나무 $T_0$가 존재해 모든 꼭짓점 $v$에 대해

$$
\boxed{\deg_{T_0}(v)\in\{\lfloor\mu_v\rfloor,\lceil\mu_v\rceil\}}
$$

를 동시에 만족한다고 추측한다. $\mu_v$가 정수이면 허용 차수는 그 정수 하나뿐이다. 본 추측은 각 꼭짓점을 따로 근사하는 것이 아니라 하나의 신장나무가 전 꼭짓점의 바닥·천장 선택을 동시에 실현한다고 말한다.

UST의 평균은 직접 신장나무를 세어 정의할 수 있다. 동치로 Kirchhoff 유효저항 공식에 의해 $\mu_v=\sum_{e\ni v}R_{\mathrm{eff}}(e)$이다. 이 공식과 UST에서 간선 포함 확률의 전기적 표현은 [Kirchhoff 유효저항 공식에 대한 자료](https://math.utah.edu/~alberts/notes/burton-pemantle/)에서 확인할 수 있다.

## 유한 계산

[재현 스크립트](explore_floor_ceil.py)는 Prüfer 부호로 신장나무를 열거하고, 평균 차수의 분모를 유지한 정수 비교로 조건을 검사한다.

- $n=2,3,4,5,6$의 모든 연결 단순 그래프를 전수검사했다.
- 추가로 고정 시드 무작위 표본 $n=7$ 2,000개와 $n=8$ 500개를 검사했다.
- 추가 밀도 실험으로 $n=7$ 4,000개와 $n=8$ 800개 연결 그래프를 검사했다.
- 구조적으로 만든 $n=7$ 그래프 230개와 $n=8$ 그래프 269개도 각각 모든 신장나무를 열거해 검사했다. 완전 이분·다분 그래프, 1–3개 간선 절단으로 두 clique를 연결한 그래프, cycle에 무작위 chord를 더한 그래프, 간선을 일부 제거한 완전 그래프를 포함한다.
- 각 구조적 그래프에서 허용된 바닥·천장 차수 벡터가 총 차수 합과 부분집합 필요조건 $d(S)\le 2\min(|S|-1,|E_G(S)|)+|\delta_G(S)|$를 만족할 수 있는지도 검사했다. 이 필요조건만으로 모든 허용 벡터를 제거한 사례는 없었다.
- 검사한 모든 그래프에서 조건을 만족하는 신장나무가 있었다.

정확한 그래프 수와 실행 정보는 JSON에 저장했다. 모든 계산은 유한 범위에 한정되며 증명이나 무한 범위의 근거로 취급하지 않는다.

## 문헌 중복 확인과 한계

Singh–Lau는 차수 하한 $A_v$와 상한 $B_v$를 둔 신장나무 최적화에서 각 제약을 최대 1만큼 위반하는 정리를 증명했다([원 논문 PDF](https://www.microsoft.com/en-us/research/wp-content/uploads/2017/01/mbdst.pdf), STOC 2007). 더 일반적인 iterative/randomized rounding 연구도 fractional spanning tree의 꼭짓점 차수에 대해 상한 $\lceil x(\delta(v))\rceil+1$ 형태를 언급한다([Chekuri–Vondrák–Zenklusen, *On a Generalization of Iterated and Randomized Rounding*](https://theoryofcomputing.org/articles/v020a006/v020a006.pdf)). 이 결과들은 본 명제 그대로가 아니며, 바닥·천장 두 값 중 하나로 모든 평균 차수를 동시에 맞추는 보장은 확인한 결과의 직접적인 결론이 아니다. 차수 제한 신장나무의 정수 실현 가능성과 반올림은 밀접한 선행 주제이므로 이 인접성을 독창성 평가에 반영한다.

“spanning tree degree floor ceiling fractional rounding”, “simultaneous degree rounding”, “fractional spanning tree degree-vector rounding” 등으로 제한 검색했으나, 균등 신장나무 평균 차수에 대한 정확한 동시 바닥·천장 명제나 이를 이미 해결하는 정리를 찾지 못했다. 2026년의 degree-constrained spanning tree 연구는 각 꼭짓점에 허용 차수 목록을 주는 일반 문제까지 다루지만, UST 평균으로부터 이 특정 목록이 실현되는지는 별도 질문이다([ICALP 2026 논문](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ICALP.2026.38)). 이는 전수 문헌 검색이 아니며 신규성을 확정하지 않는다. 알려진 미해결문제의 이름을 바꾼 명제로 제시하는 것도 아니다. 더 일반적인 fractional spanning-tree degree-vector 반올림 문헌의 인용 추적을 계속하면 중복 여부가 달라질 수 있다.

## 이전 후보의 정정

버전 0.1은 $|\deg_T(v)-\mu_v|\le1$를 주장했으나, 이는 Singh–Lau의 정리에서 fractional UST edge vector를 입력으로 하여 따르는 결과로 확인되어 본 추측에서 제외했다. 해당 후보와 그 유한 탐색은 기록 보존을 위해 `experiment.json`과 `explore.py`에 남겨 두었다. 본 버전은 더 강한 바닥·천장 반올림 문제로 대체한다.
