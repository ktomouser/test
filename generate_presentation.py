"""
Generate a 45-minute (20-22 slide) PowerPoint presentation on
"Stellar Dynamics in Spiral Galaxies" suitable for import into Apple Keynote.

Run:
    python generate_presentation.py

Output:
    stellar_dynamics_spiral_galaxies.pptx
"""

import io
import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, Arc
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
import pptx.oxml.ns as nsmap
from lxml import etree

# ---------------------------------------------------------------------------
# Colour palette (deep-space theme)
# ---------------------------------------------------------------------------
BG_COLOR       = RGBColor(0x05, 0x08, 0x24)   # very dark blue
TITLE_COLOR    = RGBColor(0xFF, 0xD7, 0x00)   # gold
HEADING_COLOR  = RGBColor(0x7B, 0xD3, 0xEA)   # light cyan
BODY_COLOR     = RGBColor(0xE8, 0xE8, 0xE8)   # near-white
ACCENT_COLOR   = RGBColor(0xFF, 0x6B, 0x6B)   # coral/red
EQ_COLOR       = RGBColor(0xA8, 0xFF, 0x78)   # lime green

SLIDE_W = Inches(13.33)
SLIDE_H = Inches(7.5)

# ---------------------------------------------------------------------------
# Matplotlib figure helpers
# ---------------------------------------------------------------------------

