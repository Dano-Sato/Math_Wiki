# Lean 라이브러리

Lean 4와 Mathlib **v4.35.0**을 사용하는 `MathWiki` 라이브러리다.
`lean-toolchain`은 Lean 버전을, `lake-manifest.json`은 의존성의 정확한 커밋을 고정한다.

## Windows에서 시작하기

Git for Windows와 PowerShell이 필요하다. 저장소 루트에서 실행한다.

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup_lean.ps1
```

이 스크립트는 공식 Elan v4.2.4를 통해 `.tools/elan/`에 Lean을 설치하고,
Lake 의존성과 Mathlib 전체의 사전 컴파일 캐시(`lake exe cache get`)를 내려받은 뒤
라이브러리를 빌드한다. 특정 import만 받던 방식과 달리 새 Mathlib import도 캐시를 활용한다.
도구와 캐시는 이 저장소 안에 두며 시스템 PATH를 영구 변경하지 않는다.
현재 프로세스의 Git HTTPS 검증은 Windows 인증서 저장소를 사용한다.
이미 설치된 환경에서는 같은 명령을 다시 실행할 수 있다.

설치와 빌드 래퍼는 `scripts/mathlib_cache.ps1`을 함께 사용한다.
최초 실행, `lean-toolchain` 또는 `lake-manifest.json` 변경, Mathlib 빌드 폴더 소실 시
캐시를 복원한다. 성공한 툴체인·manifest의 SHA256을 `.lake/mathlib-cache.key`에 기록하여
평소 빌드에서는 다운로드 명령을 생략한다. 기존 manifest가 있으면 고정된 커밋을 복원하고,
없을 때만 `lake update`로 의존성을 해결한다. 전체 캐시 다운로드에는 디스크 공간과 시간이 필요하다.

캐시 다운로드가 실패하면 빌드 전에 중단하고 성공 기록을 남기지 않는다. 같은 명령을 다시
실행하면 재시도한다. `MATHLIB_NO_CACHE_ON_UPDATE`는 중복 다운로드를 막기 위해 처리 중에만
설정하며 호출 전 값으로 복원한다. 이 변수는 래퍼의 명시적인 캐시 다운로드를 끄지는 않는다.

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
lake exe cache get
lake build
```

첫 실행 시 `lean-toolchain`과 manifest에 맞는 도구·의존성을 복원한다.

## 구성과 추가 원칙

- `MathWiki.lean`: 외부에서 `import MathWiki`로 사용하는 공개 진입점.
- `MathWiki/Basic.lean`: 유한 집합에서 조건을 만족하는 원소 수와 기본 성질.
  Mathlib 결과를 감싼 기반 코드이며 저장소의 독창적인 정리로 주장하지 않는다.
- `MathWiki/Combinatorics/CyclicCorrelation.lean`: 013 v0.1의 총 자기상관 항등식,
  반대 이동 대칭, 중심화 순열의 음의 이동 존재. 유한 가환군으로 일반화한 보조정리도 제공한다.
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

첫 원본 연계 모듈은 013의 L1·L2 보조 결과다. 본 추측의 모든 이동 동시 비양성은 미증명이다.
원본의 정수 라벨과 공개 API를 대조하는 검증은 다음으로 재현한다.

```powershell
.\scripts\lake.ps1 env lean -DwarningAsError=true conjectures/013-nonpositive-cyclic-correlation/check_lean.lean
```

## 의존성 변경

Windows에서는 Mathlib 태그(`lakefile.toml`)와 해당 태그의 `lean-toolchain`을 함께 바꾼 뒤 실행한다.

```powershell
.\scripts\lake.ps1 update
.\scripts\lake.ps1 build
```

`update` 성공 후 새 manifest에 맞는 캐시를 받고, 다른 환경에서 갱신한 manifest를 가져온 경우에도
다음 `build` 전에 변경을 감지한다. 바뀐 `lake-manifest.json`도 함께 기록한다.
`build`, `env`, `lean`, `test`, `lint`, `serve` 명령에 자동 복원을 적용한다.
도움말·버전 조회, `clean`, 직접 실행하는 `exe cache`는 그대로 Lake에 전달한다.
`--dir`/`-d`, `--file`/`-f`, `--packages`, `-K`, `--update`, `--no-cache` 같은
전역 옵션을 사용하는 고급 호출은 Lake 자체의 동작을 유지하며 래퍼의 자동 복원을 생략한다.
원시 `lake` 명령과 Linux/macOS에서는 필요할 때 직접 `lake exe cache get`을 실행한다.

개별 캐시를 다시 받으려면 모듈 이름을 지정할 수 있다.

```powershell
.\scripts\lake.ps1 exe cache get Mathlib.Data.Nat.Prime.Basic
```

전체 캐시를 다시 확인·복원하려면 `.\scripts\lake.ps1 exe cache get`을 실행한다.
의존성 빌드 산출물을 일부만 지웠다면 `.lake/mathlib-cache.key`를 지우고 빌드하여
자동 복원을 다시 수행할 수도 있다. 일반 `get`은 기존 캐시를 재사용하며 강제 덮어쓰기를 하지 않는다.

스크립트의 설치·캐시 갱신·실패 재시도·인자 전달은 임시 프로젝트와 가짜 도구로
네트워크 없이 검증할 수 있다. 실제 Lean 빌드는 별도로 `scripts/lake.ps1 build`로 확인한다.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test_lean_scripts.ps1
```

공식 참고: [Lean 설치 안내](https://docs.lean-lang.org/lean4/doc/quickstart.html),
[Mathlib](https://github.com/leanprover-community/mathlib4),
[Mathlib 캐시 안내](https://github.com/leanprover-community/mathlib4/blob/master/Cache/README.md),
[Elan](https://github.com/leanprover/elan).
