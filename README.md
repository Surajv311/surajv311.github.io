### Suraj's Personal Website

- Uses Jekyll theme - https://github.com/poole/hyde

#### Run locally

```bash
bundle install
bundle exec jekyll serve
```

Site is served at http://localhost:4000.

#### Layout

- Posts: `_posts/YYYY-MM-DD-title.md`. Front matter needs `layout: post`, `title`, and `category` (`technicalArticles` or `nonTechnicalArticles`); the Articles page groups posts by category.
- Images: `public/images/` (referenced in posts as `{{ site.baseurl }}/public/images/<file>`).
- Other static files (resume, docs, CSS): `public/`.
- Version shown in the sidebar and used for release tags: `version` in `_config.yml`.

#### SEO

- `{% seo %}` and `{% feed_meta %}` in `_includes/head.html` generate meta tags, Open Graph tags and the RSS link.
- Link-preview image defaults to `public/surajverma.png` (`defaults` in `_config.yml`). Future idea: set `image: /public/images/<file>` in a post's front matter to give that post its own preview image.

#### Releases

`.github/workflows/release.yml` runs three jobs: CI Checks (reads and validates `version` from `_config.yml`, YAML lint, post front matter and image reference checks via `.github/scripts/check_site.py`), Build (`jekyll build` plus output sanity check, pull requests only), and Release. Deploying the live site is done automatically by GitHub's built-in "pages build and deployment" workflow, not by this file. CI Checks also runs on pull requests to `main`. On push to `main`, Release creates tag + GitHub release `v<version>` if it does not exist yet. Bump `version` in `_config.yml` to cut a new release.
