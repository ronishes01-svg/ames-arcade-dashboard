"""בוני תרשימי Plotly בערכת הארקייד, עם יישור RTL."""
import numpy as np
import pandas as pd
import plotly.graph_objects as go

import theme as T

HE_FONT = "Heebo, Arial Hebrew, sans-serif"


def style(fig: go.Figure, title: str = "", height: int = 420,
          legend: bool = False, right_axis: bool = False) -> go.Figure:
    """מחיל את ערכת הארקייד ואת יישור ה-RTL על תרשים.

    right_axis=True כשציר הקטגוריות הועבר לימין (RTL) — אז צריך שוליים
    ימניים רחבים, אחרת תוויות הקטגוריות נחתכות לגמרי.
    """
    fig.update_layout(
        title=dict(text=f"<b>{title}</b>", x=0.99, xanchor="right", y=0.97,
                   font=dict(family=HE_FONT, size=17, color=T.TEXT)),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(11,11,30,.55)",
        font=dict(family=HE_FONT, size=13, color=T.TEXT),
        height=height,
        margin=dict(l=20, r=180 if right_axis else 20,
                    t=60 if title else 24, b=90 if legend else 40),
        showlegend=legend,
        legend=dict(x=1, xanchor="right", y=-0.16, yanchor="top",
                    orientation="h", bgcolor="rgba(20,20,51,.85)",
                    bordercolor=T.GRID, borderwidth=2,
                    font=dict(family=HE_FONT, size=12)),
        hoverlabel=dict(bgcolor=T.BG_CARD, bordercolor=T.CYAN,
                        font=dict(family=HE_FONT, size=13, color=T.TEXT)),
        colorway=T.SERIES,
        bargap=0.22,
    )
    grid = dict(gridcolor=T.GRID, gridwidth=1, zerolinecolor=T.GRID,
                linecolor=T.GRID, linewidth=2, automargin=True,
                tickfont=dict(family=HE_FONT, size=12, color=T.MUTED),
                title=dict(font=dict(family=HE_FONT, size=13, color=T.MUTED),
                           standoff=26))
    fig.update_xaxes(**grid)
    fig.update_yaxes(**grid)
    return fig


def money(v) -> str:
    return f"${v:,.0f}"


# ---------------- LEVEL 1 ----------------
def price_histogram(s: pd.Series) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=s, nbinsx=48, marker=dict(color=T.S_CYAN, line=dict(color=T.BG, width=2)),
        opacity=.9, name="בתים",
        hovertemplate="טווח מחיר: %{x}<br>בתים: %{y}<extra></extra>"))
    med, mean = s.median(), s.mean()
    # שתי ההערות בגבהים שונים — אחרת הן נדרסות זו על זו כשהערכים קרובים
    for val, col, label, ay in [(med, T.YELLOW, "חציון", -6),
                                (mean, T.MAGENTA, "ממוצע", -28)]:
        fig.add_vline(x=val, line=dict(color=col, width=3, dash="dash"))
        fig.add_annotation(x=val, y=1, yref="paper", yanchor="bottom", ay=ay, ax=0,
                           text=f"<b>{label} {money(val)}</b>", showarrow=False,
                           font=dict(family=HE_FONT, color=col, size=13))
    fig.update_xaxes(title="מחיר מכירה ($)", tickprefix="$", tickformat=",.0f")
    fig.update_yaxes(title="מספר בתים")
    return style(fig, "כמה עולה בית? התפלגות המחירים", 430)


def donut(counts: pd.Series, title: str, hole: float = .55) -> go.Figure:
    # פרוסות קטנות לא מקבלות תווית — אחרת האחוזים נדרסים זה על זה
    total = counts.sum()
    labels_shown = ["" if v / total < 0.04 else f"{v / total * 100:.1f}%"
                    for v in counts]
    fig = go.Figure(go.Pie(
        labels=counts.index, values=counts.to_numpy(), hole=hole,
        marker=dict(colors=T.SERIES[:len(counts)],
                    line=dict(color=T.BG, width=3)),
        text=labels_shown, texttemplate="%{text}", textposition="inside",
        insidetextfont=dict(family=HE_FONT, size=14, color="#FFFFFF"),
        textfont=dict(family=HE_FONT, size=12),
        sort=False, direction="clockwise",
        hovertemplate="%{label}<br>%{value} בתים · %{percent}<extra></extra>"))
    fig.update_layout(annotations=[dict(
        text=f"<b>{counts.sum():,}</b><br><span style='font-size:12px'>בתים</span>",
        x=.5, y=.5, showarrow=False,
        font=dict(family=HE_FONT, size=26, color=T.TEXT))] if hole > .3 else [])
    return style(fig, title, 400, legend=True)


