#!/usr/bin/env python3
"""
Add photos to the Portscatho family gallery — one command does everything.

USAGE (run from anywhere in the repo; image paths are resolved from where you run it):

    python tools/add_gallery_photos.py <year> <image-or-folder> [more images...]
    python tools/add_gallery_photos.py auto  <image-or-folder> [more images...]

  <year>  a 4-digit year (e.g. 2026) applied to ALL the photos you pass,
          or the word 'auto' to read the year from each filename's leading
          YYYY (e.g. "2026 harbour.jpg"), falling back to the file's date.

WHAT IT DOES (it does NOT git commit — you stay the editor and push yourself):
  - optimises each photo: auto-rotates via EXIF, resizes to <=1200px, saves a
    progressive JPEG                              -> img/gallery/<year>/pNN.jpg
  - makes a fast grid thumbnail (short side <=360px)             -> tNN.jpg
  - appends them to the GALLERY manifest embedded in index.html
  - bumps the service-worker cache version in sw.js (so phones refetch)

THEN review and push:
    git add -A && git commit -m "gallery: add <year> photos" && git push

NOTES
  - Needs Pillow:            pip install pillow
  - For iPhone HEIC files:   pip install pillow-heif   (WhatsApp photos are
    already JPEG, so you usually won't need this.)
  - Numbering may look gappy (p01, p03, p06...) if a year already had photos —
    that's harmless; the manifest always points at the exact filenames written.
"""
import os, re, sys, json, glob, datetime
from collections import defaultdict

try:
    from PIL import Image, ImageOps
except ImportError:
    sys.exit("Pillow is required:  pip install pillow")
try:  # optional — lets it read iPhone .HEIC files
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:
    pass

REPO  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GDIR  = os.path.join(REPO, "img", "gallery")
INDEX = os.path.join(REPO, "index.html")
SW    = os.path.join(REPO, "sw.js")
EXTS  = (".jpg", ".jpeg", ".png", ".heic", ".webp")


def clean_alt(name):
    base = re.sub(r"\.[^.]+$", "", os.path.basename(name))
    base = re.sub(r"^(19|20)\d{2}\s*", "", base)          # strip a leading year
    base = re.sub(r"[-_]", " ", base).strip()
    if not base or re.match(r"^(IMG|IMAGE|DSC|MVI|PXL)", base, re.I):
        return "Holiday memory"
    return base[:1].upper() + base[1:]


def year_of(path, mode):
    if mode != "auto":
        return mode
    m = re.match(r"((?:19|20)\d{2})", os.path.basename(path))
    if m:
        return m.group(1)
    return str(datetime.datetime.fromtimestamp(os.path.getmtime(path)).year)


def gather(paths):
    files = []
    for p in paths:
        p = p if os.path.isabs(p) else os.path.join(os.getcwd(), p)
        if os.path.isdir(p):
            files += [f for f in sorted(glob.glob(os.path.join(p, "*")))
                      if f.lower().endswith(EXTS)]
        elif os.path.isfile(p) and p.lower().endswith(EXTS):
            files.append(p)
        else:
            print("  ! skipped (not an image):", p)
    return files


def next_index(year):
    ex = glob.glob(os.path.join(GDIR, year, "p*.jpg"))
    nums = [int(re.search(r"p(\d+)\.jpg$", os.path.basename(f)).group(1)) for f in ex]
    return (max(nums) + 1) if nums else 1


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    mode = sys.argv[1]
    if mode != "auto" and not re.fullmatch(r"(19|20)\d{2}", mode):
        sys.exit("First argument must be a 4-digit year or 'auto'. Got: " + mode)

    files = gather(sys.argv[2:])
    if not files:
        sys.exit("No images found to add.")

    counters, adds = {}, defaultdict(list)
    for f in files:
        year = year_of(f, mode)
        os.makedirs(os.path.join(GDIR, year), exist_ok=True)
        if year not in counters:                 # fix the gappy-numbering bug:
            counters[year] = next_index(year)     # compute once, then count in memory
        idx = counters[year]; counters[year] += 1
        try:
            img = ImageOps.exif_transpose(Image.open(f)).convert("RGB")
        except Exception as e:
            print("  ! could not read", os.path.basename(f), "-", e); continue
        w, h = img.size; mx = max(w, h)
        full = img.resize((round(w * 1200 / mx), round(h * 1200 / mx)), Image.LANCZOS) if mx > 1200 else img
        pname = "p%02d.jpg" % idx
        full.save(os.path.join(GDIR, year, pname), "JPEG", quality=74, optimize=True, progressive=True)
        short = min(full.size)
        thumb = full.resize((round(full.size[0] * 360 / short), round(full.size[1] * 360 / short)), Image.LANCZOS) if short > 360 else full
        thumb.save(os.path.join(GDIR, year, "t%02d.jpg" % idx), "JPEG", quality=70, optimize=True, progressive=True)
        alt = clean_alt(f)
        adds[year].append({"src": "img/gallery/%s/%s" % (year, pname), "alt": alt})
        print('  + %s/%s   "%s"' % (year, pname, alt))

    # --- update the GALLERY manifest inside index.html ---
    html = open(INDEX, encoding="utf-8").read()
    m = re.search(r"const GALLERY=(\{.*?\});\s*\n\s*const now=new Date", html, re.S)
    if not m:
        sys.exit("Could not find the GALLERY manifest in index.html — nothing changed there. "
                 "(The photos were written to disk; ask Claude to wire them into the manifest.)")
    gal = json.loads(m.group(1))
    for year, items in adds.items():
        gal.setdefault(year, []).extend(items)
    html = html.replace(m.group(1), json.dumps(gal, ensure_ascii=False, separators=(",", ":")))
    open(INDEX, "w", encoding="utf-8").write(html)

    # --- bump the service-worker cache so phones refetch ---
    sw = open(SW, encoding="utf-8").read()
    vm = re.search(r"portscatho-v(\d+)", sw)
    if vm:
        nv = int(vm.group(1)) + 1
        open(SW, "w", encoding="utf-8").write(sw.replace("portscatho-v" + vm.group(1), "portscatho-v%d" % nv, 1))
        print("  * bumped service-worker cache -> portscatho-v%d" % nv)

    total = sum(len(v) for v in gal.values())
    print("\nAdded %d photo(s): %s" % (len(files), ", ".join("%s (+%d)" % (y, len(v)) for y, v in sorted(adds.items()))))
    print("Gallery now holds %d photos." % total)
    print("\nReview, then push:\n  git add -A && git commit -m \"gallery: add photos\" && git push")


if __name__ == "__main__":
    main()
