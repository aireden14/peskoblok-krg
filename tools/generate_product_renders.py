from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "public" / "products-generated"
QA = ROOT / "tools" / "output"
CANVAS = (1040, 600)


def adjust(color: tuple[int, int, int], amount: int) -> tuple[int, int, int]:
    return tuple(max(0, min(255, channel + amount)) for channel in color)


def rgba(color: tuple[int, int, int], alpha: int = 255) -> tuple[int, int, int, int]:
    return (*color, alpha)


def draw_soft_shadow(img: Image.Image, bbox: tuple[int, int, int, int], alpha: int = 76) -> None:
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    draw.ellipse(bbox, fill=(0, 0, 0, alpha))
    layer = layer.filter(ImageFilter.GaussianBlur(24))
    img.alpha_composite(layer)


def poly_mask(size: tuple[int, int], points: list[tuple[float, float]]) -> Image.Image:
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.polygon(points, fill=255)
    return mask


def add_concrete_texture(
    img: Image.Image,
    points: list[tuple[float, float]],
    rng: random.Random,
    color: tuple[int, int, int],
    rough: bool,
) -> None:
    mask = poly_mask(img.size, points)
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    bbox = mask.getbbox()
    if not bbox:
        return

    density = 210 if rough else 120
    for _ in range(density):
        x = rng.randint(bbox[0], bbox[2])
        y = rng.randint(bbox[1], bbox[3])
        if mask.getpixel((x, y)) == 0:
            continue
        tone = rng.choice((-34, -22, -12, 18, 28))
        radius = rng.choice((1, 1, 2, 3 if rough else 2))
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=rgba(adjust(color, tone), 42))

    if rough:
        for _ in range(18):
            x = rng.randint(bbox[0], bbox[2])
            y = rng.randint(bbox[1], bbox[3])
            if mask.getpixel((x, y)) == 0:
                continue
            length = rng.randint(26, 70)
            angle = rng.uniform(-0.45, 0.45)
            pts = []
            for step in range(4):
                dx = step * length / 3
                pts.append((x + dx, y + math.sin(step + angle) * rng.randint(4, 14)))
            draw.line(pts, fill=rgba(adjust(color, rng.choice((-46, 34))), 70), width=rng.randint(2, 4))

    layer.putalpha(Image.composite(layer.getchannel("A"), Image.new("L", img.size, 0), mask))
    img.alpha_composite(layer)


def draw_block(
    img: Image.Image,
    *,
    x: float,
    y: float,
    width: float,
    depth: float,
    height: float,
    color: tuple[int, int, int],
    holes: int = 3,
    rough: bool = False,
    seed: str = "block",
) -> None:
    rng = random.Random(seed)
    skew = depth * 0.55
    top_left_front = (x - width / 2, y)
    top_right_front = (x + width / 2, y)
    top_right_back = (x + width / 2 + skew, y - skew)
    top_left_back = (x - width / 2 + skew, y - skew)
    bottom_left_front = (x - width / 2, y + height)
    bottom_right_front = (x + width / 2, y + height)
    bottom_right_back = (x + width / 2 + skew, y - skew + height)

    top = [top_left_front, top_right_front, top_right_back, top_left_back]
    front = [top_left_front, top_right_front, bottom_right_front, bottom_left_front]
    right = [top_right_front, top_right_back, bottom_right_back, bottom_right_front]

    draw_soft_shadow(
        img,
        (
            int(x - width * 0.54),
            int(y + height * 0.7),
            int(x + width * 0.64 + skew),
            int(y + height * 1.08),
        ),
    )

    draw = ImageDraw.Draw(img)
    draw.polygon(front, fill=rgba(adjust(color, -30)))
    draw.polygon(right, fill=rgba(adjust(color, -48)))
    draw.polygon(top, fill=rgba(adjust(color, 26)))

    add_concrete_texture(img, front, rng, adjust(color, -30), rough)
    add_concrete_texture(img, right, rng, adjust(color, -48), rough)
    add_concrete_texture(img, top, rng, adjust(color, 26), rough=False)

    rim = rgba(adjust(color, 62), 138)
    draw.line(top + [top[0]], fill=rim, width=4)
    draw.line([top_left_front, bottom_left_front, bottom_right_front, top_right_front], fill=rgba(adjust(color, -66), 72), width=3)
    draw.line([top_right_front, top_right_back, bottom_right_back, bottom_right_front], fill=rgba(adjust(color, -72), 70), width=3)

    if holes <= 0:
        return

    def p(u: float, v: float) -> tuple[float, float]:
        ax, ay = top_left_front
        bx, by = top_right_front
        dx, dy = top_left_back
        return (ax + (bx - ax) * u + (dx - ax) * v, ay + (by - ay) * u + (dy - ay) * v)

    margin = 0.08 if holes > 1 else 0.2
    gap = 0.045 if holes > 1 else 0
    usable = 1 - margin * 2 - gap * (holes - 1)
    hole_w = usable / holes
    for index in range(holes):
        u0 = margin + index * (hole_w + gap)
        u1 = u0 + hole_w
        v0, v1 = 0.22, 0.78
        hole = [p(u0, v0), p(u1, v0), p(u1, v1), p(u0, v1)]
        draw.polygon(hole, fill=(31, 34, 38, 235))
        inner = [p(u0 + 0.025, v0 + 0.04), p(u1 - 0.025, v0 + 0.04), p(u1 - 0.025, v1 - 0.04), p(u0 + 0.025, v1 - 0.04)]
        draw.polygon(inner, fill=(15, 18, 22, 245))
        draw.line(hole + [hole[0]], fill=rgba(adjust(color, 72), 112), width=3)


