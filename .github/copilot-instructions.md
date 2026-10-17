# Copilot project instructions

## Authentication is required

- All new private pages and features must require the project's standard authentication.
- Enforce access on the server for every route; hiding links or protecting a page only in the frontend is not sufficient.
- If there is no valid session, redirect HTML pages to `/` (sign-in). APIs must return JSON `401` responses without performing the protected action.
- Links to private pages should only appear after sign-in, on the dashboard or on the page that is their parent.

## Page hierarchy and navigation

- The dashboard (`/dashboard`) is the root of the authenticated area and is level 1.
- Pages linked directly from the dashboard are level 2 and must provide navigation back to the dashboard.
- Pages linked from a level 2 page are level 3 and must return to the level 2 page that opened them. Continue this pattern at every level: each page returns to its immediate parent, never automatically to sign-in or the root, except when the current page is the dashboard.
- Add new pages to their parent's navigation and register their server routes so the hierarchy stays visible and predictable.
- When creating a page, identify its parent, add a “Back” link to that parent, and protect the server route with the standard session authentication.
