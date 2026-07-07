from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "public" / "source"
PRODUCTS = ROOT / "public" / "products"
BRAND = ROOT / "public" / "brand"
QA = ROOT / "tools" / "output"


def crop_product(source_name, slug, box, pad=18):
    img = Image.open(SOURCE / source_name).convert("RGB")
    crop = img.crop(box)
    cleanup = ImageDraw.Draw(crop)
    edge = 4
    cleanup.rectangle((0, 0, crop.width, edge), fill="white")
    cleanup.rectangle((0, crop.height - edge, crop.width, crop.height), fill="white")
    cleanup.rectangle((0, 0, edge, crop.height), fill="white")
    cleanup.rectangle((crop.width - edge, 0, crop.width, crop.height), fill="white")
    mask = crop.point(lambda channel: 255 if channel < 246 else 0).convert("L")
    bbox = mask.getbbox()
    if bbox:
        left, top, right, bottom = bbox
        left = max(0, left - pad)
        top = max(0, top - pad)
        right = min(crop.width, right + pad)
        bottom = min(crop.height, bottom + pad)
        crop = crop.crop((left, top, right, bottom))

    max_width, max_height = 450, 236
    scale = min(max_width / crop.width, max_height / crop.height)
    crop = crop.resize(
        (max(1, int(crop.width * scale)), max(1, int(crop.height * scale))),
        Image.Resampling.LANCZOS,
    )
    canvas = Image.new("RGB", (520, 300), "white")
    canvas.paste(crop, ((canvas.width - crop.width) // 2, (canvas.height - crop.height) // 2))
    canvas.save(PRODUCTS / f"{slug}.webp", quality=92, method=6)


def make_contact_sheet():
    QA.mkdir(parents=True, exist_ok=True)
    files = sorted(PRODUCTS.glob("*.webp"))
    thumbs = []
    font = ImageFont.load_default()
    for path in files:
        img = Image.open(path).convert("RGB")
        img.thumbnail((220, 126))
        tile = Image.new("RGB", (250, 172), "#f8fafc")
        tile.paste(img, ((250 - img.width) // 2, 12))
        draw = ImageDraw.Draw(tile)
        draw.text((12, 144), path.stem[:30], fill="#172033", font=font)
        thumbs.append(tile)

    cols = 3
    rows = (len(thumbs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 250, rows * 172), "#dbe4f0")
    for i, tile in enumerate(thumbs):
        sheet.paste(tile, ((i % cols) * 250, (i // cols) * 172))
    sheet.save(QA / "products-contact-sheet.jpg", quality=92)


def rounded_rectangle_mask(size, radius):
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius=radius, fill=255)
    return mask


def make_brand_icon():
    size = 1024
    icon = Image.new("RGBA", (size, size), (0, 0, 0, 0))

    base = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(base)
    for y in range(size):
        t = y / size
        r = int(24 + 34 * t)
        g = int(42 + 38 * t)
        b = int(72 + 52 * t)
        draw.line((0, y, size, y), fill=(r, g, b, 255))

    aurora = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ad = ImageDraw.Draw(aurora)
    ad.ellipse((-120, 60, 650, 650), fill=(46, 168, 255, 92))
    ad.ellipse((400, -80, 1120, 560), fill=(241, 75, 255, 84))
    ad.ellipse((250, 520, 1120, 1190), fill=(255, 106, 61, 72))
    aurora = aurora.filter(ImageFilter.GaussianBlur(56))
    base = Image.alpha_composite(base, aurora)

    mask = rounded_rectangle_mask((size, size), 230)
    shell = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    shell.paste(base, (0, 0), mask)
    icon = Image.alpha_composite(icon, shell)

    d = ImageDraw.Draw(icon)
    d.rounded_rectangle((72, 58, 952, 956), radius=206, outline=(255, 255, 255, 92), width=10)
    d.arc((98, 84, 926, 912), 200, 342, fill=(255, 255, 255, 54), width=14)
    d.rounded_rectangle((180, 136, 844, 500), radius=118, fill=(255, 255, 255, 26))

    shadow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle((206, 440, 838, 720), radius=46, fill=(0, 0, 0, 96))
    shadow = shadow.filter(ImageFilter.GaussianBlur(35))
    icon = Image.alpha_composite(icon, shadow)
    d = ImageDraw.Draw(icon)

    front = [(230, 355), (650, 430), (650, 690), (230, 610)]
    top = [(230, 355), (384, 262), (808, 338), (650, 430)]
    side = [(650, 430), (808, 338), (808, 592), (650, 690)]
    d.polygon(top, fill=(214, 230, 246, 255))
    d.polygon(front, fill=(105, 124, 150, 255))
    d.polygon(side, fill=(70, 84, 110, 255))
    d.line(front + [front[0]], fill=(236, 244, 255, 112), width=7)
    d.line(top + [top[0]], fill=(255, 255, 255, 150), width=7)
    d.line(side + [side[0]], fill=(255, 255, 255, 70), width=5)

    holes = [
        [(326, 374), (420, 390), (420, 514), (326, 497)],
        [(484, 402), (580, 420), (580, 545), (484, 526)],
    ]
    for pts in holes:
        d.polygon(pts, fill=(34, 43, 61, 255))
        d.line(pts + [pts[0]], fill=(255, 255, 255, 78), width=5)
        inner = [(pts[0][0] + 22, pts[0][1] + 20), (pts[1][0] - 18, pts[1][1] + 16), (pts[2][0] - 18, pts[2][1] - 24), (pts[3][0] + 20, pts[3][1] - 20)]
        d.polygon(inner, fill=(18, 25, 39, 255))

    highlight = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    hd = ImageDraw.Draw(highlight)
    hd.ellipse((242, 260, 660, 500), fill=(255, 255, 255, 62))
    highlight = highlight.filter(ImageFilter.GaussianBlur(28))
    icon = Image.alpha_composite(icon, highlight)

    icon.save(BRAND / "peskoblok-icon-1024.png")
    for px in (512, 256, 128, 64):
        icon.resize((px, px), Image.Resampling.LANCZOS).save(BRAND / f"peskoblok-icon-{px}.png")


def main():
    PRODUCTS.mkdir(parents=True, exist_ok=True)
    BRAND.mkdir(parents=True, exist_ok=True)

    ballast_rows = [
        ("ballast-wall-gray", (338, 205, 558, 258)),
        ("ballast-wall-color", (334, 268, 558, 318)),
        ("ballast-wall-torn-gray", (338, 333, 558, 383)),
        ("ballast-wall-torn-color", (334, 394, 558, 446)),
        ("ballast-partition-gray", (338, 460, 558, 512)),
        ("ballast-partition-color", (334, 524, 558, 575)),
        ("ballast-partition-torn-gray", (338, 587, 558, 638)),
        ("ballast-partition-torn-color", (334, 651, 558, 702)),
        ("ballast-column-gray", (338, 700, 558, 742)),
        ("ballast-column-color", (334, 752, 558, 795)),
        ("ballast-parapet-gray", (338, 805, 558, 848)),
        ("ballast-cap-gray", (338, 856, 558, 897)),
    ]
    for slug, box in ballast_rows:
        crop_product("price-ballast.jpg", slug, box)

    otsev_rows = [
        ("otsev-wall-gray", (555, 137, 725, 204)),
        ("otsev-wall-color", (475, 218, 815, 288)),
        ("otsev-wall-torn-gray", (585, 300, 710, 370)),
        ("otsev-wall-torn-color", (470, 385, 825, 452)),
        ("otsev-partition-gray", (590, 456, 705, 532)),
    ]
    for slug, box in otsev_rows:
        crop_product("price-otsev.jpg", slug, box)

    make_contact_sheet()
    make_brand_icon()


if __name__ == "__main__":
    main()
