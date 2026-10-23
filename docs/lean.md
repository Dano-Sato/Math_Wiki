# Lean 라이브러리

Lean 4와 Mathlib **v4.35.0**을 사용하는 `MathWiki` 라이브러리다.
`lean-toolchain`은 Lean 버전을, `lake-manifest.json`은 의존성의 정확한 커밋을 고정한다.

## Windows에서 시작하기

Git for Windows와 PowerShell이 필요하다. 저장소 루트에서 실행한다.

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup_lean.ps1
```

이 스크립트는 공식 Elan v4.2.4를 통해 `.tools/elan/`에 Lean을 설치하고,
Lake 의존성과 필요한 Mathlib 컴파일 캐시를 내려받은 뒤 라이브러리를 빌드한다.
도구와 캐시는 이 저장소 안에 두며 시스템 PATH를 영구 변경하지 않는다.
현재 프로세스의 Git HTTPS 검증은 Windows 인증서 저장소를 사용한다.
이미 설치된 환경에서는 같은 명령을 다시 실행할 수 있다.

이후 빌드와 개별 파일 확인:

```powershell
.\scripts\lake.ps1 build
.\scripts\lake.ps1 env lean MathWiki/Basic.lean
```

VS Code에서는 추천 확장 `leanprover.lean4`를 설치하고, 아래 셸에서 저장소를 연다.
VS Code가 이미 실행 중이면 종료 후 다시 열어 환경 변수를 전달한다.

```powershell
. .\scripts\lean_env.ps1
code .
```

현재 셸에서는 `lean`, `lake`, `elan`도 직접 사용할 수 있다.
PowerShell 실행 정책으로 스크립트가 차단되면 새 셸을
`powershell -ExecutionPolicy Bypass`로 열고 위 명령을 실행한다.

## 다른 환경

Linux/macOS 또는 전역 Elan이 있는 환경에서는 저장소 루트에서 실행한다.

```bash
lake exe cache get Mathlib.Data.Finset.Card
lake build
```

첫 실행 시 `lean-toolchain`과 manifest에 맞는 도구·의존성을 복원한다.

## 구성과 추가 원칙

- `MathWiki.lean`: 외부에서 `import MathWiki`로 사용하는 공개 진입점.
- `MathWiki/Basic.lean`: 유한 집합에서 조건을 만족하는 원소 수와 기본 성질.
  Mathlib 결과를 감싼 기반 코드이며 저장소의 독창적인 정리로 주장하지 않는다.
- `.github/workflows/lean.yml`: Lean 소스·의존성 변경 시 GitHub에서 빌드.
- `.tools/`, `.lake/`: 로컬 도구와 빌드 산출물. Git에 포함하지 않는다.

새 모듈은 `MathWiki/<주제>/<이름>.lean`에 두고, 공개할 때 `MathWiki.lean`에 import한다.
`Basic.lean`처럼 `module`과 공개 선언을 사용해 Lean 모듈 시스템을 따른다.
특정 추측에서 추출한 결과에는 모듈 설명에 원본 번호·명제 버전·증명 출처를 적는다.
먼저 `coordination.py`로 원본 번호와 라이브러리 전용 `LEAN`을 함께 점유한다.

```powershell
python coordination.py claim 005 LEAN --mode formalize --owner codex-lean-worker-1 --task "005의 증명된 보조정리 형식화"
```

공통 기반 모듈은 `LEAN`만 점유한다. `MathWiki.lean` 갱신과 빌드·검증도 `LEAN` 범위다.
도구·의존성·CI 설정 변경에는 `ROOT`와 `LEAN`을 함께 점유한다.
형식화 완료 시 원본 토론에 모듈과 검증 상태를 기록하고, 저장·검증 후 점유를 해제한다.
세부 기준은 [AGENTS.md 8절](../AGENTS.md#8-lean-형식화-절차)을 따른다.

공개 정리는 완성된 증명을 가져야 한다. `sorry`, `admit`, 미해결 추측을 가정하는
사용자 정의 `axiom`은 허용하지 않는다. 빌드는 경고를 오류로 처리한다.
미해결 명제는 필요하면 `def ... : Prop`으로 진술하고 미해결임을 문서화한다.
유한 검산에는 범위를 정리의 가정에 명시한다.

현재는 기반 모듈만 있으며, 개별 추측의 결과를 옮기는 작업은 별도로 진행한다.

## 의존성 변경

새 Mathlib import에 대한 캐시가 필요하면 모듈 이름을 지정한다.

```powershell
.\scripts\lake.ps1 exe cache get Mathlib.Data.Nat.Prime.Basic
```

필요하면 `exe cache get`으로 전체 캐시를 받을 수도 있다.
버전 업그레이드는 Mathlib 태그와 해당 태그의 `lean-toolchain`을 함께 바꾸고
`lake update` 및 빌드를 실행한다. 바뀐 `lake-manifest.json`도 함께 기록한다.

공식 참고: [Lean 설치 안내](https://docs.lean-lang.org/lean4/doc/quickstart.html),
[Mathlib](https://github.com/leanprover-community/mathlib4),
[Elan](https://github.com/leanprover/elan).
