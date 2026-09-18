# Markdown Preview 프로젝트 분석 정리 (한국어)

> 작성일: 2026-09-18
> 이 문서는 Markdown Preview 저장소를 처음 받아본 사람을 위한 분석·정리 노트입니다.

## 저장소 주소

| 구분 | 주소 |
| --- | --- |
| 이 저장소 (포크) | https://github.com/bmshin94/markdown-preview |
| 원본(업스트림) | https://github.com/pluk-inc/markdown-preview |
| 릴리즈 다운로드 | https://github.com/pluk-inc/markdown-preview/releases |
| Homebrew Cask | https://formulae.brew.sh/cask/markdown-preview |
| 릴리즈 자동화 도구 (Amore) | https://amore.computer/ |
| 후원 | https://buymeacoffee.com/pluk |

---

## 1. 이게 뭔가요?

`.md`(마크다운) 파일을 macOS에서 빠르게 읽고 편집하는 **네이티브 macOS 앱의 소스코드**입니다.
완성된 앱이 아니라 앱을 만드는 설계도 전체(Xcode 프로젝트)입니다.

### 폴더 구조

| 경로 | 역할 |
| --- | --- |
| `md-preview/` | 메인 앱 타겟 (Swift + AppKit, 85개 파일 / 약 26,000줄) |
| `md-preview/Rendering/` | 마크다운 → HTML 렌더링 파이프라인 (핵심) |
| `md-preview/Features/` | Editor, Find, Inspector, Mermaid, OpenWith, Settings, Sidebar |
| `md-preview/Vendor/` | 번들 JS: Mermaid, KaTeX, highlight.js, CodeMirror, DOMPurify, Morphdom |
| `quick-look/` | Quick Look 확장 (Finder 스페이스바 미리보기) |
| `scripts/` | 릴리즈/롤백 자동화, 성능 벤치마크 |
| `tests/swift-tests/` | Swift 테스트 (WebKit 레이아웃 회귀 테스트 포함) |
| `.agents/skills/` | AI 에이전트용 스킬 4종 (`.claude/skills/`가 심볼릭 링크) |
| `AGENTS.md` / `CLAUDE.md` | AI 코딩 에이전트 작업 지침서 |
| `Version.xcconfig` | 버전 단일 소스 (현재 `0.0.58` / build `62`) |

### 주요 기능

- **네이티브 렌더링** — Electron 없이 `WKWebView` + Apple `swift-markdown`
- **Quick Look 확장** — Finder에서 스페이스바만 눌러도 미리보기
- **Edit Mode** (`⌘E`) — 서식 툴바를 갖춘 인플레이스 편집, `⌘S` 저장
- **Mermaid 다이어그램 / KaTeX 수식** — 번들 렌더러라 오프라인 동작
- **문서 아웃라인 사이드바**, 파일 내비게이터, 인스펙터 패널
- **문서 내 검색** (`⌘F` / `⌘G` / `⌘⇧G`)
- **Open With / Open in LLM** — 외부 에디터 또는 Codex·Claude·ChatGPT로 전달
- **CLI 툴** (`mdp`, `md-preview`, `markdown-preview`), **URL 스킴** (`md-preview://file/...`)
- 지원 확장자: `.md`, `.markdown`, `.mdown`, `.mdx`, `.txt`

### 어떨 때 쓰나요?

1. GitHub에서 받은 README를 원본 기호 없이 읽고 싶을 때
2. 에디터를 켜기 번거로울 때 문서 초안 확인
3. **AI가 생성한 마크다운 리포트**를 깔끔하게 읽을 때
4. Mermaid 다이어그램이 포함된 설계 문서 확인
5. Obsidian은 무겁고 브라우저 탭은 지저분할 때

> ⚠️ **macOS 15 이상 전용**입니다. Linux/Windows에서는 빌드·실행 모두 불가합니다.

---

## 2. 쉽게 다시 설명하면

마크다운은 **밀가루 반죽**이고 이 앱은 **오븐**입니다.
`# 제목`, `**굵게**` 같은 날것의 기호를 넣으면 → 제목·굵은 글씨·목록으로 구워서 보여줍니다.

세상에 오븐은 많지만,

- 브라우저형 (Typora 등) → 탭이 지저분함
- Electron형 (Obsidian, VS Code) → 메모리를 많이 씀
- **이 앱** → macOS 기본 부품만 써서 가볍고 즉시 실행

### 이 앱만의 포인트 3가지

