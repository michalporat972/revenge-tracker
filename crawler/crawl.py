name: OSINT News Crawler

on:
  schedule:
    - cron: "0 * * * *"   # every hour on the hour (UTC)
  workflow_dispatch:        # manual trigger from the Actions tab

permissions:
  contents: write           # allows committing events.json

jobs:
  crawl:
    runs-on: ubuntu-latest
    env:
      FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true

    steps:
      - name: Checkout repo
        uses: actions/checkout@v4

      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install feedparser

      - name: Run crawler
        run: python crawler/crawl.py

      - name: Commit updated events.json (if changed)
        run: |
          git config --local user.email "github-actions[bot]@users.noreply.github.com"
          git config --local user.name  "github-actions[bot]"
          git add public/events.json
          git diff --staged --quiet \
            || git commit -m "chore: osint crawl update [skip ci]"
          git push
