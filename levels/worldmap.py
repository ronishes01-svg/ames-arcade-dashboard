"""LEVEL 2 — שכונות."""
import pandas as pd
import streamlit as st

import charts as C
import insights as I
import theme as T


def render(df, full):
    T.level_head("LEVEL 2  //  WORLD MAP", "השכונות — המשתנה שאי אפשר לשפץ")

    agg = df.groupby("Neighborhood")["SalePrice"].agg(["count", "median", "mean"])
    agg = agg[agg["count"] >= 3]
    if agg.empty:
        st.warning("אין מספיק עסקאות בשכונות שנבחרו. הרחיבו את הפילטרים.")
        return

    cols = st.columns(4)
    with cols[0]:
        T.hud("ZONES", f"{len(agg)}", "שכונות עם 3+ עסקאות", T.CYAN)
    with cols[1]:
        T.hud("TOP ZONE", agg["median"].idxmax(),
              f"חציון ${agg['median'].max():,.0f}", T.YELLOW)
    with cols[2]:
        T.hud("VALUE ZONE", agg["median"].idxmin(),
              f"חציון ${agg['median'].min():,.0f}", T.GREEN)
    with cols[3]:
        T.hud("GAP", f"x{agg['median'].max() / agg['median'].min():.1f}",
              "פער בין היקרה לזולה", T.MAGENTA)

    st.write("")
    T.insight(I.neighborhoods(df))

    st.plotly_chart(C.neighborhood_bars(agg), width="stretch")

    st.markdown("---")
    top = agg.nlargest(10, "count").index.tolist()
    st.plotly_chart(C.neighborhood_box(df[df["Neighborhood"].isin(top)], top),
                    width="stretch")
    T.note("כל תיבה היא שכונה: הקו האמצעי הוא החציון, התיבה היא 50% המרכזיים "
           "והנקודות הבודדות הן חריגים. <b>ככל שהתיבה גבוהה יותר — כך השכונה "
           "מגוונת יותר</b>, ושם יש הזדמנויות: אותה שכונה מכילה גם בתים זולים וגם יקרים.")

    st.markdown("---")
    st.plotly_chart(C.neighborhood_treemap(agg), width="stretch")

    st.markdown("---")
    st.markdown("### טבלת הדירוג המלאה")
    tbl = agg.sort_values("median", ascending=False).reset_index()
    tbl.insert(0, "דירוג", range(1, len(tbl) + 1))
    tbl["ppsf"] = df.groupby("Neighborhood")["PricePerSF"].median().reindex(
        tbl["Neighborhood"]).to_numpy()
    html = ['<table style="width:100%;border-collapse:collapse;border:3px solid '
            f'{T.GRID};background:{T.BG_CARD}">',
            f'<tr style="background:{T.BG_DEEP}">']
    for h in ["מחיר לרגל״ר", "מחיר ממוצע", "מחיר חציוני", "עסקאות", "שכונה", "דירוג"]:
        html.append(f'<th style="color:{T.CYAN};padding:10px;text-align:right;'
                    f'border-bottom:2px solid {T.GRID};font-size:13px">{h}</th>')
    html.append("</tr>")
    for _, r in tbl.iterrows():
        bar = T.pixel_bar(r["median"] / tbl["median"].max(), 8, T.CYAN)
        num = (f'font-family:VT323,monospace;font-size:20px;direction:ltr;'
               f'text-align:left;padding:6px 10px;border-bottom:1px solid {T.GRID}')
        html.append(
            f'<tr><td style="{num};color:{T.MUTED}">${r["ppsf"]:,.0f}</td>'
            f'<td style="{num};color:{T.MUTED}">${r["mean"]:,.0f}</td>'
            f'<td style="{num};color:{T.YELLOW}">${r["median"]:,.0f}</td>'
            f'<td style="{num};color:{T.TEXT}">{int(r["count"])}</td>'
            f'<td style="padding:6px 10px;text-align:right;border-bottom:1px solid '
            f'{T.GRID};font-weight:700">{r["Neighborhood"]} &nbsp;{bar}</td>'
            f'<td style="{num};color:{T.MAGENTA}">{r["דירוג"]}</td></tr>')
    html.append("</table>")
    st.markdown("".join(html), unsafe_allow_html=True)
