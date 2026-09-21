"""LEVEL 1 — סקירת השוק."""
import streamlit as st

import charts as C
import data as D
import insights as I
import theme as T


def render(df, full):
    T.level_head("LEVEL 1  //  INSERT COIN", "סקירת השוק — מה יש לנו כאן בכלל")

    s = df["SalePrice"]
    cols = st.columns(4)
    with cols[0]:
        T.hud("HOUSES SOLD", f"{len(df):,}", "עסקאות בטווח שנבחר", T.CYAN)
    with cols[1]:
        T.hud("MEDIAN PRICE", f"${s.median():,.0f}", "הבית הטיפוסי", T.YELLOW)
    with cols[2]:
        T.hud("PRICE RANGE", f"${s.min() / 1000:,.0f}K–{s.max() / 1000:,.0f}K",
              f"פער של פי {s.max() / s.min():.0f}", T.MAGENTA)
    with cols[3]:
        T.hud("AVG $/SQFT", f"${df['PricePerSF'].median():,.0f}",
              "מחיר חציוני לרגל״ר מגורים", T.GREEN)

    st.write("")
    T.insight(I.overview(df))

    st.plotly_chart(C.price_histogram(s), width="stretch")
    T.note("ההתפלגות <b>אינה סימטרית</b>: היא נדחסת סביב 130–215 אלף דולר ונמשכת "
           "בזנב ארוך ודק ימינה עד 755 אלף. לכן כל ניתוח שמסתמך על הממוצע "
           "יתאר בית שכמעט לא קיים בשוק.")

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(
            C.donut(df["SaleCondHe"].value_counts(), "מי מוכר למי — סוג העסקה"),
            width="stretch")
        T.note("רק עסקאות <b>מכירה רגילה</b> משקפות מחיר שוק אמיתי. "
               "מכירות בתוך המשפחה או בתים שנמכרו לפני סיום הבנייה מעוותים "
               "כל ממוצע שמחשבים עליהם.")
    with c2:
        st.plotly_chart(
            C.donut(df["HouseStyleHe"].value_counts().head(6),
                    "איך הבתים בנויים — סגנון"),
            width="stretch")
        T.note("השוק נשלט בפועל על ידי שני סגנונות: <b>קומה אחת</b> ו<b>שתי קומות</b>. "
               "כל השאר הוא שוליים סטטיסטיים — חשוב לזכור כשמסיקים מסקנות "
               "על סגנונות נדירים.")

    st.markdown("---")
    st.markdown("### איכות הנתונים — לפני שמסיקים משהו")
    mdf = D.raw_missing()
    c1, c2 = st.columns([1.35, 1])
    with c1:
        st.plotly_chart(C.missing_bars(mdf), width="stretch")
    with c2:
        absent = mdf[mdf["משמעות"] == "אין תכונה כזו בנכס"]["חסרים"].sum()
        real = mdf[mdf["משמעות"] == "נתון חסר אמיתי"]["חסרים"].sum()
        tot = absent + real
        T.hud("DATA INTEGRITY", f"{(1 - real / (len(df) * 81)) * 100:.1f}%",
              "אחוז התאים עם נתון אמיתי", T.GREEN)
        st.write("")
        st.markdown(
            f'<div class="hud-card" style="--bc:{T.PURPLE}">'
            f'<span class="hud-label">MISSING BREAKDOWN</span>'
            f'<div style="font-size:14px;line-height:2">'
            f'{T.pixel_bar(absent / tot, 18, T.PURPLE)}<br>'
            f'<b style="color:{T.PURPLE}">{absent:,}</b> תאים — אין תכונה כזו בנכס '
            f'(בלי בריכה, בלי סמטה)<br><br>'
            f'{T.pixel_bar(real / tot, 18, T.MAGENTA)}<br>'
            f'<b style="color:{T.MAGENTA}">{real:,}</b> תאים — נתון חסר באמת, '
            f'הושלם בחציון</div></div>',
            unsafe_allow_html=True)
        st.write("")
        T.note("<b>99.5% מהבתים \"חסרים\" נתון על בריכה</b> — פשוט כי אין להם בריכה. "
               "מי שימחק את העמודות האלה בגלל \"חוסרים\" ימחק מידע אמיתי.")
