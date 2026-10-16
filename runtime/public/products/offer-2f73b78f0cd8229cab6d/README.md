# Flaky CI retry evidence auditor — public beta

A single-purpose, read-only CLI for GitHub Actions repositories. Query a bounded window of workflow runs and report failed job names from prior attempts when the same run later succeeds, including whether the same job passed on its latest attempt.

This is *retry-correlated evidence*, not proof of flakiness or root cause, and it is not an official GitHub service. No login is needed for public repos while GitHub API quota permits. An optional, privately supplied GITHUB_TOKEN raises quota and can authorize owner-approved repositories. Do not paste tokens into reports.

Requirements: Python 3.12 standard library.
Example: python flake_audit.py --repo OWNER/REPO --limit 30 --output report.csv
Tests: python -m unittest discover -s tests -v
The tool never modifies workflows, opens PRs, reruns CI, or buys anything.
