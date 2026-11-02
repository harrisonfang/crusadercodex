# Workflows

`pages.yml` builds the website with `scripts/build.sh` and deploys only `dist/` to
GitHub Pages on pushes to `main`, or when run manually with `main` selected.
Generated output is not committed.

Merge the blank-book page and its build script before this workflow. In the
repository's Pages settings, use **GitHub Actions** as the publishing source.