1. **스페이스바 마법** — Finder에서 파일 선택 후 스페이스바만 눌러도 예쁜 미리보기 (`quick-look/` 담당)
2. **그림과 수식도 그려줌** — Mermaid 다이어그램, KaTeX 수식이 인터넷 없이도 렌더링 (`md-preview/Vendor/`에 라이브러리를 통째로 내장)
3. **AI로 바로 전달** — 툴바 버튼 하나로 현재 문서를 Claude/ChatGPT로 전달

---

## 3. 자주 묻는 질문

### 3.1 설치 및 사용법

**그냥 쓰고 싶다면 (권장)**

```sh
brew install --cask markdown-preview
```

또는 Releases 페이지에서 DMG 다운로드. 서명·공증이 되어 있어 보안 경고가 없습니다.

| 동작 | 방법 |
| --- | --- |
| 빠른 미리보기 | Finder에서 `.md` 선택 → 스페이스바 |
| 앱으로 열기 | 아이콘에 드래그 앤 드롭 |
| 터미널에서 열기 | `mdp README.md`, `mdp .` (메뉴에서 CLI 설치 후) |
| 편집 | `⌘E` → 수정 → `⌘S` |
| 검색 | `⌘F`, 다음 `⌘G`, 이전 `⌘⇧G` |
| 확대/축소 | `⌘+` / `⌘-` / `⌘0` (50%~300%) |

**소스에서 빌드하려면 (macOS 필요)**

```sh
git clone https://github.com/bmshin94/markdown-preview
cd markdown-preview
open md-preview.xcodeproj
# 테스트
swift test --package-path tests/swift-tests
```

첫 빌드 시 SPM이 Sparkle, Sentry, swift-markdown을 자동으로 받아옵니다.

### 3.2 플러그인인가요? 스킬인가요? MCP인가요?

**셋 다 아닙니다. 독립 실행형 macOS 데스크톱 앱입니다.**

| 개념 | 이 저장소는? |
| --- | --- |
| 플러그인 | ❌ (단, Quick Look 확장은 macOS 시스템 확장) |
| 스킬 | ⚠️ 스킬 자체는 아니지만 `.agents/skills/`에 **스킬 4종을 포함**함 |
| MCP | ❌ 전혀 없음 |

포함된 스킬: `amore-cli`, `release-process`, `changelog-maintenance`, `swift-concurrency`
`skills-lock.json`이 외부 스킬의 출처와 해시를 잠급니다(`package-lock.json`과 유사).

앱의 "Open in LLM" 기능도 API 연동이 아니라 **설치된 외부 앱을 실행**하는 방식이라 MCP와 무관합니다.

### 3.3 API 토큰이 필요한가요?

**일반 사용자는 필요 없습니다.** 무료이고 MIT 라이선스입니다.

개발/릴리즈 시에만 필요한 항목:

| 항목 | 용도 | 필요 시점 |
| --- | --- | --- |
| `POSTHOG_PROJECT_TOKEN` | 익명 사용 통계 (하루 1회 "앱 활성화" 이벤트) | Release 빌드 |
| Sentry DSN | 크래시 리포트 (공개 클라이언트 키, 이미 커밋됨) | Release 빌드 |
| Sparkle EdDSA 키 | 자동 업데이트 서명 | 배포 |
| Apple 공증 프로필 | notarization | 배포 |

```sh
cp Secrets.xcconfig.example Secrets.xcconfig   # POSTHOG_PROJECT_TOKEN 입력
```

`Secrets.xcconfig`는 gitignore 처리되어 있습니다. 토큰이 없거나 Debug 빌드면 분석 기능은 자동 비활성화됩니다.
문서 내용·파일명·경로는 수집하지 않고, GeoIP도 비활성화하며, 설정에서 완전히 끌 수 있습니다.

### 3.4 왜 GitHub에서 주목받을까?

(정확한 스타 수는 확인하지 않았지만, 저장소의 흔적으로 추정되는 이유)

1. **"Electron 아님"** 포지셔닝 — README 첫 문단부터 강조. 가볍고 즉시 실행
2. **Homebrew 공식 cask 등재** — 심사를 통과한 검증된 앱
3. **완전 무료 + MIT + 서명/공증** — 유료 마크다운 앱이 많은 시장에서 희소
4. **완성도** — 105KB 규모의 CHANGELOG, Swift 테스트, GitHub Actions 3종, 보안 어드바이저리(GHSA) 발급 이력, 중국어 현지화
5. **AI 시대 트렌드 적중** — LLM이 마크다운으로 답하는 시대에 md 뷰어 수요 급증, "Open in LLM" 버튼까지 탑재
6. **AI 에이전트 친화 설계** — `AGENTS.md`, `CLAUDE.md`, `.codex/config.toml`, `.agents/skills/`, `skills-lock.json`
7. **회사 후원** — Pluk / Amore 스폰서, `pluk-inc` 조직 저장소

