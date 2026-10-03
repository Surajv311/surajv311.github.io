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

#### Releases

On every push to `main`, `.github/workflows/release.yml` reads `version` from `_config.yml` and creates tag + GitHub release `v<version>` if it does not exist yet. Bump `version` in `_config.yml` to cut a new release.
