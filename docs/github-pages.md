# GitHub Pages

Merge the blank-book page and its `scripts/build.sh` before the deployment workflow.

## One-time repository setting

In **Settings → Pages → Build and deployment**, select **GitHub Actions** as the
source. No personal token or additional repository secret is required.

The workflow runs on pushes to `main`, or manually from **Actions → Deploy website →
Run workflow** with `main` selected. It stages only the website and its assets in
`_site/`, uploads that directory, and deploys it to the `github-pages` environment.
If environment deployment protection is configured, it must allow `main`.

## Address

The project site inherits the existing `harrisonfang.github.io` user site's custom
domain, so the expected address is <https://harrisonfang.com/crusadercodex/>.
Leave this repository's custom-domain field empty; do not add a `CNAME` file.
No DNS changes are needed for this project path.

The workflow summary reports the deployed URL after a successful run.

## References

- [Configure a publishing source](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)
- [Custom-domain inheritance for project sites](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/about-custom-domains-and-github-pages)
