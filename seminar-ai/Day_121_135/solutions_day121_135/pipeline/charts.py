import base64
import html
import sys
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import requests

from core import cache
from pipeline import arc as arc_pipeline
from pipeline import similar as similar_pipeline
from pipeline import summarize as summarize_pipeline
from pipeline.topics import build_corpus

COVER_URL = "https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.cover.medium.jpg"
REPORT_COLORS = ["#2563eb", "#0f766e", "#ea580c", "#7c3aed", "#dc2626", "#0891b2"]

def _save(fig, path):
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return base64.b64encode(path.read_bytes()).decode("ascii")

def lexdiv_chart(metrics, path):
    fig, (left, right) = plt.subplots(1, 2, figsize=(9, 3.2))
    fig.patch.set_facecolor("#ffffff")

    for ax in (left, right):
        ax.set_facecolor("#ffffff")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color("#d0d7de")
        ax.spines["bottom"].set_color("#d0d7de")

    counts = [metrics["tok"], metrics["typ"], metrics["hap"]]
    left.bar(["tokens", "types", "hapax"], counts, color=REPORT_COLORS[0], alpha=0.9)
    left.set_yscale("log")
    left.set_title("Counts (log scale)", fontsize=10, fontweight="bold")
    for index, value in enumerate(counts):
        left.text(index, value, f"{value:,}", ha="center", va="bottom", fontsize=8)

    ratios = [metrics["ttr"], metrics["mwl"], metrics["mwf"]]
    right.bar(
        ["TTR", "mean word len", "mean word freq"],
        ratios,
        color=[REPORT_COLORS[1], REPORT_COLORS[2], REPORT_COLORS[3]],
        alpha=0.9,
    )
    right.set_title("Ratios", fontsize=10, fontweight="bold")
    for index, value in enumerate(ratios):
        right.text(index, value, str(value), ha="center", va="bottom", fontsize=8)

    return _save(fig, path)

def compare_chart(comparison, path):
    algorithms = comparison["algorithms"]
    names = list(algorithms)
    labels = [name.upper() for name in names]

    fig, axes = plt.subplots(1, 3, figsize=(10, 3.2))
    fig.patch.set_facecolor("#ffffff")
    panels = [
        ("coherence_umass", "UMass coherence (closer to 0 = better)"),
        ("diversity", "Topic diversity"),
        ("seconds", "Fit time (s)"),
    ]
    for panel_index, (axis, (key, title)) in enumerate(zip(axes, panels)):
        axis.set_facecolor("#ffffff")
        axis.spines["top"].set_visible(False)
        axis.spines["right"].set_visible(False)
        axis.spines["left"].set_color("#d0d7de")
        axis.spines["bottom"].set_color("#d0d7de")
        values = [algorithms[name][key] or 0 for name in names]
        axis.bar(labels, values, color=REPORT_COLORS[panel_index], alpha=0.9)
        axis.set_title(title, fontsize=9, fontweight="bold")
        axis.tick_params(labelsize=9)

    best = comparison.get("best")
    if best:
        fig.suptitle(f"Best: {best.upper()}", fontsize=11, fontweight="bold", color=REPORT_COLORS[0])
    return _save(fig, path)

def _style(fig, title):
    fig.update_layout(
        template="simple_white",
        title=dict(text=title, font=dict(size=16, color="#1f2937")),
        height=460,
        margin=dict(l=40, r=40, t=50, b=40),
        font=dict(family="system-ui, sans-serif", color="#374151"),
        xaxis=dict(showgrid=True, gridcolor="#e5e7eb", zerolinecolor="#d1d5db"),
        yaxis=dict(showgrid=True, gridcolor="#e5e7eb", zerolinecolor="#d1d5db"),
    )
    return fig

def charts_html(figures):
    charts = {}
    include_js = True
    for name, fig in figures.items():
        if fig is None:
            charts[name] = None
            continue
        charts[name] = fig.to_html(
            full_html=False, include_plotlyjs=include_js, config={"displaylogo": False}
        )
        include_js = False
    return charts

def write_plotly_images(figures, out_dir):
    files = {
        "kmeans": out_dir / "kmeans.png",
        "arc": out_dir / "arc.png",
        "galaxy": out_dir / "galaxy.png",
    }
    for name, path in files.items():
        fig = figures.get(name)
        if fig is None:
            continue
        try:
            fig.write_image(path, format="png", width=1100, height=650, scale=2)
        except Exception as error:
            sys.stderr.write(
                f"bookworm: warning: could not export {path.name} with kaleido "
                f"({error})\n"
            )

def _hover_text(text, width=70, max_chars=240):
    if len(text) > max_chars:
        text = text[:max_chars].rsplit(" ", 1)[0] + "…"
    return "<br>".join(textwrap.wrap(html.escape(text), width))

