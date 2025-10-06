import os, math, glob
from PIL import Image, ImageOps, ImageDraw, ImageFont

# -------- CONFIG --------
INPUT_DIR = "dashboards"               # folder with your dashboard images
OUTPUT_GIF = "bny_dashboards_mosaic.gif"
OUTPUT_SIZE = (1600, 900)              # final GIF size (W,H) - 16:9 works well for screens
BG_COLOR = (10, 12, 18)                # deep charcoal background
GUTTER = 14                            # spacing between tiles (px)
PADDING = 24                           # outer padding around the grid (px)
ROUNDED = 18                           # rounded-corner radius for tiles
FPS = 12                               # GIF frame rate (approx)
DURATION_SEC = 5                       # total duration of GIF
ZOOM_START, ZOOM_END = 1.00, 1.06      # subtle Ken Burns zoom on the whole mosaic
TITLE = "BNY Dashboards"
SHOW_TITLE = True
TITLE_COLOR = (230, 235, 255)
TITLE_SHADOW = (0, 0, 0, 160)
TITLE_PAD = 60                         # extra top space when title is shown
LOGO_PATH = "bny_logo.png"             # set to None to disable
LOGO_MAX_W = 180                       # max logo width
LOGO_OPACITY = 210                     # 0-255
# ------------------------

# 1) Collect images
paths = []
for ext in ("*.png", "*.jpg", "*.jpeg", "*.webp"):
    paths.extend(glob.glob(os.path.join(INPUT_DIR, ext)))
paths = sorted(paths)
if not paths:
    raise SystemExit(f"No images found in '{INPUT_DIR}'. Add dashboard screenshots and try again.")

# 2) Decide grid (rows x cols) near-square
n = len(paths)
cols = math.ceil(math.sqrt(n))
rows = math.ceil(n / cols)

# 3) Compute working canvas (add space for title)
W, H = OUTPUT_SIZE
top_pad = PADDING + (TITLE_PAD if SHOW_TITLE else 0)
grid_w = W - 2*PADDING
grid_h = H - top_pad - PADDING

# 4) Cell size
cell_w = (grid_w - (cols - 1) * GUTTER) // cols
cell_h = (grid_h - (rows - 1) * GUTTER) // rows
cell_size = (cell_w, cell_h)

# Helper to paste with rounded corners
def rounded_tile(img, size, radius, bg=BG_COLOR):
    tile_bg = Image.new("RGB", size, bg)
    # Fit image inside cell preserving aspect
    fitted = ImageOps.contain(img, (size[0], size[1]))
    # Center it
    off = ((size[0] - fitted.width)//2, (size[1] - fitted.height)//2)
    tile_bg.paste(fitted, off)

    # Rounded mask
    mask = Image.new("L", size, 0)
    corner = Image.new("L", (radius*2, radius*2), 0)
    draw = ImageDraw.Draw(corner)
    draw.ellipse((0, 0, radius*2-1, radius*2-1), fill=255)
    # create full mask
    mask.paste(corner.crop((0, 0, radius, radius)), (0, 0))
    mask.paste(corner.crop((radius, 0, radius*2, radius)), (size[0]-radius, 0))
    mask.paste(corner.crop((0, radius, radius, radius*2)), (0, size[1]-radius))
    mask.paste(corner.crop((radius, radius, radius*2, radius*2)), (size[0]-radius, size[1]-radius))
    draw = ImageDraw.Draw(mask)
    draw.rectangle((radius, 0, size[0]-radius, size[1]), fill=255)
    draw.rectangle((0, radius, size[0], size[1]-radius), fill=255)

    # Apply mask onto slightly elevated card
    card = Image.new("RGB", size, BG_COLOR)
    card.paste(tile_bg, (0, 0), mask)
    # add soft outline
    outline = Image.new("RGBA", size, (255, 255, 255, 0))
    d2 = ImageDraw.Draw(outline)
    d2.rounded_rectangle((0.5, 0.5, size[0]-0.5, size[1]-0.5), radius, outline=(255,255,255,28), width=1)
    card = Image.alpha_composite(card.convert("RGBA"), outline).convert("RGB")
    return card

# 5) Build the base mosaic
base = Image.new("RGB", (W, H), BG_COLOR)

# Title
if SHOW_TITLE:
    draw = ImageDraw.Draw(base)
    try:
        # Try to use a nicer font if available. Fallback to default.
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()
    text = TITLE
    tw, th = draw.textbbox((0, 0), text, font=font)[2:]
    tx = (W - tw) // 2
    ty = PADDING
    # shadow
    shadow = Image.new("RGBA", base.size, (0,0,0,0))
    sd = ImageDraw.Draw(shadow)
    sd.rectangle((tx-14, ty-10, tx+tw+14, ty+th+10), fill=TITLE_SHADOW)
    base = Image.alpha_composite(base.convert("RGBA"), shadow).convert("RGB")
    draw = ImageDraw.Draw(base)
    draw.text((tx, ty), text, font=font, fill=TITLE_COLOR)

# Logo
if LOGO_PATH and os.path.exists(LOGO_PATH):
    logo = Image.open(LOGO_PATH).convert("RGBA")
    # scale logo
    ratio = min(LOGO_MAX_W / logo.width, 1.0)
    logo = logo.resize((int(logo.width*ratio), int(logo.height*ratio)), Image.LANCZOS)
    # apply opacity
    if logo.mode != "RGBA":
        logo = logo.convert("RGBA")
    alpha = logo.split()[3].point(lambda p: p * (LOGO_OPACITY/255.0))
    logo.putalpha(alpha)
    margin = 20
    lx = W - logo.width - margin
    ly = margin + (TITLE_PAD if SHOW_TITLE else 0)
    base.paste(logo, (lx, ly), logo)

# Tiles
x0 = PADDING
y0 = top_pad
positions = []
idx = 0
for r in range(rows):
    for c in range(cols):
        if idx >= n:
            break
        img = Image.open(paths[idx]).convert("RGB")
        tile = rounded_tile(img, cell_size, ROUNDED, BG_COLOR)
        px = x0 + c * (cell_w + GUTTER)
        py = y0 + r * (cell_h + GUTTER)
        base.paste(tile, (px, py))
        positions.append((px, py))
        idx += 1

# 6) Animate a subtle zoom (Ken Burns) over the whole mosaic
frames = []
total_frames = max(1, int(FPS * DURATION_SEC))
for i in range(total_frames):
    t = i / max(1, total_frames - 1)
    zoom = ZOOM_START + (ZOOM_END - ZOOM_START) * t
    # scale up
    zoom_w, zoom_h = int(W * zoom), int(H * zoom)
    big = base.resize((zoom_w, zoom_h), Image.LANCZOS)
    # slight diagonal pan: start top-left, end center-cropped
    cx = int((zoom_w - W) * t / 2)
    cy = int((zoom_h - H) * t / 2)
    crop = big.crop((cx, cy, cx + W, cy + H))
    frames.append(crop)

# 7) Save GIF
# duration per frame in ms
per_frame_ms = int(1000 / FPS)
frames[0].save(
    OUTPUT_GIF,
    save_all=True,
    append_images=frames[1:],
    duration=per_frame_ms,
    loop=0,
    optimize=True,
    disposal=2,
)

print(f"✅ Created {OUTPUT_GIF} with {len(frames)} frames at ~{FPS} fps.")