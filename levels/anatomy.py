"""LEVEL 4 — אנטומיה של בית ומגמות זמן."""
import pandas as pd
import streamlit as st

import charts as C
import insights as I
import theme as T

MONTHS = ["ינו", "פבר", "מרץ", "אפר", "מאי", "יוני",
          "יולי", "אוג", "ספט", "אוק", "נוב", "דצמ"]


def render(df, full):
    T.level_head("LEVEL 4  //  STATS SCREEN", "אנטומיה של בית — ומה קרה לאורך הזמן")

    T.insight(I.anatomy(df))

    c1, c2 = st.columns([1, 1])
    with c1:
        prof, axes = I.profiles(df)
        if prof:
            st.plotly_chart(C.radar(prof, axes), width="stretch")
    with c2:
        st.markdown("#### מה הראדאר מראה")
        T.note(
            "כל ציר מנורמל ל-0–100 מול כלל השוק, כך שאפשר להשוות מידות שונות "
            "על אותו גרף. השטח הכלוא בכל צורה הוא \"נפח הנכס\".")
        T.note(
            "ההבדל בין הרבעון העליון לתחתון <b>אינו אחיד על כל הצירים</b>: "
            "הפער הגדול ביותר הוא באיכות הבנייה ובשטח, "
            "והקטן ביותר בחדרי הרחצה. במילים אחרות — בתים יקרים אינם "
            "\"אותו בית עם עוד אמבטיה\", הם קטגוריית מוצר אחרת.")
        q = df.groupby("OverallQual")["SalePrice"].median()
        if len(q) >= 2:
            T.hud("QUALITY MULTIPLIER", f"x{q.iloc[-1] / q.iloc[0]:.1f}",
                  f"מציון {int(q.index[0])} לציון {int(q.index[-1])}", T.YELLOW)

    st.markdown("---")
    qagg = df.groupby("OverallQual")["SalePrice"].agg(["count", "median"])
    qagg = qagg[qagg["count"] >= 3]
    if len(qagg) >= 2:
        st.plotly_chart(C.quality_bars(qagg), width="stretch")
        T.note("שימו לב לצורת העקומה: המעבר מ-5 ל-6 שווה הרבה פחות כסף מהמעבר "
               "מ-8 ל-9. <b>איכות היא מכפיל, לא תוספת</b> — ולכן שיפוץ בבית "
               "שכבר איכותי מחזיר יותר משיפוץ זהה בבית בינוני.")

    st.markdown("---")
    st.markdown("### גיל הבית")
    dagg = df.groupby("Decade")["SalePrice"].agg(["count", "median"])
    dagg = dagg[dagg["count"] >= 5]
    if len(dagg) >= 2:
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(C.decade_price(dagg), width="stretch")
        with c2:
            st.plotly_chart(C.decade_volume(dagg), width="stretch")
        T.note("שני תרשימים ולא אחד עם שני צירים — הם מודדים דברים שונים "
               "בסקאלות שונות. יחד הם מספרים: <b>בתים חדשים שווים יותר</b>, "
               "אבל גל הבנייה הגדול היה בשנות ה-50–70, כך שרוב המלאי בשוק "
               "הוא דווקא מהעשורים הזולים יותר.")

    st.markdown("---")
    st.markdown("### מגמות מכירה")
    c1, c2 = st.columns(2)
    with c1:
        y = df.groupby("YrSold")["SalePrice"].agg(["count", "median"])
        if len(y) >= 2:
            st.plotly_chart(
                C.line_series(y.index, y["median"], "מחיר חציוני לפי שנת מכירה",
                              "שנת מכירה", T.S_CYAN, y["count"]),
                width="stretch")
    with c2:
        m = df.groupby("MoSold")["SalePrice"].agg(["count", "median"])
        if len(m) >= 2:
            st.plotly_chart(
                C.line_series(m.index, m["median"], "עונתיות — מחיר לפי חודש מכירה",
                              "חודש", T.S_PURPLE, m["count"],
                              [MONTHS[i - 1] for i in m.index]),
                width="stretch")
    vol = df["MoSold"].value_counts().sort_index()
    if len(vol):
        peak = vol.idxmax()
        T.note(
            f"שיא נפח העסקאות הוא ב<b>{MONTHS[peak - 1]}</b> ({vol.max()} מכירות) — "
            "עונת הקיץ האמריקאית הקלאסית, כשמשפחות עוברות דירה בין שנות לימוד. "
            "המחיר החציוני עצמו כמעט לא משתנה בין החודשים: <b>העונתיות משפיעה על "
            "כמות העסקאות, לא על המחיר</b>.")