def kmeans_fig(book):
    clusters = summarize_pipeline.cluster_map(book)
    if clusters is None:
        return None

    coords, labels = clusters["coords"], clusters["labels"]
    selected = clusters["selected"]
    hover = [_hover_text(text) for text in clusters["texts"]]
    shared_scale = dict(colorscale="Plasma", cmin=int(labels.min()), cmax=int(labels.max()))

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=coords[:, 0], y=coords[:, 1], mode="markers", name="Sentences",
        marker=dict(color=labels, size=8, opacity=0.45, line=dict(width=0), **shared_scale),
        text=hover, hoverinfo="text",
    ))
    fig.add_trace(go.Scatter(
        x=coords[selected, 0], y=coords[selected, 1], mode="markers", name="Selected summary",
        marker=dict(
            color=[int(labels[i]) for i in selected], size=16,
            line=dict(color="#ffffff", width=2), **shared_scale,
        ),
        text=[hover[i] for i in selected], hoverinfo="text",
    ))
    return _style(fig, "Sentence clusters — K-Means on TF-IDF (SVD projection)")

def silhouette_fig(book):
    scores = summarize_pipeline.silhouette_profile(book)
    if not scores:
        return None

    ks = sorted(scores)
    values = [scores[k] for k in ks]
    fig = go.Figure(go.Scatter(
        x=ks,
        y=values,
        mode="lines+markers",
        line=dict(color=REPORT_COLORS[1], width=3),
        marker=dict(size=9, color=REPORT_COLORS[3], line=dict(color="#fff", width=1)),
        hovertemplate="k=%{x}<br>silhouette=%{y:.4f}<extra></extra>",
    ))
    if summarize_pipeline.NUM_SENTENCES in scores:
        fig.add_vline(
            x=summarize_pipeline.NUM_SENTENCES,
            line_dash="dot",
            line_color="#adb5bd",
            annotation_text="summary k",
        )
    return _style(fig, "Summary validation — silhouette score by k")

def arc_fig(book):
    try:
        sentiments = cache.cached(
            book.id, "arc", lambda: arc_pipeline.arc(book), version=arc_pipeline.CACHE_VERSION
        )
    except LookupError:
        return None
    if len(sentiments) < 2:
        return None

    sections = sorted(sentiments, key=int)
    fig = go.Figure(go.Scatter(
        x=[int(key) for key in sections],
        y=[sentiments[key] for key in sections],
        mode="lines+markers",
        line=dict(shape="spline", smoothing=1.1, width=3, color=REPORT_COLORS[0]),
        marker=dict(size=7, color=REPORT_COLORS[2]),
        hovertemplate="Section %{x}<br>Sentiment %{y:.3f}<extra></extra>",
    ))
    fig.add_hline(y=0, line_dash="dot", line_color="#adb5bd")
    return _style(fig, "Narrative arc — mean VADER sentiment per section")

def galaxy_fig(book):
    galaxy = similar_pipeline.galaxy_map(book)
    if galaxy is None:
        return None

    fig = go.Figure()
    symbols = ["circle", "square", "diamond", "cross", "x", "triangle-up", "star"]
    cluster_labels = galaxy.get("cluster_labels") or [0] * len(galaxy["ids"])

    def hover_line(i):
        lines = [html.escape(galaxy["titles"][i])]
        ranks = galaxy.get("ranks") or []
        scores = galaxy.get("scores") or []
        if i < len(ranks) and ranks[i]:
            lines.append(f"Rank {ranks[i]}")
        if i < len(scores) and scores[i] is not None:
            lines.append(f"Similarity {scores[i]:.3f}")
        lines.append(f"Cluster {cluster_labels[i]}")
        return "<br>".join(lines)

    category_order = galaxy.get("category_order") or sorted(set(galaxy["categories"]))
    for index, category in enumerate(category_order):
        points = [i for i, cat in enumerate(galaxy["categories"]) if cat == category]
        if not points:
            continue
        fig.add_trace(go.Scatter(
            x=[galaxy["x"][i] for i in points], y=[galaxy["y"][i] for i in points],
            mode="markers", name=category,
            marker=dict(
                color=REPORT_COLORS[index % len(REPORT_COLORS)],
                symbol=[symbols[int(cluster_labels[i]) % len(symbols)] for i in points],
                size=12,
                opacity=0.85,
                line=dict(color="#ffffff", width=0.75),
            ),
            text=[hover_line(i) for i in points],
            hoverinfo="text",
        ))

    focus_index = galaxy.get("focus_index")
    if focus_index is None and book.id in galaxy["ids"]:
        focus_index = galaxy["ids"].index(book.id)
    if focus_index is not None:
        pos = focus_index
        fig.add_trace(go.Scatter(
            x=[galaxy["x"][pos]], y=[galaxy["y"][pos]],
            mode="markers", name="This book",
            marker=dict(symbol="star", size=22, color="#ffd700", line=dict(color="#ffffff", width=2)),
            text=[hover_line(pos)], hoverinfo="text",
        ))
    if galaxy.get("mode") == "full":
        title = (
            f"Local galaxy - {len(galaxy['ids']) - 1} nearest books "
            f"from {galaxy.get('source_size', '?')} local texts"
        )
    else:
        title = "Catalog galaxy - category color, silhouette cluster symbol"
    if galaxy.get("cluster_k") is not None:
        title += f" (k={galaxy['cluster_k']}, score={galaxy['cluster_score']})"
    return _style(fig, title)

def fetch_cover(book_id, path):
    try:
        response = requests.get(COVER_URL.format(book_id=book_id), timeout=15)
    except requests.RequestException:
        return None
    if response.status_code != 200:
        return None
    path.write_bytes(response.content)
    return base64.b64encode(response.content).decode("ascii")
