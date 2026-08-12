# EduSense AI - Coding Standards & Conventions

This document outlines the engineering standards and conventions for the EduSense AI project.

## 1. Project Conventions
- **Language**: TypeScript (Strict Mode).
- **Framework**: React (Vite).
- **Styling**: Tailwind CSS with standard utility classes.
- **State Management**: React Context for global state (Auth, Theme, Modals), local state for UI, and React Query (future) for remote data fetching.

## 2. Folder Organization
The project is strictly divided into structural layers to enforce separation of concerns:
- `core/`: Core infrastructure, API clients, utility functions, and foundational types.
- `modules/`: Feature-based, self-contained business domains (e.g., prototypes, future).
- `features/`: Specific user flows (e.g., `auth`).
- `components/ui/`: Reusable, generic UI components (buttons, inputs, modals).
- `components/layout/`: Structural components (sidebar, header).
- `pages/`: Page-level components that compose features and layouts.

## 3. Git Workflow
- **Branching**: Use feature branches (`feature/assessment-engine`, `fix/login-crash`).
- **Commits**: Conventional Commits format (`feat: ...`, `fix: ...`, `refactor: ...`).
- **Merging**: PR reviews required. Squash & merge to `main`.

## 4. Import Organization
Imports should be grouped logically and separated by blank lines:
1. React and third-party libraries (e.g., `react`, `lucide-react`, `zod`).
2. Absolute or alias imports (e.g., `@/components/...`).
3. Relative imports (e.g., `../components/ui/Button`, `./styles.css`).
4. Type imports should use the `import type` syntax.

## 5. Error Handling
- **Global**: The application uses a top-level `ErrorBoundary` to catch uncaught React rendering errors and prevent white screens.
- **API**: All API calls should throw standardized `ApiError` objects that contain HTTP status codes and user-friendly messages.
- **UI**: Display non-blocking errors via the `useToast()` hook.
- **Null Checks**: Extensively use Optional Chaining (`?.`) and Nullish Coalescing (`??`) to handle potentially undefined data (especially for AI/ML outputs).

## 6. Testing Strategies
- **Unit Testing**: Test pure functions, reducers, and custom hooks with Vitest.
- **Component Testing**: Use React Testing Library for critical UI components.
- **Integration**: Verify critical flows (Login, Assessment Generation) end-to-end.
- **Mocks**: During Phase 1-3, `database.ts` acts as the mock database layer. Real API clients must mock endpoints successfully before integration.

## 7. ADR Guidance (Architecture Decision Records)
Any significant architectural change (e.g., migrating to React Query, choosing a charting library, state management shift) must be documented as an ADR in `docs/adr/`.
An ADR must contain:
- Context and Problem Statement
- Decision Drivers
- Considered Options
- Decision Outcome
- Pros and Cons of the decision