def normalize_canvas(img: Image.Image) -> Image.Image:
    bbox = img.getchannel("A").getbbox()
    if not bbox:
        return img
    crop = img.crop(bbox)
    max_w, max_h = 900, 430
    scale = min(max_w / crop.width, max_h / crop.height)
    crop = crop.resize((int(crop.width * scale), int(crop.height * scale)), Image.Resampling.LANCZOS)
    out = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    out.alpha_composite(crop, ((CANVAS[0] - crop.width) // 2, (CANVAS[1] - crop.height) // 2 - 10))
    return out


def render(slug: str, spec: dict) -> None:
    img = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    kind = spec["kind"]

    if kind == "single":
        draw_block(img, x=470, y=260, width=430, depth=180, height=138, color=spec["color"], holes=spec.get("holes", 3), rough=spec.get("rough", False), seed=slug)
    elif kind == "partition":
        draw_block(img, x=480, y=270, width=440, depth=125, height=104, color=spec["color"], holes=2, rough=spec.get("rough", False), seed=slug)
    elif kind == "group":
        colors = spec["colors"]
        positions = [(260, colors[0]), (480, colors[1]), (700, colors[2])]
        for i, (x, color) in enumerate(positions):
            draw_block(img, x=x, y=285, width=232, depth=124, height=104, color=color, holes=spec.get("holes", 3), rough=spec.get("rough", False), seed=f"{slug}-{i}")
    elif kind == "group-partition":
        colors = spec["colors"]
        positions = [(255, colors[0]), (480, colors[1]), (705, colors[2])]
        for i, (x, color) in enumerate(positions):
            draw_block(img, x=x, y=292, width=260, depth=88, height=88, color=color, holes=2, rough=spec.get("rough", False), seed=f"{slug}-{i}")
    elif kind == "column":
        draw_block(img, x=490, y=230, width=248, depth=218, height=186, color=spec["color"], holes=1, rough=spec.get("rough", False), seed=slug)
    elif kind == "column-group":
        colors = spec["colors"]
        for i, (x, color) in enumerate([(250, colors[0]), (480, colors[1]), (710, colors[2])]):
            draw_block(img, x=x, y=238, width=206, depth=190, height=165, color=color, holes=1, rough=False, seed=f"{slug}-{i}")
    elif kind == "parapet":
        draw_block(img, x=460, y=300, width=620, depth=138, height=45, color=spec["color"], holes=0, rough=False, seed=slug)
    elif kind == "cap":
        draw_block(img, x=470, y=278, width=420, depth=250, height=54, color=spec["color"], holes=0, rough=False, seed=slug)
    else:
        raise ValueError(f"Unknown kind: {kind}")

    img = normalize_canvas(img)
    img.save(OUT / f"{slug}.webp", "WEBP", quality=96, method=6)


def make_contact_sheet() -> None:
    QA.mkdir(parents=True, exist_ok=True)
    files = sorted(OUT.glob("*.webp"))
    font = ImageFont.load_default()
    tiles = []
    for path in files:
        img = Image.open(path).convert("RGBA")
        bg = Image.new("RGBA", img.size, (247, 247, 249, 255))
        bg.alpha_composite(img)
        bg.thumbnail((230, 132), Image.Resampling.LANCZOS)
        tile = Image.new("RGB", (260, 178), "#ffffff")
        tile.paste(bg.convert("RGB"), ((260 - bg.width) // 2, 12))
        draw = ImageDraw.Draw(tile)
        draw.text((12, 150), path.stem[:34], fill="#1d1d1f", font=font)
        tiles.append(tile)

    cols = 3
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 260, rows * 178), "#e8e8ed")
    for index, tile in enumerate(tiles):
        sheet.paste(tile, ((index % cols) * 260, (index // cols) * 178))
    sheet.save(QA / "generated-products-contact-sheet.jpg", quality=94)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    gray = (132, 138, 143)
    dark_gray = (118, 124, 130)
    red = (178, 46, 62)
    gold = (201, 145, 64)
    plum = (144, 82, 92)
    green = (118, 147, 75)
    brick = (164, 63, 48)

    specs = {
        "ballast-wall-gray": {"kind": "single", "color": gray, "holes": 3},
        "ballast-wall-color": {"kind": "group", "colors": [red, gold, plum], "holes": 2},
        "ballast-wall-torn-gray": {"kind": "single", "color": dark_gray, "holes": 2, "rough": True},
        "ballast-wall-torn-color": {"kind": "group", "colors": [red, green, brick], "holes": 2, "rough": True},
        "ballast-partition-gray": {"kind": "partition", "color": gray},
        "ballast-partition-color": {"kind": "group-partition", "colors": [red, green, red]},
        "ballast-partition-torn-gray": {"kind": "partition", "color": dark_gray, "rough": True},
        "ballast-partition-torn-color": {"kind": "group-partition", "colors": [red, green, brick], "rough": True},
        "ballast-column-gray": {"kind": "column", "color": dark_gray},
        "ballast-column-color": {"kind": "column-group", "colors": [red, green, plum]},
        "ballast-parapet-gray": {"kind": "parapet", "color": (168, 172, 176)},
        "ballast-cap-gray": {"kind": "cap", "color": (160, 164, 169)},
        "otsev-wall-gray": {"kind": "single", "color": (145, 151, 155), "holes": 3},
        "otsev-wall-color": {"kind": "group", "colors": [red, gold, plum], "holes": 2},
        "otsev-wall-torn-gray": {"kind": "single", "color": (130, 136, 140), "holes": 2, "rough": True},
        "otsev-wall-torn-color": {"kind": "group", "colors": [red, green, brick], "holes": 2, "rough": True},
        "otsev-partition-gray": {"kind": "partition", "color": (145, 151, 155)},
    }

    for slug, spec in specs.items():
        render(slug, spec)
    make_contact_sheet()


if __name__ == "__main__":
    main()
