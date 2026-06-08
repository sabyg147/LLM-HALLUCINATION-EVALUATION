import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import io, base64

BG   = '#060610'
ACC  = '#6c63ff'
ACC2 = '#a78bfa'
GRN  = '#22d3a0'
RED  = '#f43f5e'
YLW  = '#fbbf24'
BLU  = '#3b82f6'
MUT  = '#3a3a5c'
MUT2 = '#6b6b80'

def fig_to_b64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    buf.seek(0)
    return base64.b64encode(buf.read()).decode()

def make_pipeline_diagram():
    fig = plt.figure(figsize=(18, 10), facecolor=BG)
    ax  = fig.add_axes([0.02, 0.02, 0.96, 0.96])
    ax.set_facecolor(BG)
    ax.set_xlim(0, 18)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # ── helpers ──
    def node(x, y, title, sub, color, r=0.55):
        for a, rr in [(0.05, r+0.35),(0.10, r+0.18)]:
            ax.add_patch(plt.Circle((x,y), rr, color=color, alpha=a, zorder=1))
        ax.add_patch(plt.Circle((x,y), r, color=color, alpha=0.20, zorder=2))
        ax.add_patch(plt.Circle((x,y), r, fill=False, edgecolor=color, lw=2.2, zorder=3))
        ax.text(x, y+0.14, title, ha='center', va='center', color='white',
                fontsize=8, fontweight='bold', linespacing=1.4, zorder=4)
        ax.text(x, y-0.34, sub, ha='center', va='center', color=color,
                fontsize=6.8, fontweight='600', zorder=4)

    def small_node(x, y, title, sub, color, r=0.38):
        ax.add_patch(plt.Circle((x,y), r+0.12, color=color, alpha=0.07, zorder=1))
        ax.add_patch(plt.Circle((x,y), r, color=color, alpha=0.15, zorder=2))
        ax.add_patch(plt.Circle((x,y), r, fill=False, edgecolor=color, lw=1.6, zorder=3))
        ax.text(x, y+0.10, title, ha='center', va='center', color='white',
                fontsize=7, fontweight='bold', linespacing=1.3, zorder=4)
        ax.text(x, y-0.25, sub, ha='center', va='center', color=color,
                fontsize=6, fontweight='600', zorder=4)

    def arrow(x0,y0,x1,y1, color=MUT2, label='', rad=0.0, loff=(0,-0.3), lcolor=None):
        ax.annotate('', xy=(x1,y1), xytext=(x0,y0),
            arrowprops=dict(arrowstyle='->', color=color, lw=1.6,
                            connectionstyle=f'arc3,rad={rad}'))
        if label:
            mx = (x0+x1)/2 + loff[0]
            my = (y0+y1)/2 + loff[1]
            ax.text(mx, my, label, ha='center', color=lcolor or MUT2,
                    fontsize=6.2, fontstyle='italic')

    def badge(x, y, text, color=ACC2, fs=6.8):
        ax.text(x, y, text, ha='center', va='center', color=color,
                fontsize=fs, fontweight='700',
                bbox=dict(facecolor='#0d0d20', edgecolor=color,
                          boxstyle='round,pad=0.38', linewidth=0.9))

    def box(x, y, w, h, color, title, lines):
        ax.add_patch(plt.Rectangle((x,y), w, h,
            linewidth=1.5, edgecolor=color, facecolor='#0d0d20',
            zorder=2, alpha=0.95))
        ax.text(x+w/2, y+h-0.25, title, ha='center', color=color,
                fontsize=7.5, fontweight='bold')
        for i, l in enumerate(lines):
            ax.text(x+w/2, y+h-0.55-i*0.28, l, ha='center', color='#c8c8d8',
                    fontsize=6.5, linespacing=1.3)

    # ── TITLE ──
    ax.text(0.3, 9.65, 'LLM Hallucination Detection Pipeline  ·  V2.0',
            color='white', fontsize=13, fontweight='bold')
    ax.text(0.3, 9.2,
            'Self-healing cascade: LLaMA-3.1-8B  →  Qwen3-32B  →  RAG ChromaDB  →  Verified Answer',
            color=MUT2, fontsize=8.5)

    # ── DASHED SECURITY LINE ──
    ax.plot([0.3,17.7],[8.6,8.6], color=ACC, lw=0.7, ls='--', alpha=0.25)
    ax.text(0.3, 8.75, 'SECURITY PERIMETER', color=ACC, fontsize=6.5,
            fontweight='700', alpha=0.6)

    # ── SECURITY BADGES ──
    for bx,bt in [
        (2.8,  '🔒 Layer 1\nInput Sanitize'),
        (6.0,  '🔑 Layer 2\nAccess Control'),
        (10.2, '🔍 Layer 3\nRAG Fallback'),
        (14.5, '🛡 Layer 4\nOutput Filter'),
    ]:
        badge(bx, 8.25, bt, ACC2, 6.5)

    # ── MAIN PIPELINE NODES (y=6.0) ──
    my = 6.0
    main_nodes = [
        (1.2,  my, 'USER\nQUERY',      '+ Ground Truth',  ACC),
        (3.8,  my, 'LLaMA\n3.1-8B',    'Step 01 · Fast',  BLU),
        (7.2,  my, 'Qwen3\n32B',       'Step 02 · Smart', ACC2),
        (11.0, my, 'RAG\nChromaDB',    'Step 03 · Facts', YLW),
        (15.5, my, 'VERIFIED\nANSWER', '✓ Secure Output', GRN),
    ]
    for x,y,t,s,c in main_nodes:
        node(x,y,t,s,c)

    # ── MAIN FLOW ARROWS ──
    arrow(1.75, my, 3.25, my, BLU,  'sanitized query',      loff=(0, 0.22), lcolor=BLU)
    arrow(4.35, my, 6.65, my, ACC2, 'score < θ  →  escalate', loff=(0, 0.22), lcolor=ACC2)
    arrow(7.75, my, 10.45,my, YLW,  'score < θ  →  RAG',    loff=(0, 0.22), lcolor=YLW)
    arrow(11.55,my, 14.95,my, GRN,  'verified  →  filter',  loff=(0, 0.22), lcolor=GRN)

    # ── SCORE BRANCH NODES (y=3.8) ──
    sy = 3.8
    score_nodes = [
        (3.8,  sy, 'SCORE\nLLaMA',  '0–1 cosine', BLU),
        (7.2,  sy, 'SCORE\nQwen3',  '0–1 cosine', ACC2),
        (11.0, sy, 'SCORE\nRAG',    '0–1 cosine', YLW),
    ]
    for x,y,t,s,c in score_nodes:
        small_node(x,y,t,s,c)

    # ── DOWN ARROWS model→score ──
    for x,c in [(3.8,BLU),(7.2,ACC2),(11.0,YLW)]:
        arrow(x, my-0.55, x, sy+0.38, c, 'evaluate', loff=(0.55,0), lcolor=c)

    # ── PASS BRANCH: score≥θ → verified ──
    arrow(3.8,  sy+0.38, 15.5, my-0.55, GRN,
          '✓ score ≥ θ  →  skip cascade', rad=-0.3,
          loff=(5.2, 0.7), lcolor=GRN)
    arrow(7.2,  sy+0.38, 15.5, my-0.55, GRN,
          '✓ score ≥ θ', rad=-0.22,
          loff=(3.8, 0.55), lcolor=GRN)
    arrow(11.0, sy+0.38, 15.5, my-0.55, GRN,
          '✓ score ≥ θ', rad=-0.15,
          loff=(1.8, 0.45), lcolor=GRN)

    # ── FAIL LABELS ──
    for x,y,c,nxt in [
        (3.8,  sy, BLU,  '→ Qwen3'),
        (7.2,  sy, ACC2, '→ RAG'),
        (11.0, sy, YLW,  '→ max retries'),
    ]:
        ax.text(x+0.48, y-0.08, f'< θ\n{nxt}', ha='left', va='center',
                color=c, fontsize=6.2, fontweight='700')

    # ── CHROMADB BOX ──
    box(9.6, 0.5, 2.8, 2.0, YLW, 'ChromaDB Vector Store',
        ['817 TruthfulQA answers', 'all-MiniLM-L6-v2 embeddings',
         'cosine similarity search', 'top-k retrieval'])
    arrow(11.0, sy-0.38, 11.0, 2.5, YLW, 'retrieve top-3 facts',
          loff=(1.1,0), lcolor=YLW)

    # ── SCORER BOX ──
    box(0.3, 0.5, 4.2, 1.8, BLU, 'Scorer: sentence-transformers',
        ['model: all-MiniLM-L6-v2', 'runs locally · zero API cost',
         'encodes answer + ground truth', 'returns cosine similarity 0–1'])

    # ── GROQ API BOX ──
    box(5.0, 0.5, 3.8, 1.8, ACC2, 'Groq Inference API',
        ['LLaMA-3.1-8b-instant  (fast)', 'qwen/qwen3-32b  (smart)',
         'temperature: 0.1', 'max_tokens: 200'])

    # ── RAG FLOW LABEL ──
    ax.text(14.2, 1.8, 'RAG FLOW\nRetrieve → Augment\n→ Generate',
            ha='center', va='center', color=YLW, fontsize=7,
            fontweight='700', linespacing=1.5,
            bbox=dict(facecolor=YLW+'12', edgecolor=YLW+'55',
                      boxstyle='round,pad=0.4', lw=0.8))

    # ── THRESHOLD LEGEND ──
    ax.text(14.8, 0.85, 'θ = accuracy threshold\n(default 0.3, adjustable)',
            ha='center', va='center', color=MUT2, fontsize=6.5,
            linespacing=1.4,
            bbox=dict(facecolor='#0a0a18', edgecolor=MUT,
                      boxstyle='round,pad=0.35', lw=0.7))

    return fig