def missing_bars(mdf: pd.DataFrame, top: int = 12) -> go.Figure:
    d = mdf.head(top).iloc[::-1]
    colors = [T.S_PURPLE if m == "אין תכונה כזו בנכס" else T.S_MAGENTA
              for m in d["משמעות"]]
    fig = go.Figure(go.Bar(
        x=d["אחוז"], y=d["שם עברי"], orientation="h",
        marker=dict(color=colors, line=dict(color=T.BG, width=2)),
        text=[f"{v}%" for v in d["אחוז"]], textposition="outside",
        textfont=dict(family=HE_FONT, size=12, color=T.TEXT),
        customdata=d["משמעות"],
        hovertemplate="%{y}<br>%{x}% מהשורות<br>%{customdata}<extra></extra>"))
    fig.update_xaxes(title="אחוז השורות ללא ערך", range=[0, 112])
    fig.update_yaxes(side="right")
    return style(fig, "איפה חסרים נתונים — וממה זה נובע", 450, right_axis=True)


# ---------------- LEVEL 2 ----------------
def neighborhood_bars(agg: pd.DataFrame) -> go.Figure:
    d = agg.sort_values("median").copy()
    fig = go.Figure(go.Bar(
        x=d["median"], y=d.index, orientation="h",
        marker=dict(color=T.S_CYAN, line=dict(color=T.BG, width=2)),
        text=[money(v) for v in d["median"]], textposition="outside",
        textfont=dict(family="VT323, monospace", size=16, color=T.TEXT),
        customdata=d["count"],
        hovertemplate="%{y}<br>חציון: %{x:$,.0f}<br>%{customdata} עסקאות<extra></extra>"))
    fig.update_xaxes(title="מחיר חציוני ($)", tickprefix="$", tickformat=",.0f",
                     range=[0, d["median"].max() * 1.22])
    fig.update_yaxes(side="right", tickfont=dict(size=11))
    return style(fig, "טבלת האלופים — שכונות לפי מחיר חציוני", 700, right_axis=True)


def neighborhood_box(df: pd.DataFrame, order) -> go.Figure:
    fig = go.Figure()
    for n in order:
        vals = df.loc[df["Neighborhood"] == n, "SalePrice"]
        fig.add_trace(go.Box(
            y=vals, name=n, marker=dict(color=T.S_CYAN, size=4),
            line=dict(width=2), fillcolor="rgba(20,20,51,.75)",
            boxpoints="outliers",
            hovertemplate=f"{n}<br>%{{y:$,.0f}}<extra></extra>"))
    fig.update_yaxes(title="מחיר מכירה ($)", tickprefix="$", tickformat=",.0f")
    fig.update_xaxes(tickangle=-45, tickfont=dict(size=11))
    return style(fig, "פיזור המחירים בתוך כל שכונה", 480)


def neighborhood_treemap(agg: pd.DataFrame) -> go.Figure:
    fig = go.Figure(go.Treemap(
        labels=agg.index, parents=[""] * len(agg), values=agg["count"],
        marker=dict(colors=agg["median"], colorscale=T.SCALE,
                    line=dict(color=T.BG, width=3),
                    colorbar=dict(title=dict(text="חציון", font=dict(family=HE_FONT, color=T.MUTED)),
                                  tickfont=dict(family=HE_FONT, color=T.MUTED), thickness=14)),
        textinfo="label+value",
        textfont=dict(family=HE_FONT, size=14, color="#FFFFFF"),
        hovertemplate="<b>%{label}</b><br>%{value} עסקאות<br>חציון: %{color:$,.0f}<extra></extra>"))
    return style(fig, "מפת השוק — גודל = נפח עסקאות · צבע = רמת מחיר", 520)


