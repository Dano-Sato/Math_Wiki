# 046 · 연결 지배 집합 크기 분포의 단봉성

> 연결된 그래프의 연결 지배 집합을 크기별로 세면, 그 개수는 한 봉우리만 가질까?

| 항목 | 내용 |
| --- | --- |
| ID | 046 |
| 버전 | 0.1 |
| 제안일 | 2026-10-26 |
| 제안자 | Codex — 사용자의 새 추측 탐색 요청에 따라 구성 |
| 분야 | 그래프 이론 · 연결 지배 집합 · 그래프 다항식 |
| 깊이 | 2 · 연구 수준 후보 (Codex 추정, 경계 평가) |
| 상태 | 미증명 · 모든 연결 단순 그래프 $n\le6$ 전수 확인 |
| 독창성 | 이 프로젝트에서 새로 구성한 후보. 제한 검색에서 정확히 같은 보편 단봉성 명제는 찾지 못했으나 문헌상 신규성은 미확정 |
| 토론 | [discussion.md](discussion.md) |

## 정의와 추측

유한 단순 연결 그래프 $G=(V,E)$에서 $S\subseteq V$가 **연결 지배 집합**이라는 것은 유도 부분그래프 $G[S]$가 연결이고, 모든 $v\in V$가 $S$의 어떤 정점과 같거나 인접하다는 뜻이다. $c_k(G)$를 크기 $k$인 연결 지배 집합의 개수로 두고

$$D_c(G,x)=\sum_{k=1}^{|V|}c_k(G)x^k$$

를 연결 지배 다항식이라 하자.

**추측 046.** 모든 유한 단순 연결 그래프 $G$에 대해 계수열

$$c_1(G),c_2(G),\ldots,c_{|V|}(G)$$

은 단봉이다. 즉 어떤 $m$이 있어 $c_1\le\cdots\le c_m\ge c_{m+1}\ge\cdots\ge c_{|V|}$이다. 0인 계수도 그대로 포함한다.

## 예비 검산

모든 연결 단순 그래프를 꼭짓점 수 $1\le n\le6$에서 라벨이 있는 그래프 전체로 열거하고, 각 꼭짓점 부분집합이 연결 지배 집합인지 직접 검사했다. 모두 27,476개의 연결 그래프에서 계수열의 단봉성에 반례가 없었다. 검산은 유한 범위의 증거일 뿐 일반 증명은 아니다. 재현 코드는 [verify.py](verify.py), 결과는 [experiment.json](experiment.json)에 있다.

## 문헌 확인 범위와 한계

2026-10-26에 `connected domination polynomial unimodal conjecture`, `connected domination polynomial unimodality trees`, `connected dominating sets coefficient sequence unimodal`을 검색했다. 연결 지배 다항식의 정의와 특정 그래프 족의 계산, 2026년의 근 분포 연구를 확인했지만, 이 다항식의 모든 연결 그래프에 대한 계수 단봉성을 추측으로 명시한 결과는 제한 검색에서 발견하지 못했다. 일반 지배 다항식의 단봉성은 Alikhani–Peng의 기존 추측이므로 본 명제와 구별해야 한다. 검색 범위는 제한적이며 문헌상 최초를 주장하지 않는다.

관련 배경: [Mojdeh–Emadi, Connected Domination Polynomial of Graphs (2018)](https://doi.org/10.1515/fascmath-2018-0007), [Shao–Zhao, On the Roots of Connected Domination Polynomials (2026)](https://arxiv.org/abs/2609.06569), [Galvin–Zhang, The domination polynomial of powers of paths and cycles (2024)](https://arxiv.org/abs/2408.12731).

## 열린 질문

- 추측 046의 증명 또는 반례가 있는가?
- 단봉성보다 강한 로그오목성이 성립하는 그래프 족은 무엇인가?
- 일반 지배 다항식의 기존 단봉성 문제와 연결 지배 다항식 사이에 유용한 환원이나 비교가 있는가?
