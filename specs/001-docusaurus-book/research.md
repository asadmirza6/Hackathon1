# Phase 0: Research & Clarifications

**Status**: Complete | **Date**: 2025-12-09

This document resolves all unknowns identified in the Technical Context section of `plan.md`. All NEEDS CLARIFICATION items have been investigated and documented.

---

## Research Topics Completed

### 1. Docusaurus 3.x Search Implementation

**Decision**: Use Docusaurus built-in local search plugin (`@docusaurus/plugin-search-local`)

**Rationale**:
- Zero external dependencies (no cloud services required)
- Full-text indexing of all markdown content
- Works offline; no API calls needed
- GitHub Pages compatible (static generation only)
- Out-of-the-box configuration with minimal setup

**Alternatives Considered**:
- Algolia Search: Requires paid tier for private repositories; adds external dependency
- Custom client-side search: Would require duplicating indexing logic; less efficient
- Meilisearch: Requires separate backend service; not viable for static hosting

**Status**: ✅ Resolved

---

### 2. Mobile Responsive Design Approach

**Decision**: CSS Media Queries + Docusaurus built-in Bootstrap responsive grid

**Rationale**:
- Docusaurus ships with responsive CSS framework
- No additional dependencies needed
- Bootstrap utilities work out-of-the-box
- Mobile-first design approach standard across Docusaurus themes

**Status**: ✅ Resolved

---

### 3. Sidebar Navigation Structure

**Decision**: Hardcode 4 chapters × 2 lessons in `sidebars.ts`

**Rationale**:
- Constitution mandates fixed 4×2 structure (immutable)
- Hardcoding ensures structure cannot drift from specification
- Docusaurus sidebar supports nested categories natively
- No dynamic generation needed; structure is deterministic

**Status**: ✅ Resolved

---

### 4. GitHub Pages Deployment Pipeline

**Decision**: GitHub Actions workflow (`deploy.yml`) + peaceiris/actions-gh-pages

**Rationale**:
- Native GitHub integration; no third-party CI/CD required
- peaceiris action is battle-tested, maintained, widely used
- Automatic on push to main branch

**Status**: ✅ Resolved (GitHub Actions workflow created in T007)

---

### 5. Testing Strategy

**Decision**: Jest for unit/component tests; Playwright for E2E tests

**Rationale**:
- Jest: Standard for TypeScript/React projects; fast test execution
- Playwright: Browser automation for real navigation, search, mobile viewport tests
- Both are configured and working in `package.json`

**Status**: ✅ Resolved (Jest and Playwright installed in T004)

---

## Summary

All technical unknowns have been researched and resolved:

| Topic | Decision | Risk Level |
|-------|----------|-----------|
| Search | Built-in local search plugin | Low |
| Mobile Design | CSS media queries + Bootstrap | Low |
| Navigation | Hardcoded sidebars.ts | Low |
| Deployment | GitHub Actions + peaceiris | Low |
| Testing | Jest + Playwright | Low |

**Overall Risk**: ✅ LOW. All decisions are proven patterns in Docusaurus ecosystem.

**Next Step**: Proceed to Phase 1 (Design & Contracts) to implement the above decisions.
