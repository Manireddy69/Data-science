# Data-science

Self-learning data science from scratch via books & official websites.

This repo is **notebook-first** and published as a simple course-style website by converting the `.ipynb` notebooks into static HTML.

## Build the site locally

```bash
py -m pip install -U nbconvert nbformat
py build_site.py
```

Open:

- `site/index.html`

## Publishing (GitHub Pages)

This repo can include a GitHub Actions workflow that rebuilds the site and deploys it to the `gh-pages` branch on every push to `main`.

In GitHub repo settings:

- Settings → Pages → **Deploy from a branch**
- Branch: `gh-pages` / folder: `/ (root)`

## Disclaimer

All pictures and screenshots are from a book or blog (not my code).
