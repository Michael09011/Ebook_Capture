import os
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ICONSET_DIR = os.path.join(BASE_DIR, "ebook_capture.iconset")
ICNS_PATH = os.path.join(BASE_DIR, "ebook_capture.icns")

SIZES = [16, 32, 64, 128, 256, 512]

BG_COLOR = (26, 35, 84)
BOOK_COLOR = (246, 223, 187)
ACCENT_COLOR = (242, 95, 92)
SHADOW_COLOR = (16, 23, 56)


def make_icon(size):
    image = Image.new("RGBA", (size, size), BG_COLOR)
    draw = ImageDraw.Draw(image)

    margin = size // 10
    book_w = size - 2 * margin
    book_h = int(book_w * 0.72)
    book_x = margin
    book_y = size - margin - book_h

    # back page shadow
    draw.rounded_rectangle(
        [book_x + book_w * 0.08, book_y + book_h * 0.04, book_x + book_w + book_w * 0.08, book_y + book_h + book_h * 0.04],
        radius=book_w * 0.08,
        fill=SHADOW_COLOR
    )

    # front book
    draw.rounded_rectangle(
        [book_x, book_y, book_x + book_w, book_y + book_h],
        radius=book_w * 0.1,
        fill=BOOK_COLOR,
        outline=None
    )

    # page fold line
    line_x = book_x + book_w * 0.42
    draw.line(
        [(line_x, book_y + book_h * 0.1), (line_x, book_y + book_h * 0.9)],
        fill=(200, 170, 140),
        width=max(1, size // 40)
    )

    # bookmark accent
    bookmark_w = int(book_w * 0.14)
    bookmark_h = int(book_h * 0.26)
    draw.rectangle(
        [book_x + book_w - bookmark_w - margin // 6, book_y + margin // 2,
         book_x + book_w - margin // 6, book_y + margin // 2 + bookmark_h],
        fill=ACCENT_COLOR
    )
    draw.polygon(
        [
            (book_x + book_w - bookmark_w - margin // 6, book_y + margin // 2 + bookmark_h),
            (book_x + book_w - margin // 6, book_y + margin // 2 + bookmark_h),
            (book_x + book_w - bookmark_w // 2 - margin // 6, book_y + margin // 2 + bookmark_h + bookmark_w // 2)
        ],
        fill=ACCENT_COLOR
    )

    # record dot
    dot_r = max(2, size // 35)
    draw.ellipse(
        [book_x + book_w * 0.65 - dot_r, book_y + book_h * 0.28 - dot_r,
         book_x + book_w * 0.65 + dot_r, book_y + book_h * 0.28 + dot_r],
        fill=ACCENT_COLOR
    )

    return image


def main():
    if os.path.isdir(ICONSET_DIR):
        for filename in os.listdir(ICONSET_DIR):
            path = os.path.join(ICONSET_DIR, filename)
            if os.path.isfile(path):
                os.remove(path)
    else:
        os.makedirs(ICONSET_DIR)

    for size in SIZES:
        image = make_icon(size)
        image.save(os.path.join(ICONSET_DIR, f"icon_{size}x{size}.png"), format="PNG")
        retina = image.resize((size * 2, size * 2), Image.LANCZOS)
        retina.save(os.path.join(ICONSET_DIR, f"icon_{size}x{size}@2x.png"), format="PNG")

    if os.path.exists(ICNS_PATH):
        os.remove(ICNS_PATH)

    os.system(f"iconutil -c icns '{ICONSET_DIR}'")
    print(f"Generated {ICNS_PATH}")


if __name__ == '__main__':
    main()
