from __future__ import annotations

import math
from pathlib import Path
from typing import Iterable

import imageio.v2 as imageio
import numpy as np
from PIL import Image, ImageColor, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
SOURCE = ASSETS / "source"
DOCS = ROOT / "docs"
SITE_ASSETS = DOCS / "site-assets"

HERO_PATH = ASSETS / "tax-treaty-agent-demo.png"
PREVIEW_GIF_PATH = ASSETS / "tax-treaty-agent-guided-demo.gif"
EXTENDED_GIF_PATH = ASSETS / "tax-treaty-agent-guided-demo-extended.gif"
WALKTHROUGH_MAIN_MP4_PATH = SITE_ASSETS / "walkthrough-main.mp4"
WALKTHROUGH_MAIN_POSTER_PATH = SITE_ASSETS / "walkthrough-main-poster.png"


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


FONT_H1 = load_font(58, bold=True)
FONT_H2 = load_font(26, bold=True)
FONT_BODY = load_font(24)
FONT_SMALL = load_font(18)
FONT_BADGE = load_font(20, bold=True)


BG = ImageColor.getrgb("#f4efe8")
CARD = ImageColor.getrgb("#fbf8f4")
BORDER = ImageColor.getrgb("#d9d0c5")
TEXT = ImageColor.getrgb("#2c2924")
MUTED = ImageColor.getrgb("#6d655e")
ACCENT = ImageColor.getrgb("#1f4f7a")
ACCENT_SOFT = ImageColor.getrgb("#e2edf7")
ACCENT_WARM = ImageColor.getrgb("#f2e2cb")


def rounded_mask(size: tuple[int, int], radius: int) -> Image.Image:
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, size[0], size[1]), radius=radius, fill=255)
    return mask


def card_shadow(size: tuple[int, int], radius: int = 24, blur: int = 18) -> Image.Image:
    shadow = Image.new("RGBA", (size[0] + blur * 4, size[1] + blur * 4), (0, 0, 0, 0))
    draw = ImageDraw.Draw(shadow)
    draw.rounded_rectangle(
        (blur * 2, blur * 2, blur * 2 + size[0], blur * 2 + size[1]),
        radius=radius,
        fill=(0, 0, 0, 42),
    )
    return shadow.filter(ImageFilter.GaussianBlur(blur))


def paste_card(
    canvas: Image.Image,
    image: Image.Image,
    box: tuple[int, int, int, int],
    radius: int = 28,
) -> None:
    x0, y0, x1, y1 = box
    width = x1 - x0
    height = y1 - y0
    shadow = card_shadow((width, height), radius=radius)
    canvas.alpha_composite(shadow, (x0 - 36, y0 - 30))
    card = Image.new("RGBA", (width, height), CARD + (255,))
    draw = ImageDraw.Draw(card)
    draw.rounded_rectangle((0, 0, width - 1, height - 1), radius=radius, fill=CARD, outline=BORDER, width=2)
    fitted = ImageOps.fit(image, (width - 24, height - 24), method=Image.Resampling.LANCZOS)
    mask = rounded_mask((width - 24, height - 24), radius=max(16, radius - 8))
    card.paste(fitted, (12, 12), mask)
    canvas.alpha_composite(card, (x0, y0))


def crop(img: Image.Image, box: tuple[int, int, int, int]) -> Image.Image:
    return img.crop(box).convert("RGBA")