def fig_to_image_stream(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    buf.seek(0)
    plt.close(fig)
    return buf


def make_fig(figsize=(7, 4), bg="#050824"):
    fig, ax = plt.subplots(figsize=figsize, facecolor=bg)
    ax.set_facecolor(bg)
    return fig, ax


# ---------------------------------------------------------------------------
# Presentation helpers
# ---------------------------------------------------------------------------

def new_prs():
    prs = Presentation()
    prs.slide_width  = SLIDE_W
    prs.slide_height = SLIDE_H
    return prs


def blank_layout(prs):
    return prs.slide_layouts[6]   # completely blank


def set_slide_bg(slide, color: RGBColor):
    """Fill slide background with a solid colour."""
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_textbox(slide, text, left, top, width, height,
                font_size=18, bold=False, italic=False,
                color=BODY_COLOR, align=PP_ALIGN.LEFT, wrap=True):
    txb = slide.shapes.add_textbox(left, top, width, height)
    tf  = txb.text_frame
    tf.word_wrap = wrap
    p   = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size  = Pt(font_size)
    run.font.bold  = bold
    run.font.italic = italic
    run.font.color.rgb = color
    return txb


def add_title(slide, title_text, subtitle_text=None):
    """Add a golden title bar at the top of the slide."""
    add_textbox(slide, title_text,
                Inches(0.4), Inches(0.15),
                Inches(12.5), Inches(0.65),
                font_size=30, bold=True, color=TITLE_COLOR,
                align=PP_ALIGN.CENTER)
    if subtitle_text:
        add_textbox(slide, subtitle_text,
                    Inches(0.4), Inches(0.78),
                    Inches(12.5), Inches(0.4),
                    font_size=18, italic=True, color=HEADING_COLOR,
                    align=PP_ALIGN.CENTER)


def add_bullet_box(slide, items, left, top, width, height,
                   font_size=17, color=BODY_COLOR, bullet="•  "):
    txb = slide.shapes.add_textbox(left, top, width, height)
    tf  = txb.text_frame
    tf.word_wrap = True
    first = True
    for item in items:
        if first:
            p = tf.paragraphs[0]
            first = False
        else:
            p = tf.add_paragraph()
        p.space_before = Pt(4)
        run = p.add_run()
        indent = ""
        text   = item
        if item.startswith("  "):
            indent = "      "
            text   = item.lstrip()
            run.font.size = Pt(font_size - 2)
        else:
            run.font.size = Pt(font_size)
        run.text = indent + bullet + text
        run.font.color.rgb = color
    return txb


def add_equation_box(slide, equation_text, left, top, width, height,
                     font_size=19):
    txb = slide.shapes.add_textbox(left, top, width, height)
    tf  = txb.text_frame
    tf.word_wrap = True
    p   = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = equation_text
    run.font.size  = Pt(font_size)
    run.font.color.rgb = EQ_COLOR
    run.font.bold  = True
    # light box border
    sp = txb.element
    sp_pr = sp.find(nsmap.qn("p:spPr"))
    if sp_pr is None:
        sp_pr = etree.SubElement(sp, nsmap.qn("p:spPr"))
    ln = etree.SubElement(sp_pr, nsmap.qn("a:ln"), attrib={"w": "12700"})
    solid = etree.SubElement(ln, nsmap.qn("a:solidFill"))
    srgb  = etree.SubElement(solid, nsmap.qn("a:srgbClr"),
                              attrib={"val": "A8FF78"})
    return txb


def add_image_stream(slide, stream, left, top, width, height=None):
    if height:
        slide.shapes.add_picture(stream, left, top, width, height)
    else:
        slide.shapes.add_picture(stream, left, top, width)


def add_footer(slide, slide_num, total=22):
    add_textbox(slide, f"{slide_num} / {total}",
                Inches(12.2), Inches(7.1),
                Inches(0.9), Inches(0.3),
                font_size=11, color=RGBColor(0x88, 0x88, 0x88),
                align=PP_ALIGN.RIGHT)


# ===========================================================================
# Figure generators
# ===========================================================================

def fig_cosmic_web():
    """Schematic of the hierarchical structure of the Universe."""
    fig, ax = make_fig((7, 4))
    ax.set_xlim(0, 10); ax.set_ylim(0, 6)
    ax.axis("off")
    # Filaments (white curves)
    for (x0, y0, x1, y1) in [(1,1,5,4),(5,4,9,5),(1,1,3,5),(3,5,5,4),(5,4,7,1),(7,1,9,5)]:
        ax.plot([x0,x1],[y0,y1], lw=1.2, color="#AAAAAA", alpha=0.5, zorder=1)
    # Galaxy clusters
    np.random.seed(42)
    nodes = [(1,1),(3,5),(5,4),(7,1),(9,5),(2,3),(6,2.5),(4.5,2),(8,3)]
    for (x,y) in nodes:
        s = np.random.uniform(40, 200)
        ax.scatter(x, y, s=s, color="#FFD700", zorder=3, edgecolors="white", lw=0.5)
    # Labels
    labels = [("Void", 5.5, 2.2, "#7BD3EA"),
              ("Filament", 4.3, 4.7, "#7BD3EA"),
              ("Cluster", 1.0, 0.55, "#FF6B6B"),
              ("Supercluster", 5.3, 4.35, "#FF6B6B")]
    for lbl, lx, ly, lc in labels:
        ax.text(lx, ly, lbl, color=lc, fontsize=9, ha="center", va="top")
    ax.set_title("Hierarchical Structure of the Universe\n"
                 "Voids → Filaments → Groups → Clusters → Superclusters",
                 color="#E8E8E8", fontsize=10, pad=8)
    return fig_to_image_stream(fig)


def fig_galaxy_parts():
    """Cross-section sketch of a spiral galaxy."""
    fig, ax = make_fig((7, 4))
    ax.set_xlim(-5, 5); ax.set_ylim(-3, 3)
    ax.axis("off")
    # Halo (large ellipse)
    halo = mpatches.Ellipse((0,0), 9.5, 5.5, color="#1A237E", alpha=0.35, zorder=1)
    ax.add_patch(halo)
    # Disk (thin ellipse)
    disk = mpatches.Ellipse((0,0), 8.5, 1.0, color="#283593", alpha=0.6, zorder=2)
    ax.add_patch(disk)
    # Bar
    bar = mpatches.FancyBboxPatch((-1.5,-0.25), 3.0, 0.5,
                                   boxstyle="round,pad=0.05",
                                   color="#5C6BC0", zorder=3)
    ax.add_patch(bar)
    # Bulge
    bulge = mpatches.Ellipse((0,0), 1.8, 1.4, color="#FFB300", alpha=0.9, zorder=4)
    ax.add_patch(bulge)
    # Spiral arms (rough)
    theta = np.linspace(0, 3*np.pi, 300)
    r_arm = 0.9 + 0.55*theta/(3*np.pi)*3.5
    for sgn in [1, -1]:
        x_arm = sgn * r_arm * np.cos(theta + 0.3)
        y_arm =        r_arm * np.sin(theta + 0.3) * 0.18
        ax.plot(x_arm, y_arm, lw=1.8, color="#7986CB", alpha=0.85, zorder=3)
    # Annotations
    for text, x, y, dx, dy in [
            ("Bulge",   0.0,  0.0,  0.0,  1.5),
            ("Bar",     0.0, -0.5,  0.0, -1.4),
            ("Disk",    3.8,  0.2,  0.8,  0.2),
            ("Halo",   -4.2,  2.1, -0.3,  0.0),
            ("Spiral arms", 2.5,  0.8,  0.8,  0.5)]:
        ax.annotate(text, xy=(x, y), xytext=(x+dx, y+dy),
                    color="#E8E8E8", fontsize=9,
                    arrowprops=dict(arrowstyle="->", color="#7BD3EA", lw=0.8),
                    ha="center")
    ax.set_title("Main Components of a Spiral Galaxy", color="#E8E8E8", fontsize=11)
    return fig_to_image_stream(fig)


def fig_hubble_fork():
    """Hubble tuning fork diagram."""
    fig, ax = make_fig((8, 4))
    ax.set_xlim(-1, 12); ax.set_ylim(-2.5, 2.5)
    ax.axis("off")
    # Ellipticals: E0 → E7 along horizontal
    ellip_x = [0, 1.2, 2.4, 3.6]
    ellip_labels = ["E0", "E3", "E5", "E7/S0"]
    for i, (ex, el) in enumerate(zip(ellip_x, ellip_labels)):
        ratio = 0.5 + 0.5*i/3 if i < 3 else 0.3
        ell = mpatches.Ellipse((ex, 0), 0.9, 0.9*(1-0.3*i/3),
                                color="#FFD700", alpha=0.8)
        ax.add_patch(ell)
        ax.text(ex, -0.75, el, color="#E8E8E8", ha="center", fontsize=9)
    # Fork split: Sa/Sb/Sc upper, SBa/SBb/SBc lower
    ax.plot([3.6, 5.2], [0, 1.0], color="#7BD3EA", lw=2)
    ax.plot([3.6, 5.2], [0,-1.0], color="#7BD3EA", lw=2)
    spiral_x = [5.2, 7.0, 8.8, 10.6]
    for i, sx in enumerate(spiral_x):
        label_u = ["S0", "Sa", "Sb", "Sc"][i]
        label_l = ["S0", "SBa","SBb","SBc"][i]
        # Upper (unbarred)
        ax.text(sx, 1.0+0.4*i, label_u, color="#A8FF78", ha="center",
                fontsize=10, fontweight="bold")
        # Lower (barred)
        ax.text(sx,-1.0-0.4*i, label_l, color="#FF6B6B", ha="center",
                fontsize=10, fontweight="bold")
    ax.plot([5.2, 6.9, 8.7, 10.5],
            [1.0, 1.4, 1.8, 2.2], color="#A8FF78", lw=1.5, ls="--")
    ax.plot([5.2, 6.9, 8.7, 10.5],
            [-1.0,-1.4,-1.8,-2.2], color="#FF6B6B", lw=1.5, ls="--")
    ax.text(5.5, 2.3, "Unbarred spirals (S)", color="#A8FF78", fontsize=9)
    ax.text(5.5,-2.4, "Barred spirals (SB)", color="#FF6B6B", fontsize=9)
    ax.text(0.0, 1.2, "Ellipticals (E)", color="#FFD700", fontsize=9)
    ax.set_title("Hubble Classification (Tuning Fork Diagram)", color="#E8E8E8",
                 fontsize=11)
    return fig_to_image_stream(fig)


def fig_orbits_spherical():
    """Rosette orbit in a spherical potential."""
    fig, ax = make_fig((5, 5))
    ax.set_aspect("equal")
    ax.axis("off")
    # Logarithmic potential: flat rotation curve
    # Effective potential: V_eff = V_log + L^2/(2r^2)
    # Numerically integrate
    from scipy.integrate import odeint
    def drdt(state, t):
        r, vr, phi, vphi = state
        L  = r * vphi
        # V = V_0 * ln(r) => dV/dr = V0/r
        V0 = 1.0
        dr   = vr
        dvr  = L**2/r**3 - V0/r
        dphi = vphi
        dvphi= -2*vr*vphi/r
        return [dr, dvr, dphi, dvphi]
    t   = np.linspace(0, 60, 6000)
    s0  = [1.0, 0.0, 0.0, 1.15]
    sol = odeint(drdt, s0, t)
    x   = sol[:,0]*np.cos(sol[:,2])
    y   = sol[:,0]*np.sin(sol[:,2])
    ax.plot(x, y, lw=0.8, color="#7BD3EA", alpha=0.85)
    ax.scatter([0],[0], s=60, color="#FFD700", zorder=5)
    ax.set_title("Rosette orbit\nin spherical potential",
                 color="#E8E8E8", fontsize=10, pad=4)
    return fig_to_image_stream(fig)


def fig_surface_of_section():
    """Poincaré surface of section for a 2D potential (toy model)."""
    fig, ax = make_fig((5.5, 5))
    ax.set_facecolor("#050824")
    ax.tick_params(colors="#E8E8E8")
    ax.spines[['bottom','left']].set_color("#7BD3EA")
    ax.spines[['top','right']].set_visible(False)
    ax.set_xlabel("y", color="#E8E8E8", fontsize=11)
    ax.set_ylabel(r"$\dot{y}$", color="#E8E8E8", fontsize=11)
    ax.set_title("Poincaré Surface of Section  (x=0, ẋ>0)",
                 color="#E8E8E8", fontsize=10)

    # Hénon-Heiles system – classic mixed phase space
    from scipy.integrate import solve_ivp
    def hh(t, state):
        x,  y,  px, py = state
        ax_ = -(x + 2*x*y)
        ay  = -(y + x**2 - y**2)
        return [px, py, ax_, ay]

    E_list  = [0.08, 0.10, 0.13, 0.165]
    colors  = ["#A8FF78", "#7BD3EA", "#FFD700", "#FF6B6B"]
    for E, col in zip(E_list, colors):
        for y0 in np.linspace(-0.4, 0.4, 6):
            py0_sq = 2*E - y0**2 + (2/3)*y0**3
            if py0_sq < 0.01:
                continue
            py0 = math.sqrt(py0_sq)
            try:
                sol = solve_ivp(hh, [0, 400], [0, y0, 0, py0],
                                method="DOP853", rtol=1e-10, atol=1e-12,
                                dense_output=True, max_step=0.05)
                # Collect crossings: x≈0, px>0
                t_arr = sol.t
                s_arr = sol.y
                xs   = s_arr[0]
                pxs  = s_arr[2]
                ys_  = s_arr[1]
                pys_ = s_arr[3]
                pts_y, pts_py = [], []
                for k in range(1, len(t_arr)):
                    if xs[k-1] < 0 < xs[k] and pxs[k] > 0:
                        # linear interpolation
                        frac = -xs[k-1]/(xs[k]-xs[k-1])
                        pts_y.append( ys_[k-1]  + frac*(ys_[k] - ys_[k-1]))
                        pts_py.append(pys_[k-1] + frac*(pys_[k]-pys_[k-1]))
                if pts_y:
                    ax.scatter(pts_y, pts_py, s=1.5, color=col, alpha=0.7)
            except Exception:
                pass
    ax.set_xlim(-0.55, 0.55)
    ax.set_ylim(-0.55, 0.55)
    # Legend patches
    patches = [mpatches.Patch(color=c, label=f"E={e:.3f}")
               for c, e in zip(colors, E_list)]
    ax.legend(handles=patches, fontsize=8, loc="upper right",
              facecolor="#050824", labelcolor="#E8E8E8", edgecolor="#7BD3EA")
    return fig_to_image_stream(fig)


def fig_action_angle():
    """Illustration of action-angle variables on a torus."""
    fig = plt.figure(figsize=(6, 4), facecolor="#050824")
    ax  = fig.add_subplot(111, projection="3d", facecolor="#050824")
    ax.set_facecolor("#050824")
    ax.tick_params(colors="#E8E8E8")
    for pane in [ax.xaxis.pane, ax.yaxis.pane, ax.zaxis.pane]:
        pane.fill = False
        pane.set_edgecolor("#333355")

    R, r = 2.0, 0.7
    u = np.linspace(0, 2*np.pi, 80)
    v = np.linspace(0, 2*np.pi, 40)
    U, V = np.meshgrid(u, v)
    X = (R + r*np.cos(V)) * np.cos(U)
    Y = (R + r*np.cos(V)) * np.sin(U)
    Z = r * np.sin(V)
    ax.plot_surface(X, Y, Z, alpha=0.35, color="#283593", edgecolor="none")

    # θ₁ curve (around the big circle)
    v0 = 0.4
    xu = (R + r*np.cos(v0)) * np.cos(u)
    yu = (R + r*np.cos(v0)) * np.sin(u)
    zu = r * np.sin(v0) * np.ones_like(u)
    ax.plot(xu, yu, zu, color="#FFD700", lw=2, label=r"θ₁ (fast angle)")

    # θ₂ curve (around the small circle)
    u0 = 0.0
    xv = (R + r*np.cos(v)) * np.cos(u0)
    yv = (R + r*np.cos(v)) * np.sin(u0)
    zv = r * np.sin(v)
    ax.plot(xv, yv, zv, color="#FF6B6B", lw=2, label=r"θ₂ (slow angle)")

    ax.set_title("Invariant Torus in Phase Space\n"
                 "Actions J₁, J₂ = const  |  Angles θ₁, θ₂ increase uniformly",
                 color="#E8E8E8", fontsize=9, pad=6)
    ax.legend(fontsize=8, facecolor="#050824", labelcolor="#E8E8E8",
              edgecolor="#7BD3EA")
    return fig_to_image_stream(fig)


def fig_adiabatic():
    """Adiabatic invariance: slowly varying orbit."""
    fig, axes = plt.subplots(1, 2, figsize=(8, 3.5), facecolor="#050824")
    for ax in axes:
        ax.set_facecolor("#050824")
        ax.tick_params(colors="#E8E8E8")
        for sp in ax.spines.values():
            sp.set_edgecolor("#7BD3EA")

    # Left: SHO with slowly growing frequency
    t  = np.linspace(0, 60, 5000)
    om = 1.0 + 0.02*t          # slowly increasing ω(t)
    # WKB: x ∝ ω^{-1/2} cos(∫ω dt)
    phase = np.cumsum(om) * (t[1]-t[0])
    amp   = 1.0 / np.sqrt(om)
    x_adi = amp * np.cos(phase)
    axes[0].plot(t, x_adi, color="#A8FF78", lw=1)
    axes[0].plot(t,  amp,  color="#FF6B6B", lw=1.5, ls="--", label="Envelope ∝ ω⁻¹ᐟ²")
    axes[0].plot(t, -amp,  color="#FF6B6B", lw=1.5, ls="--")
    axes[0].set_xlabel("t", color="#E8E8E8"); axes[0].set_ylabel("x", color="#E8E8E8")
    axes[0].set_title("Adiabatic orbit:\nJ = E/ω = const", color="#E8E8E8", fontsize=10)
    axes[0].legend(fontsize=8, facecolor="#050824", labelcolor="#E8E8E8",
                   edgecolor="#7BD3EA")

    # Right: bar growth – schematic rotation curve
    r_arr   = np.linspace(0.1, 5, 300)
    v_circ  = 1.0*r_arr / np.sqrt(1 + r_arr**2)   # rising then flat
    v_flat  = np.ones_like(r_arr) * v_circ.max()
    axes[1].plot(r_arr, v_circ * r_arr**0, color="#7BD3EA", lw=2,
                 label="Circular speed v_c(R)")
    axes[1].axhline(v_circ.max(), color="#FFD700", lw=1, ls=":", alpha=0.5)
    axes[1].set_xlabel("R (kpc)", color="#E8E8E8")
    axes[1].set_ylabel("v_c (km/s)", color="#E8E8E8")
    axes[1].set_title("Rotation curve\n(adiabatic bar growth)", color="#E8E8E8",
                      fontsize=10)
    axes[1].legend(fontsize=8, facecolor="#050824", labelcolor="#E8E8E8",
                   edgecolor="#7BD3EA")

    fig.tight_layout(pad=1.5)
    return fig_to_image_stream(fig)


def fig_lyapunov():
    """Lyapunov exponent separation of nearby orbits."""
    fig, axes = plt.subplots(1, 2, figsize=(8, 3.5), facecolor="#050824")
    for ax in axes:
        ax.set_facecolor("#050824")
        ax.tick_params(colors="#E8E8E8")
        for sp in ax.spines.values():
            sp.set_edgecolor("#7BD3EA")

    t = np.linspace(0, 10, 400)
    # Regular orbit: separation oscillates / grows polynomially
    d_reg = 0.001 * (1 + 0.3*t)
    # Chaotic orbit: exponential separation
    lam   = 0.35
    d_cha = 0.001 * np.exp(lam * t)
    d_cha = np.minimum(d_cha, 0.8)

    axes[0].semilogy(t, d_reg,  color="#A8FF78", lw=2, label="Regular")
    axes[0].semilogy(t, d_cha,  color="#FF6B6B", lw=2, label="Chaotic")
    axes[0].set_xlabel("t", color="#E8E8E8")
    axes[0].set_ylabel("‖δw(t)‖", color="#E8E8E8")
    axes[0].set_title("Orbit separation (log scale)", color="#E8E8E8", fontsize=10)
    axes[0].legend(fontsize=9, facecolor="#050824", labelcolor="#E8E8E8",
                   edgecolor="#7BD3EA")

    # Right: SALI / frequency map idea – just a schematic scatter
    np.random.seed(7)
    n_reg, n_cha = 200, 80
    x_reg = np.random.uniform(-0.5, 0.5, n_reg)
    y_reg = np.random.uniform(-0.5, 0.5, n_reg)
    x_cha = np.random.uniform(-0.15, 0.15, n_cha) + np.random.choice([-0.4,0.4], n_cha)
    y_cha = np.random.uniform(-0.5, 0.5, n_cha)
    axes[1].scatter(x_reg, y_reg, s=5, color="#A8FF78", alpha=0.6, label="Regular")
    axes[1].scatter(x_cha, y_cha, s=5, color="#FF6B6B", alpha=0.6, label="Chaotic")
    axes[1].set_xlabel("J₁", color="#E8E8E8")
    axes[1].set_ylabel("J₂", color="#E8E8E8")
    axes[1].set_title("Frequency map (action space)", color="#E8E8E8", fontsize=10)
    axes[1].legend(fontsize=9, facecolor="#050824", labelcolor="#E8E8E8",
                   edgecolor="#7BD3EA")

    fig.tight_layout(pad=1.5)
    return fig_to_image_stream(fig)


def fig_poincare_chaos():
    """Mixed Poincaré section showing KAM tori + chaotic band."""
    fig, ax = make_fig((5.5, 5.5))
    ax.set_facecolor("#050824")
    ax.tick_params(colors="#E8E8E8")
    ax.spines[['bottom','left']].set_color("#7BD3EA")
    ax.spines[['top','right']].set_visible(False)
    ax.set_xlabel("q₁", color="#E8E8E8", fontsize=11)
    ax.set_ylabel("p₁", color="#E8E8E8", fontsize=11)
    ax.set_title("Mixed Phase Space: KAM Tori + Resonances + Chaos",
                 color="#E8E8E8", fontsize=10)

    from scipy.integrate import solve_ivp
    def hh(t, s):
        x, y, px, py = s
        return [px, py,
                -(x + 2*x*y),
                -(y + x**2 - y**2)]

    configs = [
        (0.08, np.linspace(-0.35, 0.35, 8), "#A8FF78"),
        (0.13, np.linspace(-0.45, 0.45, 7), "#7BD3EA"),
        (0.165,np.linspace(-0.50, 0.50, 10),"#FF6B6B"),
    ]
    for E, y0s, col in configs:
        for y0 in y0s:
            py0_sq = 2*E - y0**2 + (2/3)*y0**3
            if py0_sq < 0.005:
                continue
            py0 = math.sqrt(py0_sq)
            try:
                sol = solve_ivp(hh, [0, 600], [0, y0, 0, py0],
                                method="DOP853", rtol=1e-9, atol=1e-11,
                                max_step=0.05)
                xs   = sol.y[0]; pxs = sol.y[2]
                ys_  = sol.y[1]; pys_= sol.y[3]
                pts_y, pts_py = [], []
                for k in range(1, len(sol.t)):
                    if xs[k-1] < 0 <= xs[k] and pxs[k] > 0:
                        frac = -xs[k-1]/(xs[k]-xs[k-1])
                        pts_y.append( ys_[k-1]  + frac*(ys_[k]- ys_[k-1]))
                        pts_py.append(pys_[k-1] + frac*(pys_[k]-pys_[k-1]))
                if pts_y:
                    ax.scatter(pts_y, pts_py, s=1.2, color=col, alpha=0.75)
            except Exception:
                pass

    ax.set_xlim(-0.6, 0.6); ax.set_ylim(-0.6, 0.6)
    patches = [
        mpatches.Patch(color="#A8FF78", label="KAM tori  (low E)"),
        mpatches.Patch(color="#7BD3EA", label="Island chains"),
        mpatches.Patch(color="#FF6B6B", label="Chaotic band (high E)"),
    ]
    ax.legend(handles=patches, fontsize=8, loc="upper right",
              facecolor="#050824", labelcolor="#E8E8E8", edgecolor="#7BD3EA")
    return fig_to_image_stream(fig)


def fig_resonance_web():
    """Resonance web: schematic in frequency ratio space."""
    fig, ax = make_fig((5, 4))
    ax.set_facecolor("#050824")
    ax.set_xlabel("Ω₁/Ωₚ", color="#E8E8E8")
    ax.set_ylabel("Ω₂/Ωₚ", color="#E8E8E8")
    ax.set_title("Resonance Web in Frequency Space", color="#E8E8E8", fontsize=10)
    ax.tick_params(colors="#E8E8E8")
    ax.set_xlim(0, 3); ax.set_ylim(0, 3)
    for sp in ax.spines.values():
        sp.set_edgecolor("#7BD3EA")

    fracs = [(1,1),(1,2),(2,1),(1,3),(3,1),(2,3),(3,2)]
    xx = np.linspace(0, 3, 200)
    for (m, n) in fracs:
        # m*Ω₁ - n*Ω₂ = 0  =>  Ω₂ = (m/n)*Ω₁
        yy = (m/n) * xx
        mask = (yy >= 0) & (yy <= 3)
        ax.plot(xx[mask], yy[mask], lw=1.0, color="#7BD3EA", alpha=0.5)
        # Label near center
        x_mid = 1.5
        y_mid = (m/n)*1.5
        if 0.1 < y_mid < 2.9:
            ax.text(x_mid+0.05, y_mid+0.05,
                    f"{m}:{n}", color="#FFD700", fontsize=7)
    # Scatter some orbit points
    np.random.seed(3)
    for (m, n) in fracs:
        for _ in range(20):
            xpt = np.random.uniform(0.2, 2.8)
            ypt = (m/n)*xpt + np.random.normal(0, 0.03)
            if 0 < ypt < 3:
                ax.scatter(xpt, ypt, s=4, color="#FF6B6B", alpha=0.6)
    return fig_to_image_stream(fig)


# ===========================================================================
# Build slides
# ===========================================================================

def build_presentation():
    prs = new_prs()

    # -----------------------------------------------------------------------
    # SLIDE 1 – Title slide
    # -----------------------------------------------------------------------
    slide = prs.slides.add_slide(blank_layout(prs))
    set_slide_bg(slide, BG_COLOR)

    # Central title
    add_textbox(slide, "Stellar Dynamics in Spiral Galaxies",
                Inches(0.5), Inches(2.0),
                Inches(12.3), Inches(1.3),
                font_size=40, bold=True, color=TITLE_COLOR,
                align=PP_ALIGN.CENTER)
    add_textbox(slide, "Orbits · Phase Space · Chaos · Secular Evolution",
                Inches(0.5), Inches(3.4),
                Inches(12.3), Inches(0.55),
                font_size=22, italic=True, color=HEADING_COLOR,
                align=PP_ALIGN.CENTER)
    add_textbox(slide, "45-minute lecture  |  22 slides",
                Inches(0.5), Inches(4.1),
                Inches(12.3), Inches(0.4),
                font_size=16, color=BODY_COLOR,
                align=PP_ALIGN.CENTER)
    add_textbox(slide, "Based on Binney & Tremaine, Galactic Dynamics (2nd ed.)",
                Inches(0.5), Inches(6.7),
                Inches(12.3), Inches(0.3),
                font_size=12, italic=True,
                color=RGBColor(0x88, 0x88, 0x88),
                align=PP_ALIGN.CENTER)
    add_footer(slide, 1)

    # -----------------------------------------------------------------------
    # SLIDE 2 – Outline
    # -----------------------------------------------------------------------
    slide = prs.slides.add_slide(blank_layout(prs))
    set_slide_bg(slide, BG_COLOR)
    add_title(slide, "Outline")
    topics = [
        "1.  Hierarchical structure of the Universe",
        "2.  What is a galaxy?  Main components",
        "3.  Galaxy classification – the Hubble fork",
        "4.  Orbits in spherical & axisymmetric potentials",
        "5.  Phase space – surfaces of section",
        "6.  Orbits in non-axisymmetric potentials",
        "7.  Action–angle variables and orbital tori",
        "8.  Adiabatic invariance of actions",
        "9.  Hamiltonian perturbation theory & KAM theorem",
        "10. Poincaré sections – mixed phase space",
        "11. Lyapunov exponents & frequency analysis",
        "12. Summary and outlook",
    ]
    add_bullet_box(slide, topics,
                   Inches(0.5), Inches(1.3),
                   Inches(12.0), Inches(5.8),
                   font_size=16, bullet="")
    add_footer(slide, 2)

    # -----------------------------------------------------------------------
    # SLIDE 3 – Hierarchical structure
    # -----------------------------------------------------------------------
    slide = prs.slides.add_slide(blank_layout(prs))
    set_slide_bg(slide, BG_COLOR)
    add_title(slide, "Hierarchical Structure of the Universe",
              "From quantum fluctuations to the cosmic web")

    img = fig_cosmic_web()
    add_image_stream(slide, img,
                     Inches(0.3), Inches(1.25), Inches(7.5))

    scales = [
        "Planets / Stars:  10⁻³ – 10³ AU",
        "Star clusters:    1 – 100 pc",
        "Galaxies:         1 – 100 kpc",
        "Galaxy groups:    1 – 3 Mpc",
        "Galaxy clusters:  1 – 10 Mpc",
        "Superclusters / Filaments:  10 – 100 Mpc",
        "Observable Universe:  ~ 28 Gpc",
        "",
        "Dark matter drives structure growth",
        "  ΛCDM: P(k) ∝ kⁿ·T²(k),  n ≈ 0.96",
    ]
    add_bullet_box(slide, scales,
                   Inches(8.0), Inches(1.25),
                   Inches(5.0), Inches(5.8),
                   font_size=14)
    add_footer(slide, 3)

    # -----------------------------------------------------------------------
    # SLIDE 4 – What is a galaxy? Components
    # -----------------------------------------------------------------------
    slide = prs.slides.add_slide(blank_layout(prs))
    set_slide_bg(slide, BG_COLOR)
    add_title(slide, "What is a Galaxy?  Main Components",
              "Bulge · Disk · Bar · Spiral Arms · Halo")

    img = fig_galaxy_parts()
    add_image_stream(slide, img,
                     Inches(0.3), Inches(1.2), Inches(7.2))

    facts = [
        "Disk: M_disk ~ 5×10¹⁰ M☉",
        "  Exponential profile: Σ(R) = Σ₀ exp(-R/h_R)",
        "  h_R ≈ 2–4 kpc (Milky Way: h_R ≈ 2.6 kpc)",
        "",
        "Bulge: r_eff ~ 1–2 kpc, Sérsic n≈4",
        "",
        "Bar: ℓ_bar ~ 3–5 kpc, pattern speed Ωₚ ~ 30–60 km/s/kpc",
        "",
        "DM Halo: M_halo ~ 10¹² M☉, r_vir ~ 200 kpc",
        "  NFW profile: ρ(r) = ρ_s / [(r/r_s)(1+r/r_s)²]",
        "",
        "Total luminosity: L ~ 10⁹ – 10¹¹ L☉",
        "Typical T_eff (stars): 3,000 – 50,000 K",
    ]
    add_bullet_box(slide, facts,
                   Inches(7.7), Inches(1.2),
                   Inches(5.3), Inches(5.9),
                   font_size=13)
    add_footer(slide, 4)

    # -----------------------------------------------------------------------
    # SLIDE 5 – Hubble fork
    # -----------------------------------------------------------------------
    slide = prs.slides.add_slide(blank_layout(prs))
    set_slide_bg(slide, BG_COLOR)
    add_title(slide, "Galaxy Classification: The Hubble Tuning Fork",
              "Morphological sequence from ellipticals to late spirals")

    img = fig_hubble_fork()
    add_image_stream(slide, img,
                     Inches(0.3), Inches(1.2), Inches(8.5))

    info = [
        "Ellipticals (E0–E7):",
        "  Spheroidal, old red stars, little gas",
        "  M_* up to ~ 10¹³ M☉  (cD giants)",
        "",
        "Lenticulars (S0):",
        "  Disk without spiral arms",
        "",
        "Spirals (Sa→Sc  /  SBa→SBc):",
        "  Increasing arm openness, gas fraction,",
        "  and star formation rate along sequence",
        "",
        "Irregulars (Irr): disturbed, star-forming",
        "",
        "★ de Vaucouleurs (1959) extended to RC3",
    ]
    add_bullet_box(slide, info,
                   Inches(9.0), Inches(1.2),
                   Inches(4.1), Inches(5.9),
                   font_size=12)
    add_footer(slide, 5)

    # -----------------------------------------------------------------------
    # SLIDE 6 – Orbits in spherical potentials
    # -----------------------------------------------------------------------
    slide = prs.slides.add_slide(blank_layout(prs))
    set_slide_bg(slide, BG_COLOR)
    add_title(slide, "Orbits in Static Spherical Potentials",
              "Conservation of energy E and angular momentum L")

    img = fig_orbits_spherical()
    add_image_stream(slide, img,
                     Inches(0.3), Inches(1.25), Inches(5.2))

    add_equation_box(slide,
        "Effective potential:  Φ_eff(r) = Φ(r) + L²/(2r²)\n\n"
        "Radial equation:   r̈ = −dΦ_eff/dr\n\n"
        "Apsidal angle:  Δφ = π  ⟹  closed orbit\n"
        "               Δφ ≠ π  ⟹  rosette orbit",
        Inches(5.7), Inches(1.25),
        Inches(7.3), Inches(2.5))

    pts = [
        "Isochrone potential: all bound orbits are closed",
        "Logarithmic: V_c = const  →  flat rotation curve",
        "  Φ(r) = V_c² ln(r)  +  const",
        "Hernquist/NFW: closed only for circular & radial",
        "",
        "Two integrals of motion: E, Lz  (3rd may exist)",
        "Orbit families: loop, box (radial), tube",
    ]
    add_bullet_box(slide, pts,
                   Inches(5.7), Inches(3.9),
                   Inches(7.3), Inches(3.3),
                   font_size=14)
    add_footer(slide, 6)

    # -----------------------------------------------------------------------
    # SLIDE 7 – Axisymmetric potentials & third integral
    # -----------------------------------------------------------------------
    slide = prs.slides.add_slide(blank_layout(prs))
    set_slide_bg(slide, BG_COLOR)
    add_title(slide, "Orbits in Axisymmetric Potentials",
              "Meridional plane, third integral, epicycle theory")

    add_equation_box(slide,
        "Φ(R,z)  ⟹  Integrals: E,  Lz,  (I₃ approximate)\n\n"
        "Meridional plane:  R̈ = −∂Φ_eff/∂R,   z̈ = −∂Φ/∂z\n"
        "  Φ_eff(R,z) = Φ(R,z) + Lz²/(2R²)\n\n"
        "Epicycle approximation  (R ≈ R_g + x,  |x|≪R_g):\n"
        "  ẍ = −κ²x,   z̈ = −ν²z\n"
        "  κ² = R dΩ²/dR + 4Ω²  (epicycle freq.)\n"
        "  ν² = ∂²Φ/∂z²|_z=0   (vertical freq.)\n"
        "  For flat rotation curve:  κ = √2 Ω",
        Inches(0.4), Inches(1.25),
        Inches(7.5), Inches(4.0))

    pts = [
        "Lindblad resonances:",
        "  ILR: Ω − κ/m = Ωₚ",
        "  OLR: Ω + κ/m = Ωₚ",
        "  CR:  Ω = Ωₚ  (corotation)",
        "",
        "Stars near corotation trapped",
        "in horseshoe orbits",
        "",
        "3rd integral I₃ ≈ action Jz",
        "(Stäckel potentials exact)",
        "",
        "► Oort constants A, B",
        "  A = −½(dv_c/dR)R",
        "  B = −Ω − A",
    ]
    add_bullet_box(slide, pts,
                   Inches(8.1), Inches(1.25),
                   Inches(5.0), Inches(5.5),
                   font_size=14)

    add_textbox(slide, "⚡ Animation: orbit in (R,z) meridional plane",
                Inches(0.4), Inches(5.5),
                Inches(7.5), Inches(0.4),
                font_size=12, italic=True, color=ACCENT_COLOR)
    add_footer(slide, 7)

    # -----------------------------------------------------------------------
    # SLIDE 8 – Poincaré surfaces of section
    # -----------------------------------------------------------------------
    slide = prs.slides.add_slide(blank_layout(prs))
    set_slide_bg(slide, BG_COLOR)
    add_title(slide, "Phase Space and Surfaces of Section",
              "Reducing dimensionality by 2 — Poincaré map")

    img = fig_surface_of_section()
    add_image_stream(slide, img,
                     Inches(0.3), Inches(1.2), Inches(6.2))

    pts = [
        "2-DOF Hamiltonian: 4D phase space",
        "Energy surface:  3D",
        "Poincaré section (x=0, ṗₓ>0): 2D map",
        "",
        "Regular orbits → closed curves (KAM tori)",
        "Resonant orbits → finite point sets",
        "Chaotic orbits → scattered points",
        "",
        "Example: Hénon–Heiles potential",
        "  H = ½(px²+py²) + ½(x²+y²)",
        "        + x²y − ⅓y³",
        "",
        "At low E: mostly regular",
        "At E → E_escape: mostly chaotic",
        "",
        "★ Key diagnostic for galactic dynamics",
    ]
    add_bullet_box(slide, pts,
                   Inches(6.7), Inches(1.2),
                   Inches(6.4), Inches(5.9),
                   font_size=13)
    add_footer(slide, 8)

    # -----------------------------------------------------------------------
    # SLIDE 9 – Non-axisymmetric potentials
    # -----------------------------------------------------------------------
    slide = prs.slides.add_slide(blank_layout(prs))
    set_slide_bg(slide, BG_COLOR)
    add_title(slide, "Orbits in Non-Axisymmetric Potentials",
              "Bars, triaxial ellipsoids, spiral perturbations")

    add_equation_box(slide,
        "Rotating frame (pattern speed Ωₚ):\n"
        "  H = ½|v|² + Φ(x,y) − Ωₚ Lz  =  EJ  (Jacobi integral)\n\n"
        "Barred potential (bisymmetric):\n"
        "  Φ_bar(R,φ) = Φ_0(R) + Φ_2(R) cos(2φ)\n\n"
        "Orbit families in a bar:\n"
        "  x₁ – backbone, elongated along bar (stable)\n"
        "  x₂, x₃ – perpendicular to bar\n"
        "  x₄ – retrograde\n\n"
        "Spiral arms: transient density waves\n"
        "  Lin–Shu dispersion relation:\n"
        "  (ω−mΩ)² = κ² − 2πGΣ|k|",
        Inches(0.4), Inches(1.25),
        Inches(7.5), Inches(5.5))

    pts2 = [
        "Corotation radius R_CR:",
        "  Ω(R_CR) = Ωₚ",
        "",
        "Bar resonances drive",
        "  secular angular momentum",
        "  exchange with halo",
        "",
        "Manifold theory:",
        "  unstable manifolds of L₁, L₂",
        "  trace spiral arms",
        "",
        "⚡ Animation: x₁ family in",
        "   rotating bar potential",
    ]
    add_bullet_box(slide, pts2,
                   Inches(8.1), Inches(1.25),
                   Inches(5.0), Inches(5.5),
                   font_size=14)
    add_footer(slide, 9)

    # -----------------------------------------------------------------------
    # SLIDE 10 – Action–angle variables
    # -----------------------------------------------------------------------
    slide = prs.slides.add_slide(blank_layout(prs))
    set_slide_bg(slide, BG_COLOR)
    add_title(slide, "Action–Angle Variables & Orbital Tori",
              "The natural coordinates for integrable systems")

    img = fig_action_angle()
    add_image_stream(slide, img,
                     Inches(0.3), Inches(1.2), Inches(6.5))

    add_equation_box(slide,
        "Actions  (adiabatic invariants):\n"
        "  Jᵢ = (1/2π) ∮ pᵢ dqᵢ\n\n"
        "Angles  (conjugate variables):\n"
        "  θ̇ᵢ = ∂H/∂Jᵢ = Ωᵢ(J) = const\n\n"
        "  θᵢ(t) = θᵢ(0) + Ωᵢ t\n\n"
        "Torus  T²  =  {(θ₁,θ₂) ∈ [0,2π)²}\n\n"
        "For axisymmetric disk:\n"
        "  J = (Jr, Lz, Jz)\n"
        "  Ω = (κ, Ω_φ, ν)",
        Inches(7.0), Inches(1.2),
        Inches(6.1), Inches(4.2))

    pts3 = [
        "Torus construction (McGill & Binney 1990)",
        "Stäckel fudge (Binney 2012)",
        "  fast approximation for disk potentials",
        "",
        "Actions are constants of motion",
        "  → label orbit families",
        "  → natural basis for DFs",
        "  f = f(Jr, Lz, Jz)",
    ]
    add_bullet_box(slide, pts3,
                   Inches(7.0), Inches(5.5),
                   Inches(6.1), Inches(1.8),
                   font_size=13)
    add_footer(slide, 10)

    # -----------------------------------------------------------------------
    # SLIDE 11 – Adiabatic invariance
    # -----------------------------------------------------------------------
    slide = prs.slides.add_slide(blank_layout(prs))
    set_slide_bg(slide, BG_COLOR)
    add_title(slide, "Slowly Varying Potentials & Adiabatic Invariance",
              "Actions frozen when Φ changes on timescale τ ≫ T_orbit")

    img = fig_adiabatic()
    add_image_stream(slide, img,
                     Inches(0.3), Inches(4.3), Inches(9.5))

    add_equation_box(slide,
        "Adiabatic invariant:  J = ∮ p dq / (2π)  = const\n\n"
        "Simple harmonic:  J = E / ω  →  E ∝ ω  as ω changes slowly\n\n"
        "Action change:  ΔJ / J  ~  exp(−ωτ)  ≪  1  (exponentially small)",
        Inches(0.4), Inches(1.2),
        Inches(12.5), Inches(1.8))

    apps = [
        "Eccentric orbits in a growing disk:",
        "  Jz adiabatically frozen as disk mass increases",
        "  → 'heating' by non-adiabatic perturbations required",
        "",
        "Transient spiral perturbation:",
        "  If τ_spiral ≫ T_orbit: actions conserved → no net heating",
        "  If τ_spiral ~ T_orbit: stochastic heating (resonance)",
        "",
        "Slow growth of a central black hole:",
        "  MBH grows on Gyr timescale → Jr, Jz adiabatically conserved",
        "  Orbits shrink: Ω_r, Ω_z ↑  while J = const",
    ]
    add_bullet_box(slide, apps,
                   Inches(0.4), Inches(3.1),
                   Inches(12.5), Inches(1.0),
                   font_size=13)
    add_footer(slide, 11)

    # -----------------------------------------------------------------------
    # SLIDE 12 – Hamiltonian perturbation theory
    # -----------------------------------------------------------------------
    slide = prs.slides.add_slide(blank_layout(prs))
    set_slide_bg(slide, BG_COLOR)
    add_title(slide, "Hamiltonian Perturbation Theory",
              "Canonical perturbation theory in action–angle coordinates")

    add_equation_box(slide,
        "H(θ,J) = H₀(J) + εH₁(θ,J)\n\n"
        "Generating function  S(θ,J') = θ·J' + εS₁(θ,J') + …\n\n"
        "New Hamiltonian:\n"
        "  H'(J') = H₀(J') + ε⟨H₁⟩ + O(ε²)\n\n"
        "Resonance condition:  n·Ω(J) = 0   (small divisor problem)\n\n"
        "Secular terms: ΔJ ∝ ε  at resonance  →  libration islands",
        Inches(0.4), Inches(1.25),
        Inches(7.5), Inches(4.0))

    pts4 = [
        "Spiral arm perturbation:",
        "  H₁ = −Φ_s(R) cos(mφ − ωt)",
        "  Corotation resonance: most important",
        "  ILR, OLR: wave reflection/transmission",
        "",
        "Bar perturbation (steady, m=2):",
        "  n·Ω = 0  ↔  ℓκ + mΩφ = mΩₚ",
        "  Resonances drive secular evolution",
        "",
        "Perturbation theory breaks down:",
        "  when ε is not small, OR",
        "  when resonances overlap (Chirikov)",
        "",
        "→ KAM theorem gives conditions",
        "   for persistence of tori",
    ]
    add_bullet_box(slide, pts4,
                   Inches(8.1), Inches(1.25),
                   Inches(5.0), Inches(5.7),
                   font_size=13)
    add_footer(slide, 12)

    # -----------------------------------------------------------------------
    # SLIDE 13 – KAM theorem
    # -----------------------------------------------------------------------
    slide = prs.slides.add_slide(blank_layout(prs))
    set_slide_bg(slide, BG_COLOR)
    add_title(slide, "KAM Theory",
              "Kolmogorov–Arnold–Moser: survival of invariant tori")

    add_equation_box(slide,
        "KAM theorem (1954–1963):\n\n"
        "  If H = H₀(J) + εH₁(θ,J),  H₀ non-degenerate,\n"
        "  and the frequency vector Ω(J) satisfies\n\n"
        "      |n · Ω(J)| > γ / |n|^τ   for all n ∈ ℤ^N\\{0}\n\n"
        "  (Diophantine condition, γ>0, τ>N−1)\n\n"
        "  then for ε < ε_crit(γ,τ), the invariant torus survives.",
        Inches(0.4), Inches(1.25),
        Inches(12.5), Inches(3.3))

    consequences = [
        "Most (positive-measure) tori survive small perturbations",
        "Resonant tori (n·Ω = 0) are destroyed → replaced by island chains + thin chaotic layers (Birkhoff–Poincaré)",
        "As ε increases, more tori break: Aubry–Mather theory (cantori)",
        "Last KAM torus at ε = ε_crit separates inner regular from outer chaotic region",
        "Nekhoroshev theorem: action diffusion exponentially slow for non-resonant orbits",
        "Galactic application: disk stars mostly on KAM tori; bar pushes orbits toward chaos",
    ]
    add_bullet_box(slide, consequences,
                   Inches(0.4), Inches(4.7),
                   Inches(12.5), Inches(2.6),
                   font_size=14)
    add_footer(slide, 13)

    # -----------------------------------------------------------------------
    # SLIDE 14 – Poincaré sections: mixed phase space
    # -----------------------------------------------------------------------
    slide = prs.slides.add_slide(blank_layout(prs))
    set_slide_bg(slide, BG_COLOR)
    add_title(slide, "Poincaré Sections: Mixed Phase Space",
              "KAM tori · Resonance islands · Chaotic layers")

    img = fig_poincare_chaos()
    add_image_stream(slide, img,
                     Inches(0.3), Inches(1.2), Inches(6.0))

    pts5 = [
        "As energy E → E_escape:",
        "  Regular ↔ Resonance island chains ↔ Chaotic sea",
        "",
        "Island chains (Birkhoff chains):",
        "  p:q resonance  →  p stable + p unstable fixed pts",
        "  Each stable pt surrounded by sub-islands (self-similar)",
        "",
        "Chaotic bands:",
        "  Thin near separatrices of resonances",
        "  Merge at high E → large chaotic sea",
        "",
        "Arnold diffusion (N≥3 DOF):",
        "  Slow drift along resonance web",
        "  Timescale ~ exp(1/ε)",
        "",
        "Galaxy implications:",
        "  Chaotic orbits → box-orbit heating",
        "  → affect bar slow-down, disk thickening",
    ]
    add_bullet_box(slide, pts5,
                   Inches(6.5), Inches(1.2),
                   Inches(6.6), Inches(5.9),
                   font_size=13)
    add_footer(slide, 14)

    # -----------------------------------------------------------------------
    # SLIDE 15 – Chaotic bands and invariant tori in galaxies
    # -----------------------------------------------------------------------
    slide = prs.slides.add_slide(blank_layout(prs))
    set_slide_bg(slide, BG_COLOR)
    add_title(slide, "Chaotic Orbits in Barred Galaxies",
              "Sticky orbits, stochastic heating, and secular evolution")

    add_equation_box(slide,
        "Jacobi energy:  EJ = ½v² + Φ_eff − ΩₚLz = const (rotating frame)\n\n"
        "Zero-velocity curve:  EJ = Φ_eff(R,φ)\n"
        "Lagrange points L₁, L₂, L₃, L₄, L₅\n\n"
        "Orbits with EJ > Φ(L₁,₂) can escape bar region\n"
        "→ 'Sticky' chaotic orbits linger near remnants of KAM tori",
        Inches(0.4), Inches(1.25),
        Inches(12.5), Inches(2.5))

    pts6 = [
        "Sticky orbits: chaotic but quasi-regular for ~ Gyr",
        "  Mimic regular x₁ family → populate bar",
        "",
        "Bar slow-down via halo resonance:",
        "  Trapped orbits exchange angular momentum",
        "  dL/dt ∝ ∂f/∂E at resonance (Tremaine–Weinberg)",
        "",
        "SALI / GALI indicators (Skokos 2001, 2007):",
        "  Quickly distinguish regular from chaotic",
        "  SALI → 0 exponentially for chaotic orbits",
        "  SALI → const > 0 for regular orbits",
        "",
        "N-body simulations confirm ~20% chaotic orbits in bar",
    ]
    add_bullet_box(slide, pts6,
                   Inches(0.4), Inches(3.9),
                   Inches(12.5), Inches(3.3),
                   font_size=14)
    add_footer(slide, 15)

    # -----------------------------------------------------------------------
    # SLIDE 16 – Lyapunov exponents
    # -----------------------------------------------------------------------
    slide = prs.slides.add_slide(blank_layout(prs))
    set_slide_bg(slide, BG_COLOR)
    add_title(slide, "Lyapunov Exponents",
              "Quantifying sensitivity to initial conditions")

    img = fig_lyapunov()
    add_image_stream(slide, img,
                     Inches(0.3), Inches(4.3), Inches(9.5))

    add_equation_box(slide,
        "Maximal Lyapunov exponent (MLE):\n"
        "  λ₁ = lim_{t→∞}  (1/t) ln ‖δw(t)‖ / ‖δw(0)‖\n\n"
        "  Regular orbit:   λ₁ = 0  (power-law divergence)\n"
        "  Chaotic orbit:   λ₁ > 0  (exponential divergence)\n\n"
        "Full spectrum:  λ₁ ≥ λ₂ ≥ … ≥ λ_{2N}\n"
        "  Σ λᵢ = 0  (Hamiltonian, Liouville)",
        Inches(0.4), Inches(1.25),
        Inches(12.5), Inches(2.8))

    pts7 = [
        "Numerical methods: tangent map integration alongside orbit",
        "Typical values: λ₁ ~ 0.1–1 Gyr⁻¹ for chaotic galactic orbits",
        "Lyapunov time: t_L = 1/λ₁ ~ 1–10 Gyr  (comparable to Hubble time!)",
    ]
    add_bullet_box(slide, pts7,
                   Inches(0.4), Inches(3.55),
                   Inches(12.5), Inches(0.65),
                   font_size=14)
    add_footer(slide, 16)

    # -----------------------------------------------------------------------
    # SLIDE 17 – Frequency analysis
    # -----------------------------------------------------------------------
    slide = prs.slides.add_slide(blank_layout(prs))
    set_slide_bg(slide, BG_COLOR)
    add_title(slide, "Frequency Analysis Methods",
              "Laskar's NAFF, frequency maps, and the web of resonances")

    img = fig_resonance_web()
    add_image_stream(slide, img,
                     Inches(0.3), Inches(1.2), Inches(6.0))

    add_equation_box(slide,
        "NAFF – Numerical Analysis of Fundamental Frequencies\n"
        "(Laskar 1990, 1993):\n\n"
        "  From time series x(t), find dominant frequency ω₁ s.t.\n"
        "  ∫₀ᵀ x(t) e^{−iω₁t} χ(t) dt  is maximised\n\n"
        "  Repeat on residual to get ω₂, ω₃, …\n\n"
        "Diffusion rate:  σ = |Ω(t₁) − Ω(t₂)| / T  → 0 for regular",
        Inches(6.5), Inches(1.2),
        Inches(6.6), Inches(3.5))

    pts8 = [
        "Frequency map: plot (Ω₁/Ωₚ, Ω₂/Ωₚ) for ensemble",
        "Regular orbits → sharp curves",
        "Chaotic orbits → diffuse scatter",
        "",
        "Identifies resonances as dense lines",
        "  n₁Ω₁ + n₂Ω₂ + n₃Ωₚ = 0",
        "",
        "Applied to: triaxial ellipticals (Valluri),",
        "  barred disk galaxies (Quillen, Minchev)",
        "  N-body simulations (Voglis, Contopoulos)",
    ]
    add_bullet_box(slide, pts8,
                   Inches(6.5), Inches(4.8),
                   Inches(6.6), Inches(2.5),
                   font_size=13)
    add_footer(slide, 17)

    # -----------------------------------------------------------------------
    # SLIDE 18 – Self-consistent models & distribution functions
    # -----------------------------------------------------------------------
    slide = prs.slides.add_slide(blank_layout(prs))
    set_slide_bg(slide, BG_COLOR)
    add_title(slide, "Self-Consistent Models & Distribution Functions",
              "Closing the loop: orbits ↔ potential ↔ density")

    add_equation_box(slide,
        "Collisionless Boltzmann equation (CBE):\n"
        "  ∂f/∂t + v·∇f − ∇Φ·∂f/∂v = 0\n\n"
        "Jeans theorem: any function of integrals of motion solves CBE\n"
        "  f = f(E, Lz, I₃)  for axisymmetric system\n\n"
        "Self-consistency: ρ(x) = ∫ f dv³  →  ∇²Φ = 4πGρ\n\n"
        "Action-based DFs:  f = f(Jr, Lz, Jz)  (Binney & McMillan 2011)",
        Inches(0.4), Inches(1.25),
        Inches(12.5), Inches(3.0))

    pts9 = [
        "Dehnen–Binney (1998): f(E, Lz) for disk + bulge + halo",
        "Posti et al. (2015): action DF for NFW halo",
        "Bovy et al. (2013): mono-abundance populations → disk DFs",
        "",
        "Jeans equations: ∂(ρ⟨vᵢvⱼ⟩)/∂xⱼ = −ρ ∂Φ/∂xᵢ",
        "  Used in mass modelling (Gaia + spectroscopy)",
        "",
        "★ Observable: proper motions (Gaia DR3), RVS radial velocities",
        "  → test action-based DFs directly",
    ]
    add_bullet_box(slide, pts9,
                   Inches(0.4), Inches(4.4),
                   Inches(12.5), Inches(2.8),
                   font_size=14)
    add_footer(slide, 18)

    # -----------------------------------------------------------------------
    # SLIDE 19 – Observational diagnostics
    # -----------------------------------------------------------------------
    slide = prs.slides.add_slide(blank_layout(prs))
    set_slide_bg(slide, BG_COLOR)
    add_title(slide, "Observational Diagnostics",
              "Connecting theory to data: Gaia, APOGEE, IFU surveys")

    bullet_l = [
        "Gaia DR3 (2022):",
        "  1.5 × 10⁹ stars with 5-6D phase space",
        "  Reveals: moving groups, phase spirals,",
        "  bar resonances in velocity space",
        "",
        "APOGEE / GALAH surveys:",
        "  Chemical abundances → chemodynamical DF",
        "",
        "IFU spectroscopy (MaNGA, SAMI, MUSE):",
        "  Velocity fields of external galaxies",
        "  Bar pattern speeds via Tremaine–Weinberg method:",
        "    Ωₚ sin i = ∫ Σ V dx / ∫ Σ x dx",
    ]
    add_bullet_box(slide, bullet_l,
                   Inches(0.4), Inches(1.25),
                   Inches(6.2), Inches(5.9),
                   font_size=14)

    bullet_r = [
        "N-body + SPH simulations:",
        "  GADGET-4, AREPO, AGORA",
        "  Track orbit families over Gyr",
        "",
        "Frequency analysis of N-body:",
        "  Identify resonance trapping",
        "  Bar slow-down rate",
        "",
        "Chaos fraction vs galaxy type:",
        "  Strongly barred → more chaos",
        "  Merger remnants → triaxial, chaotic",
        "",
        "★ Phase spiral (Antoja 2018):",
        "  Incomplete phase-mixing → GMC/Sgr?",
    ]
    add_bullet_box(slide, bullet_r,
                   Inches(6.8), Inches(1.25),
                   Inches(6.3), Inches(5.9),
                   font_size=14)
    add_footer(slide, 19)

    # -----------------------------------------------------------------------
    # SLIDE 20 – Open questions & frontiers
    # -----------------------------------------------------------------------
    slide = prs.slides.add_slide(blank_layout(prs))
    set_slide_bg(slide, BG_COLOR)
    add_title(slide, "Open Questions & Current Frontiers",
              "Where stellar dynamics meets cosmology")

    questions = [
        "1.  Origin of the Milky Way's long bar and its current pattern speed (~ 39 km/s/kpc)",
        "2.  Role of chaotic orbits in bar slow-down: N-body vs. secular theory",
        "3.  Dark matter substructure: granular potential fluctuations → heating & diffusion",
        "4.  Phase-space spirals (Gaia): quantifying timescale of perturbation",
        "5.  Action diffusion across resonances: Fokker–Planck approach",
        "6.  Torus construction beyond integrable backgrounds (angle maps in N-body)",
        "7.  Machine-learning orbit classification (Neural network surrogates for NAFF)",
        "8.  Connecting stellar dynamics to chemical evolution (chemodynamical torus models)",
        "9.  Stellar streams as dynamical tracers of the DM halo shape",
        "10. Relativistic corrections near the central black hole: post-Newtonian dynamics",
    ]
    add_bullet_box(slide, questions,
                   Inches(0.4), Inches(1.25),
                   Inches(12.5), Inches(5.7),
                   font_size=15, bullet="❯  ")
    add_footer(slide, 20)

    # -----------------------------------------------------------------------
    # SLIDE 21 – Summary
    # -----------------------------------------------------------------------
    slide = prs.slides.add_slide(blank_layout(prs))
    set_slide_bg(slide, BG_COLOR)
    add_title(slide, "Summary",
              "Key take-home messages")

    summary = [
        "Galaxies are hierarchical structures: bulge, disk, bar, halo each with distinct dynamics",
        "Orbits in integrable potentials are confined to invariant tori characterised by actions J",
        "Action–angle variables are the natural language for Hamiltonian dynamics in galaxies",
        "Adiabatic invariance: slowly-evolving potentials preserve actions → secular evolution",
        "KAM theorem: most invariant tori survive small perturbations; resonant ones break",
        "Poincaré sections reveal the mixed phase space: regular islands ↔ chaotic sea",
        "Lyapunov exponents and frequency analysis quantify and classify orbital chaos",
        "Gaia + IFU surveys provide unprecedented tests of theoretical orbit models",
    ]
    add_bullet_box(slide, summary,
                   Inches(0.4), Inches(1.25),
                   Inches(12.5), Inches(4.5),
                   font_size=17)

    add_textbox(slide,
                "Recommended reading:\n"
                "• Binney & Tremaine, Galactic Dynamics (2008)   "
                "• Contopoulos, Order and Chaos in Dynamical Astronomy (2002)\n"
                "• Laskar, Icarus 88 (1990)   "
                "• Skokos, Lecture Notes in Physics 790 (2010)",
                Inches(0.4), Inches(5.9),
                Inches(12.5), Inches(1.35),
                font_size=12, italic=True,
                color=RGBColor(0xAA, 0xAA, 0xAA))
    add_footer(slide, 21)

    # -----------------------------------------------------------------------
    # SLIDE 22 – Thank you / Questions
    # -----------------------------------------------------------------------
    slide = prs.slides.add_slide(blank_layout(prs))
    set_slide_bg(slide, BG_COLOR)

    add_textbox(slide, "Thank You",
                Inches(0.5), Inches(2.2),
                Inches(12.3), Inches(1.2),
                font_size=54, bold=True, color=TITLE_COLOR,
                align=PP_ALIGN.CENTER)
    add_textbox(slide, "Questions & Discussion",
                Inches(0.5), Inches(3.55),
                Inches(12.3), Inches(0.7),
                font_size=26, italic=True, color=HEADING_COLOR,
                align=PP_ALIGN.CENTER)
    add_textbox(slide,
                '"The most beautiful thing we can experience is the mysterious.\n'
                'It is the source of all true art and science."\n'
                "— Albert Einstein",
                Inches(2.0), Inches(5.0),
                Inches(9.3), Inches(1.2),
                font_size=14, italic=True,
                color=RGBColor(0x88, 0x88, 0x88),
                align=PP_ALIGN.CENTER)
    add_footer(slide, 22)

    return prs


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Building figures and assembling presentation …")
    prs = build_presentation()
    out = "stellar_dynamics_spiral_galaxies.pptx"
    prs.save(out)
    print(f"Saved: {out}")
    print(f"Slide count: {len(prs.slides)}")
    print()
    print("Open in Apple Keynote:  File → Open  (Keynote accepts .pptx natively)")
    print("Or convert:             keynote --export-to keynote --output <file>.key <file>.pptx")