### 3.5 로컬 에이전트 구축에 도움이 될까?

**앱 코드 자체는 도움이 되지 않지만, 에이전트 설정 구조는 매우 좋은 레퍼런스입니다.**

도움되지 않는 점: Swift/AppKit 코드는 에이전트와 무관, LLM API 호출 코드 없음, macOS 전용.

참고할 만한 점:

1. **`AGENTS.md` = 에이전트 지침서 작성의 모범 사례**
   - "문서가 동작을 설명하면 그 문서도 동작의 일부다" — 코드 변경으로 문서가 틀리면 같은 커밋에서 수정
   - 규칙 + 이유 + **실제 사고 사례**를 함께 기술 (Mermaid 렌더링 회귀가 문서 불일치로 오래 방치된 사례)
   - "묻지 않고 건드리면 안 되는 것" 섹션 (서명 키, 팀 ID, 엔타이틀먼트)
   - 프로젝트 팩트 테이블 (번들 ID, 최소 OS, 스킴)
   - "검증은 변경 규모에 비례하게" 원칙
2. **`.agents/skills/` + `skills-lock.json`** — 외부 스킬을 출처·해시로 버전 잠금하는 패턴
3. **`.claude/skills/` → `.agents/skills/` 심볼릭 링크** — 여러 AI 툴이 같은 스킬을 공유

이식 추천: `AGENTS.md`, `.agents/skills/`, `skills-lock.json` 세 가지 패턴.

### 3.6 React나 PHP로 만들 수 있나?

**약 90%는 가능합니다. Quick Look 연동만 불가능합니다.**

| 기능 | React | PHP |
| --- | :---: | :---: |
| 마크다운 렌더링 | ✅ | ✅ |
| Mermaid / KaTeX / 코드 하이라이팅 | ✅ | ✅ |
| 편집 모드 | ✅ | ⚠️ 프론트는 별도 JS 필요 |
| 아웃라인 / 검색 / 테마 | ✅ | ✅ |
| **Finder 스페이스바 미리보기** | ❌ | ❌ |
| 기본 `.md` 핸들러 등록 | ⚠️ Electron/Tauri면 가능 | ❌ |
| 네이티브 수준의 가벼움 | ❌ | — |

**React 스택 예시**

```
React + Vite
├─ react-markdown + remark-gfm      (렌더링)
├─ rehype-katex + katex             (수식)
├─ mermaid                          (다이어그램)
├─ @uiw/react-codemirror            (편집기)
├─ DOMPurify                        (XSS 방어)
└─ 데스크톱화: Tauri(약 5MB) 또는 Electron(약 150MB)
```

> 참고: `md-preview/Vendor/`의 라이브러리(DOMPurify, Morphdom, highlight.js, CodeMirror, KaTeX, Mermaid)는 웹에서 쓰는 것과 동일합니다. Swift는 껍데기이고 **렌더링 알맹이는 이미 웹 기술**이므로, `md-preview/Rendering/MarkdownHTML+*.swift`의 HTML 생성 로직을 그대로 참고해 포팅할 수 있습니다.

**PHP 스택 예시** — `league/commonmark`(강력) 또는 `erusev/parsedown`(간단) + Laravel/Symfony.
사내 위키·문서 포털·정적 사이트 생성기에는 적합하지만 데스크톱 앱·오프라인·Finder 연동은 불가합니다.

| 목표 | 추천 |
| --- | --- |
| 웹 서비스 / SaaS | React (Next.js + Vercel) |
| 사내 문서 포털 / 저렴한 호스팅 | PHP |
| 가벼운 데스크톱 앱 | Tauri + React |
| 맥 네이티브 (Quick Look 포함) | Swift만 가능 |

---

## 4. 수익화 아이디어

> **라이선스 확인:** MIT이므로 상업적 이용·수정·유료 판매가 가능하며 소스 공개 의무도 없습니다.
> 단 **원 저작권 표시와 MIT 라이선스 전문을 반드시 포함**해야 하고, 이름·아이콘 등 브랜딩은 교체해야 합니다.
> Sentry DSN, PostHog 토큰, Sparkle 공개키는 반드시 본인 것으로 교체해야 데이터가 원저자 서버로 가지 않습니다.

