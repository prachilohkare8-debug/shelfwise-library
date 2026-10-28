# Shelfwise — Library Desk

A responsive Library / Inventory Web App built for Web Technology Assignment 5. It demonstrates Express routing, route parameters, an Express Router, built-in and custom middleware, server-side validation with `express-validator`, EJS templates, static assets, and error handling.

## Requirements
- Node.js 18 or newer
- npm

## Run locally
```bash
npm install
npm start
```
Open `http://localhost:3000`. For auto-restart during development, use `npm run dev`.

## Features
- Browse and search the library catalogue by title, author, ISBN or book ID.
- Filter records by category.
- Add, view, edit and delete book records.
- Server-side validation for title, author, category, ISBN, total copies, available copies and shelf code.
- Duplicate ISBN prevention and correct 400 / 404 / 422 responses.
- EJS templates and static CSS/JavaScript served from `public/`.
- Custom request-logging middleware writes request entries to `data/requests.log`.
- Central error-handling middleware returns an HTML error page or JSON error response.
- Local JSON file storage in `data/books.json` for an easy classroom demo.
- Health endpoint: `GET /health`.

## Route table
| Method | Route | Purpose |
|---|---|---|
| GET | `/` | Redirect to catalogue |
| GET | `/health` | JSON health status |
| GET | `/books` | Catalogue, search and category filter |
| GET | `/books/new` | Render add-book form |
| POST | `/books` | Validate and create book |
| GET | `/books/:id` | View a single book (route parameter) |
| GET | `/books/:id/edit` | Render edit form |
| POST | `/books/:id/edit` | Validate and update book |
| POST | `/books/:id/delete` | Delete a book after browser confirmation |

## Validation checks to demonstrate
1. Add a valid record; it should appear in the catalogue.
2. Submit a title shorter than 2 characters or an invalid ISBN; the server should respond with HTTP 422 and show validation messages.
3. Enter available copies greater than total copies; the server should reject the record with HTTP 422.
4. Add an existing ISBN; the server should reject the duplicate with HTTP 422.
5. Open `/books/BK-9999`; the app should show a 404 page if that ID does not exist.
6. Open `/health`; the server should return JSON with status `ok`.

## Deployment on Render
1. Push this folder's contents to a GitHub repository (keep `package.json` in the repository root).
2. In Render, select **New → Web Service** and connect the repository.
3. Runtime: Node. Build command: `npm install`. Start command: `npm start`.
4. Deploy, then test `/`, `/health`, `/books` and an invalid record.

### Important storage note
This assignment demo uses a local JSON file. On many cloud hosts, the filesystem can be ephemeral, so new records may not survive redeploys or restarts. Use a persistent disk or a database if persistent production data is required. The app creates `data/books.json` if missing, but a read-only deployment filesystem can prevent writes.

## Project structure
```text
server.js                 Express application and top-level routes
routes/books.js           Express Router and CRUD routes
middleware/requestLogger.js Custom request logging middleware
middleware/errorHandler.js Central error-handling middleware
views/                    EJS templates
views/partials/           Shared page header/footer
public/css/styles.css     Responsive interface styles
public/js/app.js          Small UI interactions
 data/books.json           Demo inventory records
README.md                  Setup, route table and test guide
REPORT.md                  Report content/template and screenshot checklist
```

## Submission checklist
- Do not include `node_modules` or secret files in the ZIP.
- Replace the student details and date in the report before submission.
- Add real screenshots of your local/deployed output and paste the actual live URL and GitHub link into your report.
- Be prepared to explain every route, middleware and validation rule during viva.