# ---------------- LEVEL 3 ----------------
def correlation_bars(corr: pd.Series, labels) -> go.Figure:
    d = corr.iloc[::-1]
    colors = [T.S_CYAN if v > 0 else T.S_MAGENTA for v in d]
    fig = go.Figure(go.Bar(
        x=d.to_numpy(), y=[labels(i) for i in d.index], orientation="h",
        marker=dict(color=colors, line=dict(color=T.BG, width=2)),
        text=[f"{v:+.2f}" for v in d], textposition="outside",
        textfont=dict(family="VT323, monospace", size=17, color=T.TEXT),
        hovertemplate="%{y}<br>קורלציה: %{x:+.2f}<extra></extra>"))
    fig.update_xaxes(title="עוצמת הקשר למחיר (קורלציית פירסון)", range=[-.45, 1.05],
                     zeroline=True, zerolinewidth=3, zerolinecolor=T.TEXT)
    fig.update_yaxes(side="right")
    return style(fig, "הפאוור-אפים — מה באמת קשור למחיר", 640, right_axis=True)


def area_scatter(df: pd.DataFrame, outliers: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["GrLivArea"], y=df["SalePrice"], mode="markers",
        marker=dict(size=7, color=df["OverallQual"], colorscale=T.SCALE,
                    cmin=1, cmax=10, line=dict(color=T.BG, width=1), opacity=.85,
                    colorbar=dict(title=dict(text="איכות", font=dict(family=HE_FONT, color=T.MUTED)),
                                  tickfont=dict(family=HE_FONT, color=T.MUTED), thickness=14)),
        customdata=np.stack([df["Neighborhood"], df["OverallQual"]], axis=-1),
        hovertemplate="שטח: %{x:,.0f} רגל״ר<br>מחיר: %{y:$,.0f}"
                      "<br>שכונה: %{customdata[0]}<br>איכות: %{customdata[1]}/10<extra></extra>",
        name="בתים"))
    if len(df) > 30:
        z = np.polyfit(df["GrLivArea"], df["SalePrice"], 1)
        xs = np.linspace(df["GrLivArea"].min(), df["GrLivArea"].max(), 50)
        fig.add_trace(go.Scatter(
            x=xs, y=np.polyval(z, xs), mode="lines", name="קו מגמה",
            line=dict(color=T.MAGENTA, width=4, dash="dash"), hoverinfo="skip"))
    if len(outliers):
        fig.add_trace(go.Scatter(
            x=outliers["GrLivArea"], y=outliers["SalePrice"], mode="markers",
            marker=dict(size=18, color="rgba(0,0,0,0)",
                        line=dict(color=T.MAGENTA, width=3), symbol="square"),
            name="חריגים", hovertemplate="חריג ידוע<br>%{x:,.0f} רגל״ר · %{y:$,.0f}<extra></extra>"))
    fig.update_xaxes(title="שטח מגורים מעל הקרקע (רגל״ר)", tickformat=",.0f")
    fig.update_yaxes(title="מחיר מכירה ($)", tickprefix="$", tickformat=",.0f")
    return style(fig, "שטח מול מחיר — כל נקודה היא בית", 520, legend=True)


def corr_heatmap(m: pd.DataFrame, labels) -> go.Figure:
    names = [labels(c) for c in m.columns]
    fig = go.Figure(go.Heatmap(
        z=m.to_numpy(), x=names, y=names, colorscale=T.DIVERGING, zmin=-1, zmax=1,
        xgap=3, ygap=3,
        text=m.round(2).to_numpy(), texttemplate="%{text}",
        textfont=dict(family="VT323, monospace", size=15),
        colorbar=dict(tickfont=dict(family=HE_FONT, color=T.MUTED), thickness=14,
                      x=-0.06, xanchor="right"),
        hovertemplate="%{y} ↔ %{x}<br>קורלציה: %{z:.2f}<extra></extra>"))
    fig.update_xaxes(tickangle=-40, tickfont=dict(size=11))
    fig.update_yaxes(side="right", tickfont=dict(size=11))
    fig = style(fig, "מפת חום — מי קשור למי", 560, right_axis=True)
    fig.update_layout(margin=dict(l=75, r=150, t=60, b=40))
    return fig