def make_score_charts(scores: dict):
    labels     = list(scores.keys())
    values     = list(scores.values())
    bar_colors = [GRN if v >= 0.3 else RED for v in values]

    fig, axes = plt.subplots(1, 2, figsize=(11, 4), facecolor=BG)

    # ── BAR CHART ──
    ax1 = axes[0]
    ax1.set_facecolor(BG)
    bars = ax1.bar(labels, values, color=bar_colors, width=0.45,
                   edgecolor='none', zorder=3)
    ax1.set_ylim(0, 1.1)
    ax1.axhline(0.3, color=MUT2, lw=1.2, ls='--', zorder=2, label='Threshold (0.3)')
    for bar, v in zip(bars, values):
        ax1.text(bar.get_x() + bar.get_width()/2, v + 0.03,
                 f'{v:.3f}', ha='center', va='bottom',
                 color='white', fontsize=10, fontweight='bold')
    ax1.set_title('Accuracy Score per Model', color='white',
                  fontsize=11, pad=12, fontweight='bold')
    ax1.tick_params(colors='white', labelsize=10)
    for sp in ax1.spines.values():
        sp.set_visible(False)
    ax1.yaxis.label.set_color('white')
    ax1.grid(axis='y', color=MUT, alpha=0.2, lw=0.8, zorder=1)
    ax1.legend(fontsize=8, framealpha=0, labelcolor='white')

    # ── DONUT GAUGE ──
    ax2 = axes[1]
    ax2.set_facecolor(BG)
    final_score = values[-1]
    final_color = GRN if final_score >= 0.3 else RED

    # Outer ring — full circle background
    ax2.pie([1], colors=['#1a1a2e'],
            wedgeprops=dict(width=0.35, edgecolor=BG, linewidth=2),
            startangle=90)
    # Inner score arc
    ax2.pie([final_score, 1-final_score],
            colors=[final_color, '#1a1a2e'],
            wedgeprops=dict(width=0.35, edgecolor=BG, linewidth=2),
            startangle=90)

    ax2.text(0,  0.08,  f'{final_score:.3f}',
             ha='center', va='center', color='white',
             fontsize=22, fontweight='bold')
    ax2.text(0, -0.18,  'accuracy score',
             ha='center', va='center', color=MUT2, fontsize=9)
    ax2.text(0,  0.52,  labels[-1],
             ha='center', va='center', color=final_color,
             fontsize=10, fontweight='bold')
    ax2.text(0, -0.62,
             '✅ ACCURATE' if final_score >= 0.3 else '❌ HALLUCINATED',
             ha='center', va='center',
             color=final_color, fontsize=9, fontweight='700')
    ax2.set_title('Final Model Accuracy', color='white',
                  fontsize=11, pad=12, fontweight='bold')

    plt.tight_layout(pad=1.2)
    return fig
