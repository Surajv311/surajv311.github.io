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
- Link-preview image defaults to `public/surajverma.png` (`image` in `_config.yml`). Future idea: set `image: /public/images/<file>` in a post's front matter to give that post its own preview image.

#### Releases

On every push to `main`, `.github/workflows/release.yml` reads `version` from `_config.yml` and creates tag + GitHub release `v<version>` if it does not exist yet. Bump `version` in `_config.yml` to cut a new release.