def uplift_bars(rows) -> go.Figure:
    """rows: list of (label, with_median, without_median, uplift_pct)"""
    labels = [r[0] for r in rows][::-1]
    with_v = [r[1] for r in rows][::-1]
    without_v = [r[2] for r in rows][::-1]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=without_v, y=labels, orientation="h", name="בלי התכונה",
                         marker=dict(color=T.GRID, line=dict(color=T.BG, width=2)),
                         hovertemplate="בלי: %{x:$,.0f}<extra></extra>"))
    fig.add_trace(go.Bar(x=with_v, y=labels, orientation="h", name="עם התכונה",
                         marker=dict(color=T.S_GREEN, line=dict(color=T.BG, width=2)),
                         text=[f"+{r[3]:.0f}%" for r in rows][::-1],
                         textposition="outside",
                         textfont=dict(family="VT323, monospace", size=18, color=T.YELLOW),
                         hovertemplate="עם: %{x:$,.0f}<extra></extra>"))
    fig.update_layout(barmode="group")
    fig.update_xaxes(title="מחיר חציוני ($)", tickprefix="$", tickformat=",.0f")
    fig.update_yaxes(side="right")
    return style(fig, "כמה שווה כל פאוור-אפ — מחיר חציוני עם ובלי", 460,
                 legend=True, right_axis=True)


# ---------------- LEVEL 4 ----------------
def radar(profiles: dict, axes_he: list) -> go.Figure:
    fig = go.Figure()
    colors = [T.S_CYAN, T.S_PURPLE, T.S_MAGENTA]
    fills = ["rgba(2,167,178,.28)", "rgba(164,112,255,.28)", "rgba(255,50,137,.28)"]
    for (name, vals), col, fill in zip(profiles.items(), colors, fills):
        fig.add_trace(go.Scatterpolar(
            r=list(vals) + [vals[0]], theta=axes_he + [axes_he[0]],
            fill="toself", name=name,
            fillcolor=fill,
            line=dict(color=col, width=3),
            hovertemplate="%{theta}: %{r:.0f}/100<extra>" + name + "</extra>"))
    fig.update_layout(polar=dict(
        bgcolor="rgba(11,11,30,.6)",
        radialaxis=dict(visible=True, range=[0, 100], gridcolor=T.GRID,
                        linecolor=T.GRID, tickfont=dict(family=HE_FONT, size=10, color=T.MUTED)),
        angularaxis=dict(gridcolor=T.GRID, linecolor=T.GRID, direction="clockwise",
                         tickfont=dict(family=HE_FONT, size=13, color=T.TEXT))))
    return style(fig, "פרופיל הבית — זול מול ממוצע מול יקר", 520, legend=True)


def quality_bars(agg: pd.DataFrame) -> go.Figure:
    fig = go.Figure(go.Bar(
        x=agg.index.astype(str), y=agg["median"],
        marker=dict(color=agg["median"], colorscale=T.SCALE,
                    line=dict(color=T.BG, width=2)),
        text=[money(v) for v in agg["median"]], textposition="outside",
        textfont=dict(family="VT323, monospace", size=16, color=T.TEXT),
        customdata=agg["count"],
        hovertemplate="ציון איכות %{x}/10<br>חציון: %{y:$,.0f}<br>%{customdata} בתים<extra></extra>"))
    fig.update_xaxes(title="ציון איכות כללי (1–10)")
    fig.update_yaxes(title="מחיר חציוני ($)", tickprefix="$", tickformat=",.0f",
                     range=[0, agg["median"].max() * 1.18])
    return style(fig, "כל נקודת איכות עולה כסף — והקפיצה מואצת", 440)


def decade_price(agg: pd.DataFrame) -> go.Figure:
    """מחיר חציוני לפי עשור בנייה. ציר יחיד — בלי ציר כפול."""
    fig = go.Figure(go.Scatter(
        x=agg.index, y=agg["median"], mode="lines+markers",
        line=dict(color=T.S_CYAN, width=3),
        marker=dict(size=11, color=T.S_CYAN, symbol="square",
                    line=dict(color=T.BG, width=2)),
        customdata=agg["count"],
        hovertemplate="עשור %{x}<br>חציון: %{y:$,.0f}<br>%{customdata} בתים<extra></extra>"))
    fig.update_xaxes(title="עשור הבנייה", dtick=20)
    fig.update_yaxes(title="מחיר חציוני ($)", tickprefix="$", tickformat=",.0f")
    return style(fig, "כמה שווה בית לפי עשור הבנייה שלו", 380)


