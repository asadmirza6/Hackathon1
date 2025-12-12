# Quick Start Guide

**Status**: Complete | **Date**: 2025-12-09

This guide provides instructions for setting up, developing, and deploying the Physical AI course website.

---

## Prerequisites

- Node.js 18+ ([download](https://nodejs.org/))
- npm 9+ (included with Node.js)
- Git 2.30+ ([download](https://git-scm.com/))
- GitHub account with repository access
- Code editor (VS Code recommended)

---

## Project Setup

### 1. Clone Repository

```bash
git clone https://github.com/[owner]/physical-ai.git
cd physical-ai
```

### 2. Install Dependencies

```bash
cd book
npm install --legacy-peer-deps
```

**Note**: The `--legacy-peer-deps` flag resolves React version conflicts between Docusaurus and @testing-library/react.

### 3. Verify Installation

```bash
npm run build
```

Expected output:
```
✔ Client compiled successfully in 12.34s
✔ Server compiled successfully in 5.67s
```

---

## Development Workflow

### Start Local Development Server

```bash
npm run start
```

Server starts at `http://localhost:3000/physical-ai/`

### Edit Lesson Content

1. Open any file in `book/docs/chapter-N/lesson-M.md`
2. Edit markdown content
3. Save file
4. Browser auto-reloads with changes

### Create a New Lesson (Not typically done, but if needed)

1. Create file: `book/docs/chapter-N/lesson-X.md`
2. Add YAML frontmatter:
```yaml
---
title: Lesson Title
description: Short description
keywords: [tag1, tag2, tag3]
sidebar_position: X
---
```
3. Add markdown content
4. Update `book/sidebars.ts` if structure changes (unlikely)

---

## Configuration Files

### Main Configuration: `book/docusaurus.config.ts`

Key settings:
- `title`: "Physical AI & Humanoid Robotics Course"
- `baseUrl`: "/physical-ai/" (for GitHub Pages)
- `organizationName`: Your GitHub username
- `projectName`: "physical-ai"

To update site metadata, edit this file.

### Navigation: `book/sidebars.ts` (TBD in Phase 1)

Defines chapter and lesson structure:
```typescript
const sidebars = {
  default: [
    {
      label: 'Chapter 1: Physical AI Foundations',
      items: ['chapter-1/lesson-1', 'chapter-1/lesson-2'],
    },
    // ... more chapters
  ],
};
```

### Package Configuration: `book/package.json`

Key scripts:
- `npm start` - Development server
- `npm run build` - Production build
- `npm run serve` - Preview production build locally
- `npm test` - Run Jest unit tests
- `npm run test:e2e` - Run Playwright E2E tests
- `npm run lint` - Check code style with ESLint
- `npm run format` - Auto-format code with Prettier

---

## Building for Production

### Local Build

```bash
npm run build
```

Output: `book/build/` directory contains static HTML/CSS/JS

### Preview Production Build

```bash
npm run serve
```

Opens `http://localhost:3000` with production-optimized site

---

## GitHub Pages Deployment

### Prerequisites

1. Repository must be public (GitHub Pages requirement)
2. GitHub Pages enabled in repository settings:
   - Go to **Settings** → **Pages**
   - Set **Source** to `gh-pages` branch
   - Save

### Automatic Deployment

The GitHub Actions workflow (`.github/workflows/deploy.yml`) automatically:
1. Triggers on push to `main` branch
2. Installs Node.js 20
3. Runs `npm install --legacy-peer-deps`
4. Runs `npm run build`
5. Pushes built site to `gh-pages` branch
6. GitHub Pages serves the site at `https://[owner].github.io/[repo]/`

### Deploy Process

```bash
# Make changes to content
git add .
git commit -m "Update lesson content"
git push origin main

# GitHub Actions automatically:
# 1. Checks out code
# 2. Installs dependencies
# 3. Builds site
# 4. Deploys to GitHub Pages
# Site is live in ~2 minutes
```

### Monitor Deployment

1. Go to repository **Actions** tab
2. Click on latest workflow run
3. View build logs and status
4. Confirm site is live at `https://[owner].github.io/[repo]/`

---

## Testing

### Unit Tests (Jest)

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run specific test file
npm test navigation.spec.ts
```

### E2E Tests (Playwright)

```bash
# Run all E2E tests
npm run test:e2e

# Run tests in debug mode
npm run test:e2e --debug

# Run specific test file
npm run test:e2e navigation.spec.ts
```

### Code Quality

```bash
# Lint code
npm run lint

# Auto-format code
npm run format
```

---

## Troubleshooting

### Issue: "Cannot find module 'docusaurus'"

**Solution**: Run `npm install --legacy-peer-deps` again

### Issue: Port 3000 already in use

**Solution**: Kill process or use alternate port:
```bash
npm start -- --port 3001
```

### Issue: Build fails with "Exhaustive list of all broken links"

**Solution**: Ensure all markdown files have valid YAML frontmatter and don't link to non-existent docs

### Issue: GitHub Pages shows 404

**Solution**:
1. Check repository settings → Pages → Source is set to `gh-pages` branch
2. Verify GitHub Actions workflow completed successfully
3. Check that `baseUrl` in `docusaurus.config.ts` matches repository name

### Issue: Search not working

**Solution**: Ensure `@docusaurus/plugin-search-local` is installed and enabled in `docusaurus.config.ts`:
```typescript
plugins: [
  require.resolve('@docusaurus/plugin-search-local'),
],
```

---

## Project Structure Reference

```
physical-ai/
├── book/                          # Docusaurus site root
│   ├── docs/                      # Lesson content
│   │   ├── chapter-1/
│   │   │   ├── lesson-1.md
│   │   │   └── lesson-2.md
│   │   ├── chapter-2/
│   │   ├── chapter-3/
│   │   └── chapter-4/
│   ├── src/
│   │   ├── components/            # React components
│   │   ├── css/                   # Styling
│   │   └── pages/                 # Custom pages
│   ├── docusaurus.config.ts       # Main config
│   ├── sidebars.ts                # Navigation (TBD)
│   └── package.json
├── tests/                         # Test files
│   ├── e2e/                       # E2E tests
│   └── unit/                      # Unit tests
├── .github/
│   └── workflows/
│       └── deploy.yml             # CI/CD workflow
├── .gitignore
├── README.md
└── specs/
    └── 001-docusaurus-book/       # Feature specification
        ├── spec.md
        ├── plan.md
        ├── research.md
        ├── data-model.md
        └── quickstart.md
```

---

## Next Steps

1. ✅ Docusaurus project initialized
2. ✅ All lesson content created (8 files)
3. ⏳ Create `sidebars.ts` (navigation structure)
4. ⏳ Enable search plugin
5. ⏳ Create CSS customizations (responsive design)
6. ⏳ Create home page
7. ⏳ Write and run tests
8. ⏳ Deploy to GitHub Pages

---

## Documentation Links

- [Docusaurus Official Docs](https://docusaurus.io/)
- [GitHub Pages Help](https://docs.github.com/en/pages)
- [Markdown Guide](https://www.markdownguide.org/)
- [Jest Testing Guide](https://jestjs.io/)
- [Playwright E2E Testing](https://playwright.dev/)

