# Workflows

`pages.yml` builds `main` with `web/build.sh` and uploads `dist/`. A separate
job deploys that artifact to GitHub Pages. It runs on pushes to `main`, or manually
with `main` selected. Generated output is not committed.

In the repository's Pages settings, use **GitHub Actions** as the publishing source.