def decade_volume(agg: pd.DataFrame) -> go.Figure:
    """כמה בתים נבנו בכל עשור. תרשים נפרד — מידה אחרת, סקאלה אחרת."""
    fig = go.Figure(go.Bar(
        x=agg.index, y=agg["count"],
        marker=dict(color=T.S_PURPLE, line=dict(color=T.BG, width=2)),
        hovertemplate="עשור %{x}<br>%{y} בתים נבנו<extra></extra>"))
    fig.update_xaxes(title="עשור הבנייה", dtick=20)
    fig.update_yaxes(title="מספר בתים שנבנו")
    return style(fig, "מתי נבנה מלאי הבתים בעיר", 380)


def line_series(x, y, title: str, xtitle: str, color: str = T.S_CYAN,
                counts=None, xticktext=None) -> go.Figure:
    fig = go.Figure(go.Scatter(
        x=x, y=y, mode="lines+markers",
        line=dict(color=color, width=3),
        marker=dict(size=11, color=color, symbol="square",
                    line=dict(color=T.BG, width=2)),
        customdata=counts if counts is not None else [0] * len(x),
        hovertemplate="%{x}<br>חציון: %{y:$,.0f}<br>%{customdata} עסקאות<extra></extra>"))
    fig.update_xaxes(title=xtitle)
    if xticktext is not None:
        fig.update_xaxes(tickmode="array", tickvals=list(x), ticktext=xticktext)
    fig.update_yaxes(title="מחיר חציוני ($)", tickprefix="$", tickformat=",.0f")
    return style(fig, title, 400)


# ---------------- LEVEL 5 ----------------
def contribution_bars(rows) -> go.Figure:
    """rows: list of (label, delta) — תרומה בדולרים לעומת בית בסיס."""
    rows = sorted(rows, key=lambda r: abs(r[1]))
    labels = [r[0] for r in rows]
    vals = [r[1] for r in rows]
    colors = [T.S_GREEN if v >= 0 else T.S_MAGENTA for v in vals]
    fig = go.Figure(go.Bar(
        x=vals, y=labels, orientation="h",
        marker=dict(color=colors, line=dict(color=T.BG, width=2)),
        text=[f"{'+' if v >= 0 else '−'}${abs(v):,.0f}" for v in vals],
        textposition="outside",
        textfont=dict(family="VT323, monospace", size=17, color=T.TEXT),
        hovertemplate="%{y}<br>השפעה: %{x:$,.0f}<extra></extra>"))
    span = max(abs(v) for v in vals) * 1.45 if vals else 1
    fig.update_xaxes(title="השפעה על התחזית מול בית ממוצע ($)", range=[-span, span],
                     zeroline=True, zerolinewidth=3, zerolinecolor=T.TEXT,
                     tickprefix="$", tickformat=",.0f")
    fig.update_yaxes(side="right")
    return style(fig, "מה הזיז את התחזית שלך", 420, right_axis=True)


def guess_gauge(guess: float, actual: float) -> go.Figure:
    lo = min(guess, actual) * .78
    hi = max(guess, actual) * 1.22
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[actual], y=[1], mode="markers+text", name="תחזית המודל",
        marker=dict(size=34, color=T.S_CYAN, symbol="square",
                    line=dict(color=T.TEXT, width=3)),
        text=[f"<b>{money(actual)}</b>"], textposition="top center",
        textfont=dict(family="VT323, monospace", size=22, color=T.TEXT),
        hovertemplate="תחזית המודל: %{x:$,.0f}<extra></extra>"))
    fig.add_trace(go.Scatter(
        x=[guess], y=[1], mode="markers+text", name="הניחוש שלך",
        marker=dict(size=34, color=T.S_YELLOW, symbol="diamond",
                    line=dict(color=T.TEXT, width=3)),
        text=[f"<b>{money(guess)}</b>"], textposition="bottom center",
        textfont=dict(family="VT323, monospace", size=22, color=T.TEXT),
        hovertemplate="הניחוש שלך: %{x:$,.0f}<extra></extra>"))
    fig.add_shape(type="line", x0=min(guess, actual), x1=max(guess, actual),
                  y0=1, y1=1, line=dict(color=T.MAGENTA, width=4, dash="dot"))
    fig.update_xaxes(range=[lo, hi], tickprefix="$", tickformat=",.0f", title="")
    fig.update_yaxes(visible=False, range=[.5, 1.5])
    return style(fig, "", 230, legend=True)
