"""Render animated pipeline GIFs for each portfolio project.

Usage: python3 scripts/make_pipeline_gifs.py   (writes to gifs/)
Stage data mirrors the .flow blocks in index.html - keep them in sync.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent.parent / "gifs"

BG = (11, 14, 20)
SURFACE = (20, 26, 38)
SURFACE_2 = (25, 32, 46)
LINE = (39, 48, 63)
LINE_BRIGHT = (59, 70, 87)
TEXT = (234, 239, 247)
TEXT_DIM = (179, 190, 206)
TEXT_FAINT = (135, 148, 166)
ACCENT = (111, 216, 230)
ACCENT_DIM = (77, 158, 171)
OK = (127, 184, 138)

W, H = 1200, 380
FPS = 15
FONT_PATH = "/System/Library/Fonts/Menlo.ttc"

PROJECTS = [
    {
        "slug": "delivery-time",
        "title": "ml-based delivery time estimation",
        "stages": [
            ("PostgreSQL", "SQLAlchemy ORM"),
            ("EDA", "predictive features"),
            ("3x XGBoost", "sequential stages"),
            ("GridSearchCV", "hyperparameters"),
            ("Aggregate", "sum → final ETA"),
            ("FastAPI", "REST predictions"),
        ],
        "metric": ("73%", "baseline on-time delivery compliance"),
    },
    {
        "slug": "observability",
        "title": "ai-powered observability platform",
        "stages": [
            ("Raw logs", "unstructured"),
            ("Preprocess", "standardise"),
            ("ChromaDB", "embeddings"),
            ("Hybrid search", "cosine ≥ 0.5"),
            ("Rerank", "MiniLM cross-enc"),
            ("LLM", "root cause"),
        ],
        "metric": ("92 / 95 / 92", "RAG Triad: context rel. / groundedness / answer rel."),
    },
    {
        "slug": "utility-cost",
        "title": "ml-based utility cost estimation",
        "stages": [
            ("Project data", "historical"),
            ("EDA", "cost drivers"),
            ("Features", "engineer + encode"),
            ("Optuna", "tuning"),
            ("XGBoost", "multivariate"),
            ("4 outputs", "costs at once"),
        ],
        "metric": ("R² 0.75–0.78", "material / internal / external labour / misc"),
    },
    {
        "slug": "survey-intelligence",
        "title": "survey intelligence platform",
        "stages": [
            ("MongoDB", "survey responses"),
            ("Beanie ODM", "retrieval"),
            ("OpenCV", "click heatmaps"),
            ("Azure Blob", "image storage"),
            ("Video pulse", "ratings @ reactions"),
            ("FastAPI", "analytics APIs"),
        ],
        "metric": ("heatmap + pulse", "survey analytics served over REST"),
    },
    {
        "slug": "alzheimers-cnn",
        "title": "lightweight cnn for alzheimer's classification",
        "stages": [
            ("MRI datasets", "2 x Mendeley"),
            ("Split 80:10:10", "stratified"),
            ("Augment", "+ SHA-256 dedup"),
            ("3-layer CNN", "16-32-64"),
            ("5-fold CV", "consistency"),
            ("Cross-dataset", "both directions"),
        ],
        "metric": ("98%", "bidirectional cross-dataset accuracy"),
    },
]

STAGE_FRAMES = 10  # frames each stage stays "active" (packet travels during it)
HOLD_FRAMES = 30  # frames holding on the finished pipeline + metric


def font(size, bold=False):
    return ImageFont.truetype(FONT_PATH, size, index=1 if bold else 0)


F_TITLE = font(16)
F_NODE = font(18, bold=True)
F_SUB = font(13)
F_IDX = font(12)
F_METRIC = font(34, bold=True)
F_METRIC_SUB = font(15)


def lerp(a, b, t):
    return tuple(int(x + (y - x) * t) for x, y in zip(a, b))


def node_boxes(n):
    margin, gap = 40, 26
    nw = (W - 2 * margin - gap * (n - 1)) / n
    top, nh = 120, 104
    return [(margin + i * (nw + gap), top, margin + i * (nw + gap) + nw, top + nh) for i in range(n)]


def draw_frame(p, step, sub_t, finished):
    """step = index of active stage; sub_t in [0,1) progress within it."""
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # window chrome
    d.rounded_rectangle((16, 16, W - 16, H - 16), 14, fill=SURFACE, outline=LINE)
    d.rounded_rectangle((16, 16, W - 16, 60), 14, fill=SURFACE_2)
    d.rectangle((16, 46, W - 16, 60), fill=SURFACE_2)
    d.line((16, 60, W - 16, 60), fill=LINE)
    for i in range(3):
        d.ellipse((36 + i * 18, 33, 46 + i * 18, 43), fill=LINE_BRIGHT)
    d.text((106, 29), f"{p['title']} · pipeline", font=F_TITLE, fill=TEXT_FAINT)

    stages = p["stages"]
    boxes = node_boxes(len(stages))

    # connectors + packet
    for i in range(len(stages) - 1):
        x0, y = boxes[i][2], (boxes[i][1] + boxes[i][3]) / 2
        x1 = boxes[i + 1][0]
        done = finished or i < step
        d.line((x0, y, x1, y), fill=ACCENT_DIM if done else LINE_BRIGHT, width=2)
        if not finished and i == step:
            px = x0 + (x1 - x0) * sub_t
            d.ellipse((px - 5, y - 5, px + 5, y + 5), fill=ACCENT)

    for i, ((name, sub), (x0, y0, x1, y1)) in enumerate(zip(stages, boxes)):
        if finished or i < step:
            state = "done"
        elif i == step:
            state = "active"
        else:
            state = "idle"

        if state == "active":
            glow = lerp(SURFACE, ACCENT, 0.18)
            d.rounded_rectangle((x0 - 4, y0 - 4, x1 + 4, y1 + 4), 12, fill=glow)
            d.rounded_rectangle((x0, y0, x1, y1), 10, fill=SURFACE_2, outline=ACCENT, width=2)
            name_c, sub_c, idx_c = TEXT, TEXT_DIM, ACCENT
        elif state == "done":
            d.rounded_rectangle((x0, y0, x1, y1), 10, fill=SURFACE_2, outline=ACCENT_DIM, width=1)
            name_c, sub_c, idx_c = TEXT, TEXT_DIM, ACCENT_DIM
        else:
            d.rounded_rectangle((x0, y0, x1, y1), 10, fill=BG, outline=LINE, width=1)
            name_c, sub_c, idx_c = TEXT_FAINT, LINE_BRIGHT, LINE_BRIGHT

        d.text((x0 + 14, y0 + 12), f"{i + 1:02d}", font=F_IDX, fill=idx_c)
        if state == "done":
            d.text((x1 - 24, y0 + 10), "✓", font=F_IDX, fill=OK)
        d.text((x0 + 14, y0 + 40), name, font=F_NODE, fill=name_c)
        d.text((x0 + 14, y0 + 70), sub, font=F_SUB, fill=sub_c)

    # progress bar
    total = len(stages)
    prog = 1.0 if finished else (step + sub_t) / total
    d.rounded_rectangle((40, 262, W - 40, 266), 2, fill=LINE)
    d.rounded_rectangle((40, 262, 40 + (W - 80) * prog, 266), 2, fill=ACCENT)

    # metric
    value, label = p["metric"]
    if finished:
        d.text((40, 292), value, font=F_METRIC, fill=ACCENT)
        vw = d.textlength(value, font=F_METRIC)
        d.text((40 + vw + 22, 306), label, font=F_METRIC_SUB, fill=TEXT_DIM)
    else:
        d.text((40, 300), f"> running stage {step + 1:02d}/{total:02d} · {stages[step][0]}",
               font=F_METRIC_SUB, fill=TEXT_FAINT)
    return img


def render(p):
    frames = []
    for step in range(len(p["stages"])):
        for f in range(STAGE_FRAMES):
            frames.append(draw_frame(p, step, f / STAGE_FRAMES, False))
    done = draw_frame(p, 0, 0, True)
    frames.extend([done] * HOLD_FRAMES)

    # shared palette sampled from idle, mid-run and finished frames
    sample = Image.new("RGB", (W, H * 3))
    for i, fr in enumerate((frames[0], frames[len(frames) // 3], frames[-1])):
        sample.paste(fr, (0, H * i))
    pal = sample.quantize(colors=64, method=Image.Quantize.MEDIANCUT)
    q = [fr.quantize(palette=pal, dither=Image.Dither.NONE) for fr in frames]
    path = OUT / f"{p['slug']}.gif"
    q[0].save(path, save_all=True, append_images=q[1:], duration=int(1000 / FPS),
              loop=0, optimize=True, disposal=1)
    return path


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for p in PROJECTS:
        path = render(p)
        print(f"{path.name}: {path.stat().st_size // 1024} KB")
