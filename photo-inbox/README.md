# 📥 Photo inbox — drop holiday photos here

Upload the day's photos into this folder and the gallery updates itself.

## From your phone (no laptop needed)

1. Open **github.com** in your phone browser → your **portscatho-guide** repo.
2. Go into this **`photo-inbox`** folder → **Add file** → **Upload files**.
3. Pick the day's photos from your camera roll (WhatsApp-saved photos are fine).
4. Choose **"Commit directly to the master branch"** → **Commit changes**.

That's it. Within a minute or two, a background job (GitHub Action) will:

- optimise each photo and make a thumbnail,
- add them to the gallery under the **current year**,
- **empty this folder** again,
- and publish — so everyone sees them.

Refresh the app and the new photos are in the Gallery. Upload again the next day.

## What year does a photo go into?

- **This year's photos:** just upload them — they land in the **current year** automatically.
- **An older photo** (e.g. someone sends you one from 2015): **rename the file to start
  with the year** before uploading — `2015 harbour day.jpg` → lands in **2015**.
  `2019 towan beach.jpg` → **2019**, and so on. No leading year = current year.

> Tip: this folder should normally be empty (apart from this README). If photos
> are still sitting here after a few minutes, check the repo's **Actions** tab for
> the "Add gallery photos from inbox" run and its log.