### A급 (수익성 高 / 실현성 高)

| # | 아이디어 | 난이도 | 예상 수익 |
| --- | --- | --- | --- |
| 1 | **웹 마크다운 스튜디오 SaaS** — 무료/Pro($5월)/Team($15인). 클라우드 동기화, PDF·DOCX 내보내기, 실시간 협업 | ⭐⭐⭐ | 월 $500~5,000 |
| 2 | **마크다운 → PDF 변환 API** — `POST /v1/convert`. 1,000건당 $10. 청구서·계약서·리포트 자동화 SaaS가 주 고객. `MarkdownWebView+PDFExport.swift`의 인쇄용 CSS 노하우가 경쟁력 | ⭐⭐ | 월 $300~3,000 |
| 3 | **AI 리포트 뷰어** — LLM 출력 마크다운을 붙여넣으면 렌더링 + 공유 링크 + PDF/PPT 변환. Pro는 브랜딩·팀 워크스페이스·비밀번호 보호 | ⭐⭐⭐ | 월 $1,000~10,000 |

### B급 (수익성 中 / 실현성 高)

| # | 아이디어 | 난이도 | 예상 수익 |
| --- | --- | --- | --- |
| 4 | **Mac App Store 프리미엄 버전** — 리브랜딩 후 $9.99. iCloud 동기화, AI 요약/번역, 노션·옵시디언 연동, 프레젠테이션 모드 추가. (개발자 계정 연 $99, 원본이 무료라 차별화 필수) | ⭐⭐⭐⭐ | 월 $200~2,000 |
| 5 | **테마/템플릿 마켓플레이스** — 앱은 무료 배포, 테마 팩 $3~10 판매. 등록 개발자 수수료 30% 모델. `Theme/ThemePreset.swift` 구조가 확장에 유리 | ⭐⭐ | 월 $100~1,000 |
| 6 | **강의/전자책** — AppKit + WKWebView, Quick Look 확장(자료 희소), 샌드박스·공증·Sparkle 전 과정, AI 에이전트 협업 워크플로우. $49~199 | ⭐⭐ | 월 $200~2,000 |
| 7 | **Obsidian / VS Code 확장 유료화** — 렌더링 파이프라인만 분리. 사용자 풀이 커서 유통이 쉬움 | ⭐⭐⭐ | 월 $100~1,000 |

### C급 (니치, 마진 우수)

| # | 아이디어 | 난이도 | 예상 수익 |
| --- | --- | --- | --- |
| 8 | **기업 사내 문서 포털 구축** — Git 연동, SSO, 권한 관리. 구축비 + 유지보수비 | ⭐⭐⭐ | 건당 $2,000~20,000 |
| 9 | **기술 블로그 플랫폼** — md 작성 시 자동 배포, 커스텀 도메인 $5/월 (경쟁 치열) | ⭐⭐⭐⭐ | 월 $100~5,000 |
| 10 | **문서 마이그레이션 툴** — Notion ↔ Obsidian ↔ Confluence ↔ md 변환 | ⭐⭐⭐ | 월 $200~2,000 |
| 11 | **후원 모델** — Buy Me a Coffee, GitHub Sponsors (원본이 채택한 방식) | ⭐ | 월 $10~500 |
| 12 | **문서 분석 SaaS** — 품질 점수, 가독성, 깨진 링크 검사, CI 연동 B2B | ⭐⭐⭐⭐ | 월 $300~3,000 |

### 추천 로드맵

```
1단계 (1~2개월)   #2 PDF 변환 API        → 가장 빠른 매출, 기술 부담 낮음
2단계 (3~6개월)   #3 AI 리포트 뷰어      → 트렌드 적중, 확장성 우수
3단계 (6개월~)    #1 웹 SaaS로 통합      → 구독 모델 완성
병행              #6 강의/전자책         → 부수입 + 마케팅
```

### 리스크

- 마크다운 시장은 레드오션. "또 하나의 md 에디터"는 차별화 없이는 실패
- PDF 품질 / AI 연동 / 협업 중 **하나를 압도적으로** 잘해야 함
- MIT 저작권 고지 누락은 법적 리스크
- 무료 오픈소스 원본이 존재하므로 "유료인 이유"가 명확해야 함

---

## 참고

- 라이선스: MIT (`LICENSE`)
- 최소 요구사항: macOS 15 이상, Apple Silicon 또는 Intel
- 현재 버전: 0.0.58 (build 62)
- 릴리즈 절차: `.agents/skills/release-process/SKILL.md` 및 `scripts/release.sh`
