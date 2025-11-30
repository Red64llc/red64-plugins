# Plan Tech Stack

Create the tech stack document with a pre-filled template.

## What This Command Does

This command creates the `.red64/product/tech-stack.md` file with a structured template for documenting your project's technology choices organized by category.

## Execution Steps

### Step 1: Check for Existing Tech Stack Document

First, check if `.red64/product/tech-stack.md` already exists in the current working directory.

```bash
test -f .red64/product/tech-stack.md && echo "exists" || echo "missing"
```

### Step 2: Handle Based on Existence

**If tech-stack.md already exists:**

Output the following message and stop:

```
Skipped: .red64/product/tech-stack.md already exists. No changes made.

Your tech stack is already defined. Edit the file directly to make changes.
```

**If tech-stack.md does NOT exist:**

Continue to Step 3.

### Step 3: Create Product Directory

Ensure the product directory exists:

```bash
mkdir -p .red64/product
```

### Step 4: Create Tech Stack Document

Create `.red64/product/tech-stack.md` with the following template content:

```markdown
# Tech Stack

<!-- This document lists the technologies used in your project, organized by category. Update each section to reflect your actual technology choices. -->

## Overview

<!-- Write a 1-2 sentence description of your project's technical architecture. -->

[Your Project Name] is a [type of application/system]. The codebase consists of [high-level components] using [primary technologies/patterns].

---

## Languages

<!-- List the programming languages used in your project. -->

- **[Primary Language]** (e.g., TypeScript, Python, Go)
- **[Secondary Language]** (if applicable)
- **[Markup/Style Languages]** (e.g., HTML, CSS, Markdown)

## Frameworks

<!-- List the frameworks and major libraries your project uses. -->

### Frontend
- **[UI Framework]** (e.g., React, Vue, Next.js)
- **[Styling Solution]** (e.g., Tailwind CSS, styled-components)
- **[State Management]** (e.g., Redux, Zustand, React Context)

### Backend
- **[Server Framework]** (e.g., Express, FastAPI, Django)
- **[API Style]** (e.g., REST, GraphQL, tRPC)
- **[Authentication]** (e.g., NextAuth, Clerk, custom JWT)

## Database

<!-- List database technologies and data storage solutions. -->

- **[Primary Database]** (e.g., PostgreSQL, MongoDB, SQLite)
- **[ORM/Query Builder]** (e.g., Prisma, Drizzle, SQLAlchemy)
- **[Caching Layer]** (e.g., Redis, in-memory) (if applicable)
- **[File Storage]** (e.g., S3, Cloudinary, local) (if applicable)

## Infrastructure

<!-- List hosting, deployment, and infrastructure services. -->

- **[Hosting Platform]** (e.g., Vercel, AWS, Railway)
- **[Container Runtime]** (e.g., Docker) (if applicable)
- **[CI/CD Platform]** (e.g., GitHub Actions, CircleCI)
- **[Monitoring/Observability]** (e.g., Sentry, DataDog) (if applicable)

## Development Tools

<!-- List tools used for development, testing, and code quality. -->

### Code Quality
- **[Linter]** (e.g., ESLint, Ruff, Pylint)
- **[Formatter]** (e.g., Prettier, Black)
- **[Type Checker]** (e.g., TypeScript, mypy)

### Testing
- **[Unit Testing]** (e.g., Jest, pytest, Vitest)
- **[Integration Testing]** (e.g., Playwright, Cypress)
- **[API Testing]** (e.g., Supertest, httpx)

### Version Control
- **[VCS]** (e.g., Git)
- **[Repository Host]** (e.g., GitHub, GitLab)
- **[Branching Strategy]** (e.g., feature branches, trunk-based)

---

## Notes

<!-- Add any additional context about your technology choices or architecture decisions. -->

- [Note about architecture pattern, e.g., "Follows monorepo structure with Turborepo"]
- [Note about constraints, e.g., "Designed to work offline-first"]
- [Note about future plans, e.g., "Planning migration to X in next quarter"]
```

### Step 5: Output Success Message

Output the following success message:

```
Success: Created .red64/product/tech-stack.md

Your tech stack template is ready. Edit the file to document:
  - Programming languages
  - Frontend and backend frameworks
  - Database and storage solutions
  - Infrastructure and deployment
  - Development tools and practices

File location: .red64/product/tech-stack.md
```

## Notes

- This command is idempotent: running it multiple times will not overwrite existing content
- The template uses a simple list format organized by category
- Example technologies are provided in parentheses to guide selection
