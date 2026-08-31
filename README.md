# B2B Dashboard — GRC & Task Management MVP

[![CI](https://github.com/USERNAME/b2b-dashboard/actions/workflows/ci.yml/badge.svg)](https://github.com/USERNAME/b2b-dashboard/actions/workflows/ci.yml)

A minimum-viable internal dashboard for a small team to track **business
structure** (Business Units, Functions, Committees), **risk & compliance**
(Risks, Controls), and **tasks** — with email notifications for the events
that matter. Built with Django 4.x, server-rendered templates, and
Bootstrap 5, so it runs with zero external services out of the box and is
straightforward to extend.

## Why this shape

This is explicitly an MVP: the goal is something a team can start using
*today* and grow deliberately, not a fully genericized platform on day
one. That trade-off shows up in a few deliberate choices:

- **SQLite by default, Postgres via one env var.** `make up` (Docker) uses
  Postgres; running locally without Docker just works against a SQLite
  file — no setup tax to try it.
- **Console email backend by default.** Notifications work immediately
  (printed to the terminal) without configuring SMTP; switch
  `EMAIL_BACKEND` in `.env` when you're ready to send real email.
- **Three roles, not a permissions matrix.** `admin` / `manager` / `member`
  covers "who can delete organizational data" vs. "who can create/edit"
  vs. "who mostly just works their own tasks" — see
  [Roles & permissions](#roles--permissions) below. If the team outgrows
  this, Django's built-in `Group`/`Permission` system is still there
  underneath (`PermissionsMixin`) to layer on top.
- **Demo data seed command.** `make seed` populates realistic Business
  Units, a Risk, a Control, and a Task with three demo logins, so a new
  team sees a populated dashboard on day one instead of empty tables.

## Data model

```
BusinessUnit ──┬── Function
               ├── Committee (chair, members)
               └── Risk ──── Control
                     │
                   Task (optionally linked to a Risk or Control)
```

- **BusinessUnit** — top-level org unit (e.g. "Finance"), has a head.
- **Function** — a department within a BusinessUnit (e.g. "IT Security").
- **Committee** — a governance body with a chair and members, optionally
  tied to a BusinessUnit.
- **Risk** — title, severity × likelihood (used to compute a simple
  1–20 `risk_score`), status, owner, business unit.
- **Control** — mitigates a Risk; type (preventive/detective/corrective),
  effectiveness, owner.
- **Task** — the actionable work item: owner, due date, status, priority,
  optionally linked to the Risk or Control it came from.
- **Notification** — in-app + optional email record of something a user
  should know about.

## Roles & permissions

| Action                                   | Member | Manager | Admin |
|--------------------------------------------|:------:|:-------:|:-----:|
| View Business Units / Functions / Committees / Risks / Controls | ✅ | ✅ | ✅ |
| Create/edit Business Units / Functions / Committees / Risks / Controls | ❌ | ✅ | ✅ |
| Delete Business Units / Functions / Committees / Risks / Controls | ❌ | ❌ | ✅ |
| Create a Task (assign to self or others)  | ✅ | ✅ | ✅ |
| Edit/delete a Task                        | Own only | ✅ (any) | ✅ (any) |
| Mark a Task done                          | Own only | ✅ (any) | ✅ (any) |

Enforced by three small mixins in `apps/common/mixins.py`
(`ManagerRequiredMixin`, `AdminRequiredMixin`,
`OwnerOrManagerRequiredMixin`) applied per view — see that file for the
exact logic.

## Notifications

Two patterns are used deliberately, to show both approaches in a small
enough codebase to compare directly:

- **Explicit, in the view** (`apps/tasks/views.py`) — a task's creation/
  reassignment view calls `notify()` directly. Clear and easy to trace,
  but only fires from that one entry point.
- **Signal-based** (`apps/grc/signals.py`) — a `post_save` signal on
  `Risk` notifies the owner on creation regardless of how the Risk was
  created (web UI, Django admin, a future import script, etc.).

Both funnel through the single `apps.notifications.services.notify()`
function, which creates the in-app `Notification` row and emails it,
swallowing (and logging) any email failure so a broken SMTP config never
blocks the action that triggered it.

## Getting started

### Option A — Docker (recommended)

```bash
cp .env.example .env
make up
make migrate   # if not already applied by the container's entrypoint
make seed       # optional: populate demo data
make superuser  # optional: create your own admin login
```

Visit http://localhost:8000 and log in. If you ran `make seed`, three
demo accounts are available (password `DemoPass123!` for all):

| Email | Role |
|---|---|
| admin@example.com | Admin |
| manager@example.com | Manager |
| member@example.com | Member |

### Option B — Local (SQLite, no Docker)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py seed_demo_data   # optional
python manage.py runserver
```

### Running tests

```bash
pytest
```

## Continuous Integration

`.github/workflows/ci.yml` runs on every push/PR to `main`: spins up a
real Postgres service container, lints (`flake8`), checks formatting
(`black --check`), applies migrations, runs the full pytest suite with
coverage, then builds the Docker image to catch Dockerfile regressions.
Replace `USERNAME` in the badge URL above with your GitHub username/org
once you push this repo.

## Project layout

```
b2b-dashboard/
├── apps/
│   ├── accounts/       # custom email-based User, auth, profile
│   ├── core/            # BusinessUnit, Function, Committee + dashboard
│   ├── grc/              # Risk, Control
│   ├── tasks/            # Task + mark-done action
│   ├── notifications/    # Notification model + notify() service
│   └── common/            # shared base model, permission mixins, seed command
├── config/                 # settings, urls, wsgi/asgi
├── templates/               # base layout + shared partials
├── static/css/                # small custom.css on top of Bootstrap 5
├── docker-compose.yml
├── Dockerfile
├── Makefile
└── requirements.txt
```

Each app follows a conventional Django MVT layout
(`models.py` / `forms.py` / `views.py` / `urls.py` / `admin.py` /
`templates/<app>/`) — deliberately not over-engineered with extra
layers, since a small MVP benefits more from being easy to read
top-to-bottom than from architectural ceremony.

## What's next (deliberately out of scope for the MVP)

- REST API (the templates-only UI is enough for an internal tool today;
  Django REST Framework would be a natural addition later)
- Per-notification-type preferences / digest emails
- File attachments on Risks/Controls/Tasks
- Full audit trail of field-level changes (currently just created/updated
  timestamps)

## License

MIT — see [LICENSE](LICENSE).
