# Adding gallery photos (holiday workflow)

The family gallery lives in this repo. To add photos to the **shared** copy everyone
sees, run the helper script, review, and push. No local-only copy — it goes to master.

## From a browser Claude Code session (e.g. on holiday, phone or laptop)

1. Open **claude.ai/code**, signed into your account, on the `portscatho-guide` repo.
2. **Attach the day's photos** to a chat message.
3. Ask Claude:

   > Run `tools/add_gallery_photos.py 2026 <the attached photos>`, then commit and push.

That's it — Claude saves the attached files, runs the script, and pushes.

## What the script does

```
python tools/add_gallery_photos.py <year> <image-or-folder> [more...]
python tools/add_gallery_photos.py auto  <folder>            # read year from "YYYY name.jpg"
```

- Optimises each photo (auto-rotate, ≤1200px) → `img/gallery/<year>/pNN.jpg`
- Makes a grid thumbnail (≤360px) → `tNN.jpg`
- Appends them to the `GALLERY` manifest in `index.html`
- Bumps the service-worker cache in `sw.js` so phones refetch

It does **not** commit — you (the editor) push:

```
git add -A && git commit -m "gallery: add 2026 photos" && git push
```

## Requirements

- `pip install pillow`
- iPhone `.HEIC` only: `pip install pillow-heif` (WhatsApp photos are already JPEG)

## Test year

Use year `2099` for testing; delete `img/gallery/2099/` and revert `index.html` / `sw.js`
afterwards so nothing test-related is left in the gallery.
