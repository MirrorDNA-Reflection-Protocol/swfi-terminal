# SWFI Terminal

Terminal-style redesign prototype for SWFI, served at `swfi.activemirror.ai`.

## Local

```bash
cd /Users/mirror-admin/repos/swfi-terminal
/usr/bin/python3 serve.py
```

Then open `http://127.0.0.1:8344`.

## Files

- `index.html`: public landing page and terminal concept
- `styles.css`: visual system and layout
- `app.js`: small UI interactions
- `serve.py`: zero-dependency static server with `/health`

## Deployment

This repo is served locally on port `8344` and exposed through the existing `mirror-proxy` Cloudflare tunnel as `swfi.activemirror.ai`.
