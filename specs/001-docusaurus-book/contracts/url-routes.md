# URL Routes & Contracts: Docusaurus Book

**Date**: 2025-12-09
**Feature**: Docusaurus Online Book
**Phase**: 1 (Design)

---

## Overview

This document defines the URL routing structure for the Docusaurus book. Since this is a static site with no backend API, routes are file-based URLs that map directly to markdown files.

---

## URL Structure

All URLs are relative to the site root. The site is deployed to GitHub Pages at:
- **Base URL**: `https://username.github.io/physical-ai/` (or custom domain)

### Home Page

```
GET /
```

**Maps to**: `book/docs/intro.md`
**Content**: Course introduction, feature overview, CTA to first lesson
**Accepts**: None
**Returns**: HTML rendered from markdown
**Status Codes**:
- 200: Success
- 404: File not found (indicates corrupted deploy)

---

### Lesson Pages

#### Get Lesson Content

```
GET /docs/chapter-{N}/lesson-{M}
```

**Parameters**:
- `{N}`: Chapter number (1, 2, 3, or 4)
- `{M}`: Lesson number (1 or 2)

**Valid URLs**:
```
/docs/chapter-1/lesson-1
/docs/chapter-1/lesson-2
/docs/chapter-2/lesson-1
/docs/chapter-2/lesson-2
/docs/chapter-3/lesson-1
/docs/chapter-3/lesson-2
/docs/chapter-4/lesson-1
/docs/chapter-4/lesson-2
```

**Maps to**: `book/docs/chapter-{N}/lesson-{M}.md`

**Content**: HTML rendered from markdown lesson file with:
- Page title (from markdown frontmatter `title`)
- Sidebar navigation (hardcoded 4 chapters × 2 lessons structure)
- Active lesson highlight in sidebar
- Breadcrumb navigation (optional)

**Accepts**: None

**Returns**:
- HTML page with lesson content
- Sidebar navigation component
- Search box (header)
- Footer with previous/next lesson links (optional)

**Status Codes**:
- 200: Success (lesson found)
- 404: Invalid chapter/lesson number (outside 1-4, 1-2 range)

**Headers**:
- `Content-Type: text/html; charset=utf-8`
- `Cache-Control: public, max-age=3600` (1-hour cache for GitHub Pages)

**Example Request/Response**:
```
Request:
GET /docs/chapter-2/lesson-1 HTTP/1.1
Host: username.github.io
User-Agent: Mozilla/5.0

Response:
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
Cache-Control: public, max-age=3600

<!DOCTYPE html>
<html>
  <head>
    <title>Lesson Title - Physical AI Course</title>
    ...
  </head>
  <body>
    <div class="navbar">...</div>
    <div class="sidebar">
      <ul>
        <li>Chapter 1
          <ul>
            <li><a href="/docs/chapter-1/lesson-1">Lesson 1</a></li>
            <li><a href="/docs/chapter-1/lesson-2">Lesson 2</a></li>
          </ul>
        </li>
        ...
        <li><strong>Chapter 2</strong>  <!-- Active chapter -->
          <ul>
            <li><strong>Lesson 1</strong></li>  <!-- Active lesson -->
            <li><a href="/docs/chapter-2/lesson-2">Lesson 2</a></li>
          </ul>
        </li>
        ...
      </ul>
    </div>
    <main>
      <h1>Lesson Title</h1>
      <p>Lesson content here...</p>
    </main>
  </body>
</html>
```

---

## Search API (Client-Side)

Since this is a static site, search is performed client-side via JavaScript (no backend API).

### Search Query

```
searchIndex.search(query: string) -> SearchResult[]
```

**Input**:
- `query` (string): User search input (e.g., "robotics", "kinematics")

**Returns**: Array of search results (sorted by relevance)

```typescript
interface SearchResult {
  id: string;              // Lesson ID (e.g., "chapter-1/lesson-1")
  title: string;           // Lesson title
  url: string;             // URL to lesson (e.g., "/docs/chapter-1/lesson-1")
  snippet: string;         // First 200 chars of lesson content
  relevance: number;       // Score 0-1 (1.0 = perfect match)
}
```

**Behavior**:
- Search is performed against indexed lesson content (title, description, keywords, content)
- Results are returned instantly (no network latency)
- If no results found, return empty array
- If query is empty or < 2 characters, return empty array

