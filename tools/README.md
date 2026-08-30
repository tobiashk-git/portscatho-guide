# Adding gallery photos (holiday workflow)

The family gallery lives in this repo. To add photos to the **shared** copy everyone
sees, run the helper script, review, and push. No local-only copy — it goes to master.

## Everyday way (phone-only, automatic) — the photo inbox

Upload the day's photos to the **`photo-inbox/`** folder from your phone
(github.com → repo → `photo-inbox` → Add file → Upload files → commit to master).
A GitHub Action (`.github/workflows/gallery-inbox.yml`) then optimises them, adds
them to the current year, empties the inbox, and pushes — no laptop, no Claude
session needed. See `photo-inbox/README.md`.

> Note: attaching a photo in a Claude Code chat does **not** work for this — a
> cloud session receives the image to *look at*, not as a *file* it can process.
> The photos must reach the repo (the inbox upload above), where they're real files.

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
