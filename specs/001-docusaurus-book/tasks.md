# Tasks: Docusaurus Online Book

**Input**: Design documents from `/specs/001-docusaurus-book/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/url-routes.md, quickstart.md

**Tests**: Test tasks are included (per spec requirements for MVP validation)

**Organization**: Tasks are grouped by user story (P1, P2, P3) to enable independent implementation and testing of each story.

---

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic Docusaurus structure per implementation plan

**Acceptance**: Docusaurus project is initialized with 4-chapter × 2-lesson structure ready for content

- [ ] T001 Initialize Docusaurus 3.x project in `book/` directory with `npx create-docusaurus@latest`
- [ ] T002 [P] Configure `book/docusaurus.config.js` with site metadata, GitHub Pages baseUrl, and plugin settings
- [ ] T003 [P] Create directory structure: `book/docs/chapter-{1,2,3,4}/` with placeholder files
- [ ] T004 [P] Initialize `book/package.json` with Docusaurus and testing dependencies (Jest, Playwright, TypeScript)
- [ ] T005 [P] Configure `book/.eslintrc.json` and `book/.prettierrc` for code quality
- [ ] T006 Configure `book/tsconfig.json` for TypeScript compilation
- [ ] T007 Create `book/.github/workflows/deploy.yml` GitHub Actions workflow for build and deploy
- [ ] T008 Configure GitHub repository: enable GitHub Pages, set source branch to `gh-pages`

**Checkpoint**: Docusaurus project ready; can run `npm start` in `book/` directory

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before any user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

**Acceptance**: Sidebar navigation structure is fixed, search plugin is enabled, build validates against 4×2 structure

- [ ] T009 Create `book/sidebars.js` with hardcoded 4 chapters × 2 lessons structure per data-model.md
- [ ] T010 [P] Enable Docusaurus search plugin in `book/docusaurus.config.js` (local search, no external service)
- [ ] T011 [P] Create `book/src/css/custom.css` with Infima-based responsive grid and typography
- [ ] T012 [P] Configure mobile-responsive viewport settings in `book/docusaurus.config.js`
- [ ] T013 Create `book/src/components/Layout.tsx` with sidebar, header, footer, and search box placement
- [ ] T014 Create `book/docs/intro.md` home page with course introduction, feature overview, and CTA button
- [ ] T015 [P] Setup test infrastructure: configure Jest in `book/jest.config.js` with TypeScript support
- [ ] T016 [P] Setup Playwright configuration in `book/playwright.config.ts` for E2E testing against built site
- [ ] T017 Create `book/scripts/validate-structure.ts` to verify 4×2 lesson structure during build

**Checkpoint**: Foundation complete; can build site and validate structure

---

## Phase 3: User Story 1 - Navigate Course Content (Priority: P1) 🎯 MVP

**Goal**: Implement sidebar navigation and lesson pages so users can access all 8 lessons via clickable links. Verify navigation works correctly and pages load quickly.

**Independent Test**: Can be fully tested by visiting website, clicking sidebar links, and verifying all 8 lesson pages load with correct content and active lesson highlighting.

### Tests for User Story 1 (Required for MVP validation)

> **CRITICAL: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T018 [P] [US1] Create navigation unit test in `book/tests/__tests__/navigation.spec.ts` verifying sidebar renders 4 chapters
- [ ] T019 [P] [US1] Create navigation unit test verifying each chapter shows exactly 2 lessons
- [ ] T020 [P] [US1] Create navigation unit test verifying active lesson highlighting works correctly
- [ ] T021 [P] [US1] Create E2E test in `book/tests/e2e/navigation.e2e.ts` testing full lesson navigation flow
- [ ] T022 [P] [US1] Create E2E test verifying deep linking (direct URL access) works without breaking sidebar

### Implementation for User Story 1

- [ ] T023 [P] [US1] Create sample lesson markdown files in `book/docs/chapter-1/lesson-*.md` with metadata and placeholder content
- [ ] T024 [P] [US1] Create sample lesson markdown files in `book/docs/chapter-2/lesson-*.md`
- [ ] T025 [P] [US1] Create sample lesson markdown files in `book/docs/chapter-3/lesson-*.md`
- [ ] T026 [P] [US1] Create sample lesson markdown files in `book/docs/chapter-4/lesson-*.md`
- [ ] T027 [US1] Implement sidebar navigation component in `book/src/components/Sidebar.tsx` rendering hardcoded structure
- [ ] T028 [US1] Implement active lesson highlighting in `book/src/components/Sidebar.tsx` based on current URL
- [ ] T029 [US1] Implement lesson page layout in `book/src/theme/DocLayout.tsx` with proper spacing, typography, and code block styling
- [ ] T030 [US1] Implement breadcrumb navigation in `book/src/components/Breadcrumb.tsx` (optional but improves UX)
- [ ] T031 [US1] Test sidebar navigation works on mobile (viewport <768px) without horizontal scrolling
- [ ] T032 [US1] Verify page load time is <2 seconds using Lighthouse audit on first 2 lessons

**Checkpoint**: User Story 1 fully functional. Users can navigate all 8 lessons via sidebar. All tests PASS.

**MVP Deliverable**: At this point, the course website is usable with all lessons accessible.

---

## Phase 4: User Story 2 - Search Course Content (Priority: P2)

**Goal**: Implement full-text search functionality so users can find lessons by keyword. Search results must link to correct lessons and return results within 500ms.

**Independent Test**: Can be fully tested by searching for keywords (e.g., "robotics", "algorithms") and verifying results link to correct lessons and search performance is fast.

### Tests for User Story 2 (Required for implementation validation)

> **CRITICAL: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T033 [P] [US2] Create search unit test in `book/tests/__tests__/search.spec.ts` verifying search index is built correctly
- [ ] T034 [P] [US2] Create search unit test verifying search returns results for common keywords
- [ ] T035 [P] [US2] Create search unit test verifying search returns empty array for non-existent keywords
- [ ] T036 [P] [US2] Create search unit test verifying search response time is <500ms
- [ ] T037 [P] [US2] Create E2E test in `book/tests/e2e/search.e2e.ts` testing complete search user journey

### Implementation for User Story 2

- [ ] T038 [US2] Add `keywords` and `description` frontmatter to all 8 lesson files (chapters 1-4)
- [ ] T039 [US2] Create `book/src/components/SearchBox.tsx` component with input field and results dropdown
- [ ] T040 [US2] Implement search result rendering with lesson title, snippet, and relevance score
- [ ] T041 [US2] Implement search result click handler linking to correct lesson
- [ ] T042 [US2] Integrate search box into header component in `book/src/components/Header.tsx`
- [ ] T043 [US2] Test search functionality across all 8 lessons ensuring results are accurate
- [ ] T044 [US2] Measure search performance and optimize if needed to meet <500ms requirement
- [ ] T045 [US2] Test search on mobile devices; verify dropdown doesn't overflow screen

**Checkpoint**: User Story 2 fully functional. Search works across all 8 lessons. All tests PASS.

**Feature Complete**: At this point, core course features are complete (navigation + search).

---

## Phase 5: User Story 3 - Deploy to GitHub Pages (Priority: P3)

**Goal**: Setup automated CI/CD so the site builds and deploys on every push to main branch. Verify deployment is automatic with no manual steps and changes appear live within 2 minutes.

**Independent Test**: Can be fully tested by pushing code to main branch and verifying site deploys automatically to GitHub Pages within 2 minutes.

### Tests for User Story 3 (Required for deployment validation)

> **CRITICAL: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T046 [P] [US3] Create build validation test in `book/tests/__tests__/build.spec.ts` verifying Docusaurus build succeeds
- [ ] T047 [P] [US3] Create build validation test verifying all 8 lesson files exist and are valid markdown
- [ ] T048 [P] [US3] Create build validation test verifying HTML output is valid and has no broken links
- [ ] T049 [P] [US3] Create smoke test for deployed site in `book/tests/e2e/deployment.e2e.ts` verifying live site is accessible

### Implementation for User Story 3

- [ ] T050 [US3] Review `.github/workflows/deploy.yml` workflow and test locally with `act` (GitHub Actions local runner)
- [ ] T051 [US3] Add build caching to deploy workflow to reduce build time (npm cache via actions/setup-node)
- [ ] T052 [US3] Add build validation step to deploy workflow that runs `npm run build` and fails if errors occur
- [ ] T053 [US3] Configure GitHub Pages settings: set source to `gh-pages` branch, enable HTTPS
- [ ] T054 [US3] Test full deployment by pushing to a feature branch, merging to main, and verifying site deploys
- [ ] T055 [US3] Measure deployment time from push to live site availability (should be <2 minutes per spec requirement SC-007)
- [ ] T056 [US3] Setup GitHub repository secrets for any required environment variables (if using custom domain for Pages)
- [ ] T057 [US3] Create `book/README.md` documenting deployment process and troubleshooting steps

**Checkpoint**: User Story 3 fully functional. Site deploys automatically on push to main. Deployment time is <2 minutes.

**All Features Complete**: At this point, the entire Docusaurus book is built, deployed, and live.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Optimize performance, improve accessibility, and validate quality metrics

**Acceptance**: All success criteria from spec.md are met

### Performance Optimization

- [ ] T058 [P] Run Lighthouse audit on all 8 lesson pages; target score >90 for all metrics
- [ ] T059 [P] Optimize images in `book/docs/` using Docusaurus image plugin (if any images added)
- [ ] T060 [P] Enable code splitting and lazy loading in Docusaurus config to minimize bundle size
- [ ] T061 [P] Verify page load time is <2 seconds using real device or network throttling (4G speed)
- [ ] T062 Measure search response time; ensure <500ms per SC-003

### Accessibility & Responsive Design

- [ ] T063 [P] Run accessibility audit on all pages using axe-core or similar tool
- [ ] T064 [P] Verify heading hierarchy is correct (h1 → h2 → h3, no skipped levels)
- [ ] T065 [P] Test responsive design on 5 breakpoints: 320px, 576px, 768px, 1024px, 1440px
- [ ] T066 [P] Verify touch targets are at least 44×44px on mobile devices per WCAG guidelines
- [ ] T067 [P] Test color contrast for text elements using axe-core or WebAIM contrast checker
- [ ] T068 Verify mobile experience on real devices (iOS Safari, Android Chrome) not just emulation

### Content Quality Validation

- [ ] T069 [P] Validate all lesson files are valid markdown (no syntax errors)
- [ ] T070 [P] Verify all lesson files have required frontmatter: title, description, keywords
- [ ] T071 [P] Verify lesson content meets minimum length requirement (~2000 words per lesson, ~5000 recommended)
- [ ] T072 [P] Check all internal links work (sidebar links, search results, breadcrumbs)
- [ ] T073 [P] Verify course structure clearly communicates 4 chapters × 2 lessons with no ambiguity per SC-006

### Documentation & User Guides

- [ ] T074 Create `book/CONTRIBUTING.md` documenting how to add/edit lessons for future content updates
- [ ] T075 Create deployment troubleshooting guide in `book/README.md` (resolve common issues like cache, build errors)
- [ ] T076 Create lesson content template in `book/LESSON_TEMPLATE.md` for consistent formatting
- [ ] T077 Document lesson metadata fields (title, description, keywords, author, dates) in `book/README.md`

### Final Validation & Sign-off

- [ ] T078 Run complete test suite: `npm test` (Jest) + `npm run test:e2e` (Playwright)
- [ ] T079 Verify all acceptance criteria from spec.md are satisfied (checklist in spec.md)
- [ ] T080 Test on multiple browsers: Chrome, Firefox, Safari, Edge (latest 2 versions)
- [ ] T081 Verify all success criteria are met (SC-001 through SC-007)
- [ ] T082 Create summary report documenting feature completion and metrics achieved

**Checkpoint**: All quality gates passed. Product is ready for release.

---

## Dependencies & Parallel Execution

### Critical Path (Sequential)
```
T001 (init) → T002-T008 (setup) → T009-T017 (foundational) → T023-T032 (US1 implementation) → T033-T045 (US2 implementation) → T046-T057 (US3 implementation) → T058-T082 (polish)
```

### Parallel Opportunities

**Setup Phase** (T002-T008): All can run in parallel
- Docusaurus config, directory structure, ESLint, TypeScript, GitHub Actions, testing setup

**Foundational Phase** (T009-T017): Mostly parallel after T009 (sidebars must come first)
- Sidebars (T009) blocks nothing
- Search plugin (T010), CSS (T011), viewport (T012), testing setup (T015, T016) can run in parallel after T009

**User Story 1 - Tests First** (T018-T022): All tests can run in parallel, then implementation
- Tests must be written FIRST (T018-T022)
- Sample lesson files (T023-T026) can run in parallel during implementation
- Component implementation (T027-T030) depends on sample content

**User Story 2** (T033-T045): Can start after US1 tests pass
- Tests (T033-T037) can run in parallel
- Implementation (T038-T045) depends on having lesson content from US1

**User Story 3** (T046-T057): Can start after US1 is implemented
- Tests (T046-T049) can run in parallel
- Deployment setup (T050-T057) can run in parallel after tests are written

**Polish Phase** (T058-T082): Can run in parallel
- Performance (T058-T062), Accessibility (T063-T068), Content validation (T069-T073) are independent
- Documentation (T074-T077) is independent
- Final validation (T078-T082) depends on all previous phases

### MVP Scope

**Minimum Viable Product = User Story 1 ONLY**

Implement T001-T022 (Setup + Foundational + US1 tests and implementation):
- ✅ All 8 lessons accessible via sidebar navigation
- ✅ Navigation works correctly with active lesson highlighting
- ✅ Pages load quickly (<2 seconds)
- ✅ MVP is testable and deployable
- ❌ Search not included in MVP
- ❌ GitHub Pages deployment not included in MVP (can deploy locally for demo)

**MVP Acceptance**: US1 tests all PASS. Users can navigate all 8 lessons. Load time <2 seconds.

---

## Task Execution Guidelines

### Red-Green-Refactor Cycle (TDD)

For each user story phase:

1. **RED**: Run tests (T018-T022 for US1, etc.) - verify they FAIL
2. **GREEN**: Implement features to make tests PASS
3. **REFACTOR**: Clean up code, optimize, improve readability

### Branch & Commit Strategy

- Feature branch: `001-docusaurus-book` (already created)
- Per user story: create sub-branches `001-docusaurus-book/us1-navigation`, `001-docusaurus-book/us2-search`, etc.
- Per task: commit with format: `[T###] [US#] Brief description`
  - Example: `[T023] [US1] Create sample lesson files for chapter 1`

### Testing Validation

- After each phase: run full test suite for that phase
- After US1 complete: run T018-T022 tests - all PASS
- After US2 complete: run T033-T045 tests - all PASS + US1 tests still PASS
- After US3 complete: run T046-T057 tests - all PASS + US1, US2 tests still PASS
- Polish phase: run full suite including Lighthouse, accessibility, browser compatibility

---

## Metrics & Success

Track these metrics as you implement:

| Metric | Target | Acceptance Criteria |
|--------|--------|-------------------|
| Page Load Time | <2 seconds | SC-004 |
| Search Response Time | <500ms | SC-003 |
| Search Accuracy | 95%+ of keywords | SC-003 |
| Lighthouse Score | >90 | Performance |
| Mobile Render | Correct on iOS/Android | SC-005 |
| Navigation Clicks | <1 to reach any lesson | SC-001 |
| Deployment Time | <2 minutes | SC-007 |
| Test Pass Rate | 100% | QA Gate |
| Accessibility Score | >90 | WCAG 2.1 AA |

---

## Summary

- **Total Tasks**: 82
- **Setup Phase**: 8 tasks
- **Foundational Phase**: 9 tasks
- **User Story 1**: 15 tasks (5 tests + 10 implementation)
- **User Story 2**: 13 tasks (5 tests + 8 implementation)
- **User Story 3**: 12 tasks (4 tests + 8 implementation)
- **Polish Phase**: 25 tasks (performance, accessibility, documentation, validation)

**Estimated Implementation Timeline**:
- Setup + Foundational: 1-2 days
- User Story 1 (MVP): 2-3 days
- User Story 2: 2-3 days
- User Story 3: 1-2 days
- Polish: 2-3 days
- **Total: 1-2 weeks** (depending on team size and parallelization)

**Next Step**: Begin Phase 1 (Setup) with T001-T008. Ensure Docusaurus project initializes correctly before proceeding to foundational phase.