**Example**:
```javascript
// User types "robot" in search box
const results = searchIndex.search("robot");

// Returns:
[
  {
    id: "chapter-1/lesson-1",
    title: "Introduction to Robotics",
    url: "/docs/chapter-1/lesson-1",
    snippet: "A robot is a mechanical or virtual artificial agent...",
    relevance: 0.95
  },
  {
    id: "chapter-3/lesson-2",
    title: "Robot Kinematics",
    url: "/docs/chapter-3/lesson-2",
    snippet: "In this lesson we explore the kinematic equations...",
    relevance: 0.85
  }
]
```

---

## Navigation Links

All navigation is accomplished through standard HTML `<a>` tags linking to the lesson URLs above.

### Sidebar Links

Each lesson in the sidebar is a link:
```html
<a href="/docs/chapter-1/lesson-1">Lesson 1</a>
```

### Search Result Links

Each search result is a link that navigates to the lesson:
```html
<a href="/docs/chapter-3/lesson-1">
  <strong>Robot Kinematics</strong>
  <p>In this lesson we explore...</p>
</a>
```

### Previous/Next Lesson Navigation (Optional)

At the bottom of each lesson page:
```html
<div class="lesson-nav">
  <a href="/docs/chapter-1/lesson-1" class="prev">← Previous Lesson</a>
  <a href="/docs/chapter-1/lesson-2" class="next">Next Lesson →</a>
</div>
```

---

## Error Handling

### 404 Not Found

If a user accesses an invalid URL (e.g., `/docs/chapter-5/lesson-1`):

```
GET /docs/chapter-5/lesson-1 HTTP/1.1

HTTP/1.1 404 Not Found
Content-Type: text/html

<!DOCTYPE html>
<html>
  <head>
    <title>404 - Page Not Found</title>
  </head>
  <body>
    <h1>404 - Page Not Found</h1>
    <p>The lesson you requested does not exist.</p>
    <a href="/">Return to Home</a>
  </body>
</html>
```

### Corrupted Markdown

If a lesson markdown file is missing or corrupted, Docusaurus build will fail. This is caught in CI/CD:

```bash
npm run build  # Fails if any lesson file is invalid
# Error: ...lesson-1.md not found
```

This ensures only valid builds are deployed to GitHub Pages.

---

## Deep Linking

Users can directly access any lesson URL without going through sidebar navigation. This must work correctly:

```
Direct URL: https://username.github.io/physical-ai/docs/chapter-2/lesson-1

Expected Behavior:
1. Page loads and displays Chapter 2, Lesson 1 content
2. Sidebar appears with all 4 chapters visible
3. Sidebar highlights Chapter 2 as the active chapter
4. Lesson 1 is highlighted as the active lesson
5. Navigation works correctly from this state
```

---

## Versioning & Backward Compatibility

**Immutable URLs**: Lesson URLs will never change (they are frozen by the fixed 4×2 structure).

**If Content Updates**:
- Lesson markdown content can be updated; URL remains the same
- Build produces new HTML but URL does not change
- Cached pages will refresh (1-hour cache expiration)

**If Lesson Structure Changes** (unlikely, but noted for completeness):
- Structure is immutable per constitution
- If needed in future, would require URL redirection strategy
- Not applicable in this phase

---

## Testing Acceptance Criteria

Each route must be tested:

| Route | Expected Status | Expected Content | Test |
|-------|-----------------|------------------|------|
| `/` | 200 | Home page with intro | Load and verify links work |
| `/docs/chapter-1/lesson-1` | 200 | Lesson 1.1 content | Load and check title, sidebar |
| `/docs/chapter-1/lesson-2` | 200 | Lesson 1.2 content | Load and check title, sidebar |
| ... | ... | ... | All 8 lessons |
| `/docs/chapter-5/lesson-1` | 404 | 404 error page | Verify error handling |
| Direct URL with deep link | 200 | Correct lesson content | Verify sidebar highlights correct item |
| Search query "robot" | Results array | Multiple matching lessons | Verify search functionality |

---

## Summary

- **Homepage**: `/` → `intro.md`
- **Lessons**: `/docs/chapter-{1-4}/lesson-{1-2}` → Corresponding markdown file
- **Search**: Client-side JavaScript API (no backend endpoint)
- **Error Handling**: 404 for invalid routes; build fails for corrupt content
- **Deep Linking**: All URLs must work and update sidebar state correctly
- **Caching**: 1-hour cache headers for performance

