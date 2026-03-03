#!/usr/bin/env python3
"""
Rewrites compliance-tracker git history with 10 logical commits.

INSTRUCTIONS:
  1. Clone the repo locally if you haven't already:
       git clone https://github.com/ss7227-Developer/compliance-tracker.git
  2. Copy this script into the repo root folder
  3. Run it:
       python rewrite_history.py
  4. When it finishes, force-push to GitHub:
       git push origin main --force
"""

import subprocess
import sys
import os

# ── helpers ──────────────────────────────────────────────────────────────────

def run(cmd, check=True):
    """Run a shell command, print it, return stdout."""
    print(f"  $ {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"  ERROR: {result.stderr.strip()}")
        sys.exit(1)
    return result.stdout.strip()

def files_exist(paths):
    """Return only the paths that actually exist on disk."""
    existing = []
    for p in paths:
        p = p.rstrip("/")
        if os.path.exists(p):
            existing.append(p)
    return existing

def stage(paths):
    """git add each path that exists."""
    for p in files_exist(paths):
        run(f'git add "{p}"')

def commit(message, date):
    """Commit with a fixed author date and commit date."""
    env_prefix = (
        f'GIT_AUTHOR_DATE="{date}" '
        f'GIT_COMMITTER_DATE="{date}" '
    )
    # Windows-safe: use subprocess with env vars
    env = os.environ.copy()
    env["GIT_AUTHOR_DATE"] = date
    env["GIT_COMMITTER_DATE"] = date
    result = subprocess.run(
        ["git", "commit", "-m", message],
        env=env,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        # Nothing to commit — skip silently
        print(f"  (skipped — nothing staged for: {message[:60]})")
        return False
    print(f"  ✓ committed: {message[:70]}")
    return True

# ── commit plan ──────────────────────────────────────────────────────────────

COMMITS = [
    {
        "date": "2026-02-03T09:15:00",
        "message": "Initial Django project setup with PostgreSQL and environment config",
        "paths": [
            "backend/manage.py",
            "backend/requirements.txt",
            "backend/compliance_project/__init__.py",
            "backend/compliance_project/settings.py",
            "backend/compliance_project/urls.py",
            "backend/compliance_project/wsgi.py",
            "backend/compliance_project/asgi.py",
            ".gitignore",
            ".gitattributes",
            ".env.example",
        ],
    },
    {
        "date": "2026-02-05T11:30:00",
        "message": "Add Celery app initialisation for async task processing",
        "paths": [
            "backend/compliance_project/celery.py",
        ],
    },
    {
        "date": "2026-02-07T14:00:00",
        "message": "Add Inspection model with audit trail, classification mapping, and S3 archive key",
        "paths": [
            "backend/inspections/__init__.py",
            "backend/inspections/apps.py",
            "backend/inspections/models.py",
            "backend/inspections/migrations",
            "backend/inspections/admin.py",
            "backend/inspections/management",
            "backend/inspections/management/__init__.py",
            "backend/inspections/management/commands/__init__.py",
            "backend/inspections/management/commands/wait_for_db.py",
        ],
    },
    {
        "date": "2026-02-10T10:00:00",
        "message": "Add FDA data ingestion pipeline with paginated OpenFDA fetch and Celery task",
        "paths": [
            "backend/inspections/tasks.py",
            "backend/inspections/management/commands/fetch_fda_data.py",
        ],
    },
    {
        "date": "2026-02-13T16:00:00",
        "message": "Add AWS S3 data lake archival with versioned bucket and per-record archive key",
        "paths": [
            "backend/inspections/s3.py",
        ],
    },
    {
        "date": "2026-02-17T13:00:00",
        "message": "Add filterable REST API with DRF serializers, stats endpoint, and pagination",
        "paths": [
            "backend/inspections/serializers.py",
            "backend/inspections/views.py",
            "backend/inspections/filters.py",
            "backend/inspections/urls.py",
        ],
    },
    {
        "date": "2026-02-20T15:00:00",
        "message": "Add Scikit-learn ML risk scoring with OAI rate, frequency, and recency features",
        "paths": [
            "backend/inspections/risk.py",
            "backend/inspections/management/commands/score_risk.py",
        ],
    },
    {
        "date": "2026-02-25T11:00:00",
        "message": "Build React 18 dashboard with Recharts trend chart and sortable compliance table",
        "paths": [
            "frontend",
        ],
    },
    {
        "date": "2026-02-28T14:00:00",
        "message": "Add Docker Compose with production override for AWS RDS and SQS",
        "paths": [
            "backend/Dockerfile",
            "docker-compose.yml",
            "docker-compose.prod.yml",
        ],
    },
    {
        "date": "2026-03-02T10:00:00",
        "message": "Add README with architecture diagram, API reference, and deployment guide",
        "paths": [
            "README.md",
        ],
    },
]

# ── main ─────────────────────────────────────────────────────────────────────

def main():
    # Confirm we're in the right repo
    remote = run("git remote get-url origin", check=False)
    if "compliance-tracker" not in remote:
        print(f"\nWARNING: Remote is '{remote}'")
        print("Are you sure you're in the compliance-tracker directory?")
        answer = input("Continue anyway? (y/N): ").strip().lower()
        if answer != "y":
            sys.exit(0)

    print("\n── Step 1: stash any uncommitted changes ──────────────────────────")
    run("git stash", check=False)

    print("\n── Step 2: check out orphan branch ────────────────────────────────")
    run("git checkout --orphan rewritten-history")

    print("\n── Step 3: unstage everything ─────────────────────────────────────")
    run("git rm -rf --cached .")

    print("\n── Step 4: create logical commits ─────────────────────────────────")
    for i, c in enumerate(COMMITS, 1):
        print(f"\n  [{i}/{len(COMMITS)}] {c['message'][:60]}...")
        stage(c["paths"])
        commit(c["message"], c["date"])

    # Catch any remaining unstaged files in a final cleanup commit
    remaining = run("git status --porcelain", check=False)
    if remaining:
        print("\n  [+] Staging remaining files not matched above...")
        run("git add -A")
        commit("Add remaining project files", "2026-03-03T10:00:00")

    print("\n── Step 5: replace main with rewritten history ─────────────────────")
    # Delete local main if it exists, then rename this branch to main
    run("git branch -D main", check=False)
    run("git branch -m main")

    print("\n✅ Done! History rewritten with", run("git log --oneline | wc -l", check=False), "commits.")
    print("\nNow run:")
    print("  git push origin main --force")
    print("\nThen verify at: https://github.com/ss7227-Developer/compliance-tracker/commits/main")

if __name__ == "__main__":
    main()