def make_badge(draw: ImageDraw.ImageDraw, x: int, y: int, text: str, fill: tuple[int, int, int], fg: tuple[int, int, int]) -> int:
    bbox = draw.textbbox((0, 0), text, font=FONT_BADGE)
    width = bbox[2] - bbox[0] + 32
    height = bbox[3] - bbox[1] + 18
    draw.rounded_rectangle((x, y, x + width, y + height), radius=height // 2, fill=fill)
    draw.text((x + 16, y + 9), text, font=FONT_BADGE, fill=fg)
    return width


def scene_canvas(title: str, subtitle: str, image: Image.Image) -> Image.Image:
    canvas = Image.new("RGBA", (960, 720), BG + (255,))
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle((26, 28, 934, 692), radius=30, fill=(255, 255, 255, 82), outline=(255, 255, 255, 110))
    draw.text((54, 44), title, font=FONT_H2, fill=TEXT)
    draw.text((54, 82), subtitle, font=FONT_SMALL, fill=MUTED)
    paste_card(canvas, image, (54, 128, 906, 668), radius=24)
    return canvas


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def ease(t: float) -> float:
    return 0.5 - 0.5 * math.cos(math.pi * t)


def build_cursor(size: int = 44) -> Image.Image:
    cursor = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(cursor)
    points = [
        (4, 2),
        (4, 34),
        (12, 26),
        (18, 40),
        (25, 37),
        (19, 23),
        (31, 23),
    ]
    shadow = [(x + 2, y + 3) for x, y in points]
    draw.polygon(shadow, fill=(0, 0, 0, 80))
    draw.polygon(points, fill=(18, 18, 18, 255))
    draw.line(points + [points[0]], fill=(255, 255, 255, 220), width=2)
    return cursor


CURSOR = build_cursor()


def add_cursor(canvas: Image.Image, pos: tuple[float, float], click: float = 0.0) -> Image.Image:
    frame = canvas.copy()
    halo = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(halo)
    x, y = pos
    base_radius = 18 + int(6 * click)
    draw.ellipse((x - base_radius, y - base_radius, x + base_radius, y + base_radius), fill=(255, 206, 84, int(90 + 60 * click)))
    if click > 0:
        ring = 24 + int(18 * click)
        draw.ellipse((x - ring, y - ring, x + ring, y + ring), outline=(255, 206, 84, int(160 - 120 * click)), width=4)
    halo = halo.filter(ImageFilter.GaussianBlur(6))
    frame.alpha_composite(halo)
    frame.alpha_composite(CURSOR, (int(x) - 6, int(y) - 4))
    return frame


def crossfade(a: Image.Image, b: Image.Image, steps: int) -> list[Image.Image]:
    return [Image.blend(a, b, alpha=(i + 1) / (steps + 1)) for i in range(steps)]


def animate_pointer(
    canvas: Image.Image,
    start: tuple[float, float],
    end: tuple[float, float],
    frames: int,
    click_at_end: bool = False,
) -> list[Image.Image]:
    results: list[Image.Image] = []
    for i in range(frames):
        t = 0 if frames == 1 else i / (frames - 1)
        eased = ease(t)
        x = lerp(start[0], end[0], eased)
        y = lerp(start[1], end[1], eased)
        click = 0.0
        if click_at_end and t > 0.7:
            click = (t - 0.7) / 0.3
        results.append(add_cursor(canvas, (x, y), click=click))
    return results


def save_gif(path: Path, frames: Iterable[Image.Image], duration_ms: int) -> int:
    items = [frame.convert("P", palette=Image.Palette.ADAPTIVE, colors=255) for frame in frames]
    if not items:
        raise ValueError("no frames to save")
    items[0].save(
        path,
        save_all=True,
        append_images=items[1:],
        duration=duration_ms,
        loop=0,
        optimize=False,
        disposal=2,
    )
    return len(items)


def save_mp4(path: Path, frames: Iterable[Image.Image], fps: int = 18) -> int:
    items = [frame.convert("RGB") for frame in frames]
    if not items:
        raise ValueError("no frames to save")
    with imageio.get_writer(
        path,
        fps=fps,
        codec="libx264",
        quality=8,
        pixelformat="yuv420p",
        macro_block_size=1,
    ) as writer:
        for frame in items:
            writer.append_data(np.asarray(frame))
    return len(items)


def save_first_frame(path: Path, frame: Image.Image) -> None:
    frame.convert("RGB").save(path, quality=95)


def hold(frame: Image.Image, count: int) -> list[Image.Image]:
    return [frame.copy() for _ in range(count)]


def build_assets() -> None:
    SITE_ASSETS.mkdir(parents=True, exist_ok=True)
    empty_form = Image.open(SOURCE / "guided-step-0.png").convert("RGBA")
    filled_form = Image.open(SOURCE / "guided-step-1.png").convert("RGBA")
    result_view = Image.open(SOURCE / "guided-step-2.png").convert("RGBA")
    legacy_layout = Image.open(SOURCE / "legacy-demo-layout.png").convert("RGBA")

    form_empty_top = crop(empty_form, (80, 90, 900, 1230))
    form_filled_top = crop(filled_form, (80, 90, 900, 1230))
    form_run_crop = crop(filled_form, (70, 700, 930, 1480))
    result_crop = crop(result_view, (70, 720, 930, 1530))
    handoff_crop = crop(legacy_layout, (450, 120, 900, 980))
    hero_form = ImageOps.fit(form_filled_top, (900, 700), method=Image.Resampling.LANCZOS)
    hero_result = ImageOps.fit(result_crop, (920, 620), method=Image.Resampling.LANCZOS)
    hero_handoff = ImageOps.fit(handoff_crop, (760, 980), method=Image.Resampling.LANCZOS)

    hero = Image.new("RGBA", (1600, 960), BG + (255,))
    draw = ImageDraw.Draw(hero)
    draw.ellipse((1040, -40, 1560, 480), fill=ACCENT_SOFT + (255,))
    draw.ellipse((-120, 700, 320, 1100), fill=ACCENT_WARM + (255,))
    draw.text((108, 96), "Tax Treaty Agent", font=FONT_H1, fill=TEXT)
    draw.text((110, 174), "Guided treaty pre-screening with conservative outputs and workflow-ready handoff.", font=FONT_BODY, fill=MUTED)
    badge_x = 108
    badge_x += make_badge(draw, badge_x, 230, "3 treaty pairs", ACCENT_SOFT, ACCENT) + 14
    badge_x += make_badge(draw, badge_x, 230, "guided review", ACCENT_WARM, TEXT) + 14
    make_badge(draw, badge_x, 230, "human-reviewed compiler", (228, 241, 230), (38, 98, 53))
    draw.text((108, 304), "Guide the facts", font=FONT_H2, fill=TEXT)
    draw.text((824, 304), "Return a structured result", font=FONT_H2, fill=TEXT)
    paste_card(hero, hero_form, (108, 346, 744, 842), radius=30)
    paste_card(hero, hero_result, (824, 346, 1492, 842), radius=30)
    draw.text((108, 872), "Bounded input keeps the review path explicit.", font=FONT_SMALL, fill=MUTED)
    draw.text((824, 872), "Structured output carries review and handoff detail.", font=FONT_SMALL, fill=MUTED)
    hero.convert("RGB").save(HERO_PATH, quality=95)
    hero.convert("RGB").save(SITE_ASSETS / "hero-cover.png", quality=95)
    hero_form.convert("RGB").save(SITE_ASSETS / "guided-facts-panel.png", quality=95)
    hero_result.convert("RGB").save(SITE_ASSETS / "review-result-panel.png", quality=95)
    hero_handoff.convert("RGB").save(SITE_ASSETS / "workflow-handoff-panel.png", quality=95)

    scene_a = scene_canvas("Guided review starts in the wizard", "The product opens directly into a bounded fact-collection flow.", form_empty_top)
    scene_b = scene_canvas("Raw dividend facts are entered directly", "The reduced-rate branch is driven by structured facts, not free-form model recall.", form_filled_top)
    scene_c = scene_canvas("The user runs a guided review", "The main action stays focused on the workflow path instead of chat.", form_run_crop)
    scene_d = scene_canvas("Structured output and review state return", "The result card makes the treaty lane and review status immediately visible.", result_crop)
    scene_e = scene_canvas("Workflow handoff is ready downstream", "The handoff package is designed for human review, not just display.", handoff_crop)

    short_frames: list[Image.Image] = []
    short_frames += animate_pointer(scene_a, (300, 210), (350, 250), 10)
    short_frames += crossfade(short_frames[-1], add_cursor(scene_b, (340, 236)), 4)
    short_frames += animate_pointer(scene_b, (340, 236), (385, 282), 10)
    short_frames += crossfade(short_frames[-1], add_cursor(scene_c, (430, 470)), 4)
    short_frames += animate_pointer(scene_c, (430, 470), (438, 472), 12, click_at_end=True)
    short_frames.append(add_cursor(scene_d, (700, 224)))
    short_frames += animate_pointer(scene_d, (700, 224), (710, 392), 18)
    short_frame_count = save_gif(PREVIEW_GIF_PATH, short_frames, duration_ms=90)

    extended_frames: list[Image.Image] = []
    extended_frames += animate_pointer(scene_a, (300, 210), (350, 250), 16)
    extended_frames += [extended_frames[-1]] * 16
    extended_frames += crossfade(extended_frames[-1], add_cursor(scene_b, (340, 236)), 8)
    extended_frames += animate_pointer(scene_b, (340, 236), (385, 282), 16)
    extended_frames += [extended_frames[-1]] * 18
    extended_frames += crossfade(extended_frames[-1], add_cursor(scene_c, (430, 470)), 8)
    extended_frames += animate_pointer(scene_c, (430, 470), (438, 472), 18, click_at_end=True)
    extended_frames += [extended_frames[-1]] * 18
    extended_frames.append(add_cursor(scene_d, (700, 224)))
    extended_frames += animate_pointer(scene_d, (700, 224), (710, 392), 22)
    extended_frames += [extended_frames[-1]] * 18
    extended_frames += crossfade(extended_frames[-1], add_cursor(scene_e, (700, 216)), 10)
    extended_frames += animate_pointer(scene_e, (700, 216), (704, 520), 24)
    extended_frames += [extended_frames[-1]] * 24
    extended_frame_count = save_gif(EXTENDED_GIF_PATH, extended_frames, duration_ms=120)

    short_seconds = round(short_frame_count * 0.09, 1)
    extended_seconds = round(extended_frame_count * 0.12, 1)

    walkthrough_frames: list[Image.Image] = []
    walkthrough_frames += animate_pointer(scene_a, (250, 214), (356, 250), 20, click_at_end=True)
    walkthrough_frames += hold(walkthrough_frames[-1], 14)
    walkthrough_frames += crossfade(walkthrough_frames[-1], add_cursor(scene_b, (338, 236)), 10)
    walkthrough_frames += animate_pointer(scene_b, (338, 236), (382, 282), 20, click_at_end=True)
    walkthrough_frames += hold(walkthrough_frames[-1], 14)
    walkthrough_frames += animate_pointer(walkthrough_frames[-1], (382, 282), (428, 334), 18, click_at_end=True)
    walkthrough_frames += hold(walkthrough_frames[-1], 12)
    walkthrough_frames += animate_pointer(walkthrough_frames[-1], (428, 334), (468, 386), 18, click_at_end=True)
    walkthrough_frames += hold(walkthrough_frames[-1], 16)
    walkthrough_frames += crossfade(walkthrough_frames[-1], add_cursor(scene_c, (430, 470)), 10)
    walkthrough_frames += animate_pointer(scene_c, (430, 470), (438, 472), 20, click_at_end=True)
    walkthrough_frames += hold(walkthrough_frames[-1], 18)
    walkthrough_frames += crossfade(walkthrough_frames[-1], add_cursor(scene_d, (690, 212)), 10)
    walkthrough_frames += animate_pointer(scene_d, (690, 212), (696, 304), 22, click_at_end=True)
    walkthrough_frames += hold(walkthrough_frames[-1], 16)
    walkthrough_frames += animate_pointer(walkthrough_frames[-1], (696, 304), (704, 432), 22, click_at_end=True)
    walkthrough_frames += hold(walkthrough_frames[-1], 16)
    walkthrough_frames += crossfade(walkthrough_frames[-1], add_cursor(scene_e, (690, 214)), 10)
    walkthrough_frames += animate_pointer(scene_e, (690, 214), (696, 516), 26, click_at_end=True)
    walkthrough_frames += hold(walkthrough_frames[-1], 16)
    walkthrough_frames += animate_pointer(walkthrough_frames[-1], (696, 516), (244, 132), 22, click_at_end=True)
    walkthrough_frames += hold(walkthrough_frames[-1], 24)

    save_mp4(WALKTHROUGH_MAIN_MP4_PATH, walkthrough_frames)
    save_first_frame(WALKTHROUGH_MAIN_POSTER_PATH, walkthrough_frames[0])

    print(f"hero={HERO_PATH.name}")
    print(f"preview_gif={PREVIEW_GIF_PATH.name} frames={short_frame_count} seconds={short_seconds}")
    print(f"extended_gif={EXTENDED_GIF_PATH.name} frames={extended_frame_count} seconds={extended_seconds}")
    print(f"walkthrough_mp4={WALKTHROUGH_MAIN_MP4_PATH.name}")


if __name__ == "__main__":
    build_assets()
