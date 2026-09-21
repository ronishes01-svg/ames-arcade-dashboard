"""LEVEL 3 — מה מניע את המחיר."""
import streamlit as st

import charts as C
import data as D
import insights as I
import theme as T


def render(df, full):
    T.level_head("LEVEL 3  //  POWER-UPS", "מה באמת מניע את המחיר")

    corr = I.price_corr(df, 15)
    T.insight(I.drivers(df))

    c1, c2 = st.columns([1, 1])
    with c1:
        st.plotly_chart(C.correlation_bars(corr, D.he), width="stretch")
    with c2:
        st.markdown("#### איך קוראים את הגרף הזה")
        T.note(
            "קורלציה נעה בין 1- ל-1+. <b>קרוב ל-1+</b> = ככל שהמשתנה גדל, המחיר עולה. "
            "<b>קרוב ל-0</b> = אין קשר ליניארי. <b>שלילי</b> (מג'נטה) = הקשר הפוך.")
        top3 = corr.head(3)
        for i, (name, v) in enumerate(top3.items()):
            st.markdown(
                f'<div class="hud-card" style="--bc:{T.SERIES[i]};margin-bottom:10px">'
                f'<span class="hud-label">#{i + 1} DRIVER</span>'
                f'<div style="font-size:18px;font-weight:900;color:{T.TEXT}">'
                f'{D.he(name)}</div>'
                f'<div style="margin-top:8px">{T.pixel_bar(abs(v), 20, T.SERIES[i])}</div>'
                f'<div class="hud-sub">קורלציה {v:+.2f} · מסביר '
                f'{v ** 2 * 100:.0f}% מהשונות במחיר</div></div>',
                unsafe_allow_html=True)
        neg = corr[corr < 0]
        if len(neg):
            T.note(
                f"הקשר השלילי הבולט: <b>{D.he(neg.index[0])}</b> ({neg.iloc[0]:+.2f}). "
                "זה לא אומר שהתכונה מורידה את ערך הבית — אלא שהיא נפוצה יותר "
                "דווקא בבתים ישנים וקטנים.")

    st.markdown("---")
    out = I.outliers(df)
    st.plotly_chart(C.area_scatter(df, out), width="stretch")
    T.note(
        "צבע הנקודה = ציון האיכות. רואים שני כיוונים בו-זמנית: <b>ימינה = גדול יותר, "
        "צהוב = איכותי יותר</b>, ושניהם מעלים את המחיר. "
        + (f"הריבועים המסומנים הם <b>{len(out)} חריגים מפורסמים</b> בדאטהסט: בתים ענקיים "
           "מעל 4,000 רגל״ר שנמכרו מתחת ל-300 אלף — עסקאות של בנייה שלא הושלמה, "
           "לא מחירי שוק. כל מודל ניבוי רציני מסיר אותם." if len(out) else ""))

    st.markdown("---")
    c1, c2 = st.columns([1.2, 1])
    with c1:
        top10 = ["SalePrice"] + I.price_corr(df, 9).index.tolist()
        m = df[top10].corr(numeric_only=True)
        st.plotly_chart(C.corr_heatmap(m, D.he), width="stretch")
    with c2:
        st.markdown("#### הבעיה שמפת החום חושפת")
        T.note(
            "<b>מולטיקולינאריות</b>: המנבאים החזקים קשורים חזק גם זה לזה. "
            "שטח המוסך ומספר מקומות החניה הם כמעט אותו משתנה (0.88), "
            "וכך גם שטח המרתף וקומת הקרקע. "
            "המשמעות: אי אפשר פשוט לסכום את ההשפעות — הן נספרות פעמיים.")
        T.note("לכן בשלב 5 המודל הוא <b>Gradient Boosting</b> ולא רגרסיה ליניארית פשוטה: "
               "הוא מתמודד עם החפיפה הזו ועם קשרים לא-ליניאריים.")

    st.markdown("---")
    rows = I.feature_uplift(df)
    if rows:
        st.plotly_chart(C.uplift_bars(rows), width="stretch")
        best = rows[0]
        T.note(
            f"<b>{best[0]}</b> מציג את הפער הגדול ביותר: {best[1]:,.0f}$ מול "
            f"{best[2]:,.0f}$ — תוספת של <b>{best[3]:.0f}%</b>. "
            "חשוב להיזהר בפרשנות: בתים בלי מיזוג מרכזי הם כמעט תמיד בתים ישנים "
            "וקטנים יותר, כך שחלק מהפער נובע מהגיל ולא מהמזגן עצמו.")
