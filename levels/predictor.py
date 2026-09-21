"""LEVEL 5 — מנבא המחיר ומיני-משחק הניחוש."""
import pandas as pd
import streamlit as st

import charts as C
import data as D
import model as M
import theme as T

RANKS = [(0.97, "REAL ESTATE TYCOON", "מדהים. אתה קורא את השוק הזה כמו ספר.", T.YELLOW),
         (0.92, "SENIOR AGENT", "מצוין — סטייה קטנה מאוד מהמודל.", T.GREEN),
         (0.85, "AGENT", "לא רע בכלל. אתה בטווח ההגיוני.", T.CYAN),
         (0.70, "ROOKIE", "יש כיוון, אבל הפער עוד גדול.", T.PURPLE),
         (0.00, "TOURIST", "הפער ענק. כדאי לחזור לשלבים 3–4.", T.MAGENTA)]


def render(df, full):
    T.level_head("LEVEL 5  //  BOSS FIGHT", "בנה בית, נחש מחיר — ותראה אם ניצחת את המודל")

    model, columns, metrics, importances = M.train(full)

    cols = st.columns(4)
    with cols[0]:
        T.hud("MODEL R²", f"{metrics['r2']:.3f}", "מהשונות במחיר מוסברת", T.CYAN)
    with cols[1]:
        T.hud("AVG ERROR", f"${metrics['mae']:,.0f}", "סטייה ממוצעת בדולרים", T.YELLOW)
    with cols[2]:
        T.hud("ERROR %", f"{metrics['mape']:.1f}%", "סטייה ממוצעת באחוזים", T.MAGENTA)
    with cols[3]:
        T.hud("TRAIN / TEST", f"{metrics['n_train']}/{metrics['n_test']}",
              "בתים לאימון / לבדיקה", T.GREEN)

    T.note(
        f"המודל הוא <b>Gradient Boosting</b> שאומן על {metrics['n_train']} בתים ונבדק על "
        f"{metrics['n_test']} בתים שהוא <b>לא ראה</b> באימון. הוא מסביר "
        f"<b>{metrics['r2'] * 100:.1f}%</b> מהשונות, עם טעות ממוצעת של כ-"
        f"<b>{metrics['mape']:.1f}%</b>. זה טוב — אבל לא קסם: הנתונים הם של איימס, "
        "איווה, 2006–2010, ואין להם שום תוקף לשוק אחר או לימינו.")

    st.markdown("---")
    st.markdown("### 🏗 בנה את הבית שלך")

    med = full.median(numeric_only=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        area = st.slider("שטח מגורים מעל הקרקע (רגל״ר)", 400, 4000,
                         int(med["GrLivArea"]), 50)
        qual = st.slider("ציון איכות בנייה (1–10)", 1, 10, int(med["OverallQual"]))
        cond = st.slider("ציון מצב הבית (1–10)", 1, 10, int(med["OverallCond"]))
        lot = st.slider("שטח המגרש (רגל״ר)", 1300, 30000, int(med["LotArea"]), 100)
    with c2:
        bsmt = st.slider("שטח מרתף (רגל״ר)", 0, 3000, int(med["TotalBsmtSF"]), 50)
        garage = st.slider("מקומות חניה במוסך", 0, 4, int(med["GarageCars"]))
        baths = st.slider("סך חדרי רחצה", 1.0, 6.0, float(med["TotalBath"]), .5)
        fires = st.slider("קמינים", 0, 3, int(med["Fireplaces"]))
    with c3:
        built = st.slider("שנת בנייה", 1880, 2010, int(med["YearBuilt"]))
        remod = st.slider("שנת שיפוץ אחרון", 1950, 2010,
                          max(int(med["YearRemodAdd"]), built))
        beds = st.slider("חדרי שינה", 0, 8, int(med["BedroomAbvGr"]))
        rooms = st.slider("סך חדרים מעל הקרקע", 2, 14, int(med["TotRmsAbvGrd"]))

    c1, c2 = st.columns(2)
    with c1:
        hood = st.selectbox("שכונה", sorted(full["Neighborhood"].unique()),
                            index=sorted(full["Neighborhood"].unique()).index("NAmes"))
    with c2:
        air = st.radio("מיזוג אוויר מרכזי", ["Y", "N"], horizontal=True,
                       format_func=lambda x: "יש" if x == "Y" else "אין")

    values = {
        "GrLivArea": area, "OverallQual": qual, "OverallCond": cond,
        "TotalBsmtSF": bsmt, "GarageCars": garage, "TotalBath": baths,
        "YearBuilt": built, "YearRemodAdd": max(remod, built), "LotArea": lot,
        "Fireplaces": fires, "BedroomAbvGr": beds, "TotRmsAbvGrd": rooms,
    }
    row = M.build_row(columns, values, hood, air)
    pred = M.predict(model, row)

    st.markdown("---")
    st.markdown("### 🎯 נחש את המחיר לפני שהמודל מדבר")
    c1, c2 = st.columns([1, 1])
    with c1:
        guess = st.number_input("הניחוש שלך ($)", 20000, 900000, 180000, 5000)
    with c2:
        st.write("")
        st.write("")
        fight = st.button("FIGHT!  ⚔  חשוף את תחזית המודל")

    if fight:
        st.session_state["guess"] = guess
        st.session_state["pred"] = pred

    if st.session_state.get("pred"):
        g, p = st.session_state["guess"], st.session_state["pred"]
        acc = 1 - abs(g - p) / p
        rank, msg, color = next(
            (r[1], r[2], r[3]) for r in RANKS if acc >= r[0])
        score = max(0, int(acc * 10000))

        cols = st.columns([1, 1, 1])
        with cols[0]:
            T.hud("MODEL SAYS", f"${p:,.0f}", "תחזית המודל לבית שבנית", T.CYAN)
        with cols[1]:
            T.hud("YOUR GUESS", f"${g:,.0f}",
                  f"פער של ${abs(g - p):,.0f}", T.YELLOW)
        with cols[2]:
            T.hud("SCORE", f"{score:,}", f"דיוק {acc * 100:.1f}%", color)

        st.markdown(
            f'<div class="hud-card" style="--bc:{color};margin-top:14px;text-align:center">'
            f'<div style="font-family:\'Press Start 2P\',monospace;font-size:20px;'
            f'color:{color};text-shadow:0 0 18px {color};direction:ltr;'
            f'letter-spacing:2px">{rank}</div>'
            f'<div style="margin-top:14px">{T.pixel_bar(max(acc, 0), 26, color)}</div>'
            f'<div style="font-size:16px;margin-top:12px;font-weight:700">{msg}</div>'
            f'</div>', unsafe_allow_html=True)

        st.plotly_chart(C.guess_gauge(g, p), width="stretch")

    st.markdown("---")
    st.markdown("### למה המודל אמר את מה שאמר")
    baseline = {k: float(med[k]) for k in values if k in med.index}
    contrib = M.contributions(model, columns, values, hood, air, baseline)
    rows = [(D.he(k) if k != "Neighborhood" else f"שכונה: {hood}", v)
            for k, v in contrib if abs(v) > 50]
    if rows:
        st.plotly_chart(C.contribution_bars(rows), width="stretch")
        T.note(
            "כל עמודה עונה על שאלה אחת: <b>בכמה הייתה משתנה התחזית אם הפיצ'ר הזה "
            "היה חוזר לערך החציוני בשוק?</b> ירוק = התכונה מוסיפה לך ערך מעל "
            "הבית הממוצע, מג'נטה = גורעת. שימו לב שהסכום אינו בדיוק הפער מהחציון — "
            "המודל לא ליניארי, והפיצ'רים משפיעים זה על זה.")
    else:
        T.note("בנית בית שקרוב מאוד לחציון השוק בכל הממדים — אין פיצ'ר בולט שמזיז "
               "את התחזית. הזיזו סליידר כדי לראות השפעה.")

    with st.expander("מה המודל למד שחשוב — משקלי הפיצ'רים"):
        top = importances.nlargest(12)
        for name, w in top.items():
            label = D.he(name) if not name.startswith(("Neighborhood_", "CentralAir_")) \
                else name.replace("Neighborhood_", "שכונה ").replace("CentralAir_", "מיזוג ")
            st.markdown(
                f'<div style="display:flex;gap:14px;align-items:center;margin:6px 0">'
                f'<span style="min-width:190px;font-weight:700">{label}</span>'
                f'{T.pixel_bar(w / top.max(), 20, T.S_CYAN)}'
                f'<span class="num" style="color:{T.MUTED}">{w * 100:.1f}%</span></div>',
                unsafe_allow_html=True)
        T.note("משקל גבוה = המודל נשען על הפיצ'ר הזה הרבה. זה <b>לא</b> אותו דבר "
               "כמו קורלציה משלב 3: כאן זה נמדד בנוכחות כל שאר הפיצ'רים.")
