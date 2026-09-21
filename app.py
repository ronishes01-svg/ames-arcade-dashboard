"""ARCADE REALTY — ניתוח שוק הדיור של איימס בסגנון ארקייד של שנות ה-90."""
import streamlit as st

import data as D
import theme as T
from levels import anatomy, drivers, overview, predictor, worldmap

st.set_page_config(page_title="ARCADE REALTY — ניתוח שוק הדיור",
                   page_icon="🕹", layout="wide",
                   initial_sidebar_state="expanded")
T.inject()

full = D.load_data()

# ---------------- סיידבר ----------------
with st.sidebar:
    st.markdown(
        f'<div style="border:3px solid {T.CYAN};padding:12px;text-align:center;'
        f'background:{T.BG_CARD};box-shadow:5px 5px 0 rgba(0,0,0,.6)">'
        f'<div style="font-family:\'Press Start 2P\',monospace;font-size:11px;'
        f'color:{T.YELLOW};direction:ltr;line-height:1.7">GAME<br>SETTINGS</div></div>',
        unsafe_allow_html=True)
    st.write("")

    pmin, pmax = int(full["SalePrice"].min()), int(full["SalePrice"].max())
    price = st.slider("טווח מחירים ($)", pmin, pmax, (pmin, pmax), 5000,
                      format="$%d")
    ymin, ymax = int(full["YearBuilt"].min()), int(full["YearBuilt"].max())
    years = st.slider("שנת בנייה", ymin, ymax, (ymin, ymax))
    hoods = st.multiselect("שכונות (ריק = הכול)",
                           sorted(full["Neighborhood"].unique()))
    conds = st.multiselect(
        "סוג העסקה (ריק = הכול)",
        sorted(full["SaleCondition"].unique()),
        format_func=lambda c: D.SALE_COND_HE.get(c, c))

    df = D.apply_filters(full, price, hoods, years, conds)

    st.write("")
    pct = len(df) / len(full)
    st.markdown(
        f'<div class="hud-card" style="--bc:{T.GREEN}">'
        f'<span class="hud-label">HOUSES IN PLAY</span>'
        f'<div class="hud-value" style="font-size:34px">{len(df):,}</div>'
        f'<div style="margin-top:8px">{T.pixel_bar(pct, 16, T.GREEN)}</div>'
        f'<div class="hud-sub">{pct * 100:.0f}% מתוך {len(full):,} העסקאות</div></div>',
        unsafe_allow_html=True)

    st.write("")
    T.note("הפילטרים משפיעים על שלבים 1–4. <b>שלב 5 תמיד מאומן על כל הדאטה</b> "
           "כדי שהמודל לא ישתנה תחת הרגליים.")

    st.markdown("---")
    st.markdown(
        f'<div style="font-size:12px;color:{T.MUTED};line-height:1.8">'
        f'<b style="color:{T.CYAN}">מקור הנתונים</b><br>'
        f'Ames Housing Dataset — 1,460 עסקאות מכירת בתים בעיר איימס, איווה, '
        f'ארה״ב, 2006–2010. 81 עמודות לכל נכס.</div>',
        unsafe_allow_html=True)

# ---------------- ראש ----------------
T.marquee(
    "ARCADE REALTY  //  AMES 1872-2010",
    "ניתוח שוק הדיור של איימס, איווה — 1,460 עסקאות, 81 משתנים, 5 שלבים",
    "השתמשו בפילטרים מימין כדי לשנות את חתך הנתונים · כל תרשים אינטראקטיבי — "
    "רחפו עם העכבר לפרטים")

if df.empty:
    st.markdown(
        f'<div class="hud-card" style="--bc:{T.MAGENTA};text-align:center;'
        f'margin-top:30px;padding:50px">'
        f'<div style="font-family:\'Press Start 2P\',monospace;font-size:26px;'
        f'color:{T.MAGENTA};text-shadow:0 0 20px {T.MAGENTA};direction:ltr">'
        f'GAME OVER</div>'
        f'<div style="font-size:18px;margin-top:22px;font-weight:700">'
        f'אף בית לא עבר את הפילטרים שבחרת</div>'
        f'<div style="font-size:15px;margin-top:10px;color:{T.MUTED}">'
        f'הרחיבו את טווח המחירים או את שנות הבנייה בסרגל מימין</div></div>',
        unsafe_allow_html=True)
    st.stop()

# ---------------- בחירת שלב ----------------
LEVELS = [
    ("שלב 1 · סקירת השוק", overview),
    ("שלב 2 · שכונות", worldmap),
    ("שלב 3 · מה מניע מחיר", drivers),
    ("שלב 4 · אנטומיה וזמן", anatomy),
    ("שלב 5 · מנבא המחיר", predictor),
]
# קישור ישיר לשלב: ?level=3
names = [name for name, _ in LEVELS]
if "level_select" not in st.session_state:
    try:
        idx = int(st.query_params.get("level", 1)) - 1
    except ValueError:
        idx = 0
    st.session_state["level_select"] = names[idx] if 0 <= idx < len(names) else names[0]

choice = st.radio("LEVEL SELECT", names, horizontal=True,
                  label_visibility="collapsed", key="level_select")
st.query_params["level"] = str(names.index(choice) + 1)
st.write("")
dict(LEVELS)[choice].render(df, full)

st.markdown("---")
st.markdown(
    f'<div style="text-align:center;color:{T.MUTED};font-size:12px;'
    f'line-height:2;padding:10px 0 30px">'
    f'<span style="font-family:\'Press Start 2P\',monospace;color:{T.CYAN};'
    f'direction:ltr">GAME OVER — INSERT COIN TO CONTINUE</span><br>'
    f'נבנה ב-Streamlit · pandas · Plotly · scikit-learn &nbsp;|&nbsp; '
    f'Ames Housing Dataset (De Cock, 2011)</div>',
    unsafe_allow_html=True)
