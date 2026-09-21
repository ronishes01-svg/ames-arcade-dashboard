"""ערכת עיצוב ארקייד 90' — פלטה, CSS פיקסלי ורכיבי HUD."""
import streamlit as st

# ---------- פלטה ----------
BG        = "#0B0B1E"
BG_CARD   = "#141433"
BG_DEEP   = "#070714"
CYAN      = "#00F0FF"
MAGENTA   = "#FF2E88"
YELLOW    = "#FFD300"
GREEN     = "#3DFF6E"
PURPLE    = "#9B5CFF"
ORANGE    = "#FF7A18"
TEXT      = "#E8E8FF"
MUTED     = "#8C8CB8"
GRID      = "#2A2A55"

# ---------- צבעי תרשימים ----------
# הצבעים שלמעלה הם ה"כרום" של הממשק (מסגרות, זוהר, כותרות) — ניאון מלא.
# צבעי הסדרות בתרשימים מוצמדים לרצועת הבהירות של מצב כהה (OKLCH L 0.48–0.67)
# ומסודרים בסדר קבוע שעבר אימות CVD (ΔE 10.7 deutan · 16.4 ראייה רגילה)
# בכלי validate_palette.js מול משטח #0B0B1E. הסדר קבוע — לא ממחזרים ולא מערבבים.
SERIES = ["#02A7B2",  # ציאן
          "#01B241",  # ירוק
          "#A470FF",  # סגול
          "#B09101",  # צהוב
          "#FF3289",  # מג'נטה
          "#E76A01",  # כתום
          "#019EE2",  # כחול
          "#FF444B"]  # אדום
S_CYAN, S_GREEN, S_PURPLE, S_YELLOW, S_MAGENTA, S_ORANGE, S_BLUE, S_RED = SERIES

# סדרתי (עוצמה): גוון אחד, כהה → בהיר. לא קשת.
SCALE = [[0.00, "#0E2A33"], [0.25, "#0D5F6B"], [0.50, "#02A7B2"],
         [0.75, "#4FD5DF"], [1.00, "#A6EEF4"]]

# מתפצל (קוטביות): שני גוונים + אפור ניטרלי באמצע.
DIVERGING = [[0.00, "#FF3289"], [0.25, "#B35F86"], [0.50, "#6E6E86"],
             [0.75, "#2E8FA0"], [1.00, "#02A7B2"]]

FONTS = ("'Press Start 2P', 'Heebo', monospace")
HE_FONT = "'Heebo', 'Arial Hebrew', sans-serif"

CSS = f"""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&family=VT323&family=Heebo:wght@400;700;900&display=swap" rel="stylesheet">
<style>
:root {{
  --bg:{BG}; --card:{BG_CARD}; --cyan:{CYAN}; --mag:{MAGENTA};
  --yellow:{YELLOW}; --green:{GREEN}; --purple:{PURPLE}; --text:{TEXT}; --muted:{MUTED};
}}

/* ---------- בסיס + RTL ---------- */
html, body, .stApp, [data-testid="stAppViewContainer"] {{
  direction: rtl; text-align: right;
  background: {BG};
  color: {TEXT};
  font-family: {HE_FONT};
}}
.stApp {{
  background-image:
    radial-gradient(ellipse at 20% -10%, #1E1B4B 0%, transparent 55%),
    radial-gradient(ellipse at 85% 0%, #3B0F3F 0%, transparent 50%),
    linear-gradient(180deg, {BG} 0%, {BG_DEEP} 100%);
  background-attachment: fixed;
}}
* {{ border-radius: 0 !important; }}
img, canvas {{ image-rendering: pixelated; }}

/* ---------- סריקות CRT ---------- */
.stApp::after {{
  content: ""; position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  pointer-events: none; z-index: 9999; opacity: .30;
  background: repeating-linear-gradient(
    to bottom, rgba(0,0,0,.35) 0px, rgba(0,0,0,.35) 1px,
    transparent 1px, transparent 3px);
}}

/* ---------- טיפוגרפיה ---------- */
h1, h2, h3 {{ font-family: {HE_FONT}; font-weight: 900; color: {TEXT};
              letter-spacing: 0; text-shadow: 0 0 10px rgba(0,240,255,.45); }}
.px-en {{ font-family: {FONTS}; letter-spacing: 1px; }}
.px-num {{ font-family: 'VT323', monospace; font-weight: 400; }}

/* ---------- שלטי HUD ---------- */
.hud-card {{
  background: {BG_CARD};
  border: 3px solid var(--bc, {CYAN});
  box-shadow: 6px 6px 0 rgba(0,0,0,.65), inset 0 0 22px rgba(0,240,255,.07);
  padding: 14px 16px; height: 100%;
}}
.hud-label {{
  font-family: {FONTS}; font-size: 9px; color: {MUTED};
  letter-spacing: 1.5px; display: block; margin-bottom: 6px; direction: ltr; text-align: right;
}}
.hud-value {{
  font-family: 'VT323', monospace; font-size: 42px; line-height: .95;
  color: var(--bc, {CYAN}); text-shadow: 0 0 14px var(--bc, {CYAN}); direction: ltr; text-align: right;
}}
.hud-sub {{ font-size: 12px; color: {MUTED}; margin-top: 6px; font-weight: 700; }}

/* ---------- כרטיס תובנה ---------- */
.insight {{
  background: linear-gradient(90deg, rgba(255,211,0,.12), rgba(255,211,0,.02));
  border: 3px solid {YELLOW};
  border-right-width: 10px;
  box-shadow: 6px 6px 0 rgba(0,0,0,.6);
  padding: 14px 18px; margin: 6px 0 20px 0;
}}
.insight .tag {{
  font-family: {FONTS}; font-size: 9px; color: {YELLOW};
  letter-spacing: 1.5px; direction: ltr; text-align: right; display: block; margin-bottom: 8px;
}}
.insight .body {{ font-size: 16px; line-height: 1.75; color: {TEXT}; font-weight: 400; }}
.insight .body b {{ color: {YELLOW}; font-weight: 900; }}

/* ---------- הערה/הסבר ---------- */
.note {{
  border-right: 5px solid {PURPLE};
  background: rgba(155,92,255,.08);
  padding: 10px 14px; font-size: 14px; line-height: 1.7; color: {TEXT};
  margin: 4px 0 16px 0;
}}
.note b {{ color: {PURPLE}; }}

/* ---------- כותרת שלב ---------- */
.level-head {{
  border: 3px solid {MAGENTA};
  background: linear-gradient(90deg, rgba(255,46,136,.16), transparent);
  box-shadow: 6px 6px 0 rgba(0,0,0,.6);
  padding: 12px 18px; margin-bottom: 18px;
}}
.level-head .lv {{ font-family: {FONTS}; font-size: 10px; color: {MAGENTA};
                   letter-spacing: 2px; direction: ltr; text-align: right; display: block; }}
.level-head .ti {{ font-size: 26px; font-weight: 900; color: {TEXT}; margin-top: 8px;
                   text-shadow: 0 0 12px rgba(255,46,136,.5); }}

/* ---------- באנר עליון ---------- */
.marquee {{
  border: 4px solid {CYAN};
  box-shadow: 0 0 0 4px {BG}, 0 0 28px rgba(0,240,255,.35), 8px 8px 0 rgba(0,0,0,.6);
  background: linear-gradient(135deg, #16003B 0%, #2A0A4D 50%, #061A3D 100%);
  padding: 20px 24px; margin-bottom: 8px;
}}
.marquee .t1 {{ font-family: {FONTS}; font-size: 22px; color: {YELLOW};
                text-shadow: 3px 3px 0 {MAGENTA}, 0 0 24px rgba(255,211,0,.6);
                direction: ltr; text-align: right; line-height: 1.5; }}
.marquee .t2 {{ font-size: 15px; color: {CYAN}; margin-top: 12px; font-weight: 700; }}
.marquee .t3 {{ font-size: 13px; color: {MUTED}; margin-top: 4px; }}

/* ---------- מד פיקסלי ---------- */
.pxbar {{ font-family: 'VT323', monospace; font-size: 22px; letter-spacing: -1px;
          direction: ltr; text-align: right; line-height: 1.2; }}

/* ---------- טאבים כמחסניות ---------- */
[data-testid="stTabs"] [role="tablist"] {{ gap: 6px; border-bottom: 3px solid {GRID}; }}
[data-testid="stTabs"] [role="tab"] {{
  background: {BG_CARD}; border: 3px solid {GRID}; border-bottom: none;
  padding: 10px 16px; color: {MUTED};
  font-family: {HE_FONT}; font-weight: 700; font-size: 14px;
}}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {{
  background: linear-gradient(180deg, rgba(0,240,255,.18), rgba(0,240,255,.03));
  border-color: {CYAN}; color: {CYAN};
  box-shadow: 0 -4px 18px rgba(0,240,255,.25);
}}
[data-testid="stTabs"] [role="tab"] p {{ font-size: 14px !important; font-weight: 700; }}

/* ---------- בוחר השלבים (LEVEL SELECT) ---------- */
[data-testid="stMainBlockContainer"] [role="radiogroup"] {
  gap: 8px; flex-wrap: wrap; margin-bottom: 4px;
}
[data-testid="stMainBlockContainer"] [role="radiogroup"] > label {
  background: #141433; border: 3px solid #2A2A55;
  box-shadow: 4px 4px 0 rgba(0,0,0,.6);
  padding: 12px 18px; margin: 0; cursor: pointer;
  transition: transform .06s linear, border-color .1s linear;
}
[data-testid="stMainBlockContainer"] [role="radiogroup"] > label:hover {
  border-color: #9B5CFF; transform: translate(-1px, -1px);
}
[data-testid="stMainBlockContainer"] [role="radiogroup"] > label > div:first-child {
  display: none;   /* מסתיר את העיגול, נשארת "מחסנית" */
}
[data-testid="stMainBlockContainer"] [role="radiogroup"] > label p {
  font-size: 15px !important; font-weight: 700; color: #8C8CB8; margin: 0;
}
[data-testid="stMainBlockContainer"] [role="radiogroup"] > label:has(input:checked) {
  border-color: #00F0FF;
  background: linear-gradient(180deg, rgba(0,240,255,.20), rgba(0,240,255,.04));
  box-shadow: 4px 4px 0 rgba(0,0,0,.6), 0 0 22px rgba(0,240,255,.3);
}
[data-testid="stMainBlockContainer"] [role="radiogroup"] > label:has(input:checked) p {
  color: #00F0FF; font-weight: 900;
}

/* ---------- סיידבר ---------- */
[data-testid="stSidebar"] {{
  direction: rtl; background: {BG_DEEP}; border-left: 3px solid {GRID};
}}
[data-testid="stSidebar"] * {{ color: {TEXT}; }}
[data-testid="stSidebar"] h2 {{ font-size: 16px; }}

/* ---------- ווידג'טים ---------- */
.stButton > button {{
  background: linear-gradient(180deg, {MAGENTA}, #B31560);
  border: 3px solid {TEXT}; color: #FFF;
  font-family: {HE_FONT}; font-weight: 900; font-size: 16px;
  box-shadow: 5px 5px 0 rgba(0,0,0,.7); padding: 10px 20px; width: 100%;
  transition: transform .06s linear;
}}
.stButton > button:hover {{ background: linear-gradient(180deg, {YELLOW}, {ORANGE});
                            color: {BG}; border-color: {YELLOW}; }}
.stButton > button:active {{ transform: translate(5px, 5px); box-shadow: 0 0 0 rgba(0,0,0,0); }}
[data-testid="stMetricValue"] {{ font-family: 'VT323', monospace; color: {CYAN}; }}
[data-baseweb="select"] > div, .stNumberInput input, .stTextInput input {{
  background: {BG_CARD} !important; border: 2px solid {GRID} !important; color: {TEXT} !important;
}}
[data-baseweb="tag"] {{ background: {PURPLE} !important; }}
.stSlider [data-baseweb="slider"] div[role="slider"] {{
  background: {CYAN} !important; border: 2px solid {TEXT} !important; }}

/* ---------- טבלאות RTL ---------- */
[data-testid="stTable"] table, .stDataFrame {{ direction: rtl; }}
[data-testid="stTable"] table {{ width: 100%; border-collapse: collapse;
                                 border: 3px solid {GRID}; background: {BG_CARD}; }}
[data-testid="stTable"] th {{
  background: {BG_DEEP}; color: {CYAN}; font-weight: 900; font-size: 13px;
  text-align: right; padding: 10px 12px; border-bottom: 2px solid {GRID};
}}
[data-testid="stTable"] td {{
  color: {TEXT}; font-size: 14px; padding: 8px 12px;
  border-bottom: 1px solid {GRID}; text-align: right;
}}
/* מספרים מיושרים לשמאל בתוך התא, לפי כללי ה-RTL */
[data-testid="stTable"] td.num, .num {{
  text-align: left; direction: ltr; font-family: 'VT323', monospace; font-size: 19px;
}}

hr {{ border: none; border-top: 3px solid {GRID}; margin: 26px 0; }}
[data-testid="stHeader"] {{ background: transparent; }}
#MainMenu, footer {{ visibility: hidden; }}
.block-container {{ padding-top: 2.2rem; max-width: 1400px; }}
</style>
"""


def inject() -> None:
    # st.html ולא st.markdown: שורות ריקות בתוך <style> סוגרות את בלוק ה-HTML
    # של markdown, וכל שאר ה-CSS מודפס למסך כטקסט.
    st.html(CSS)


# ---------- רכיבי UI ----------
def marquee(title_en: str, subtitle: str, note: str) -> None:
    st.markdown(
        f'<div class="marquee"><div class="t1">{title_en}</div>'
        f'<div class="t2">{subtitle}</div><div class="t3">{note}</div></div>',
        unsafe_allow_html=True,
    )


def level_head(level_en: str, title_he: str) -> None:
    st.markdown(
        f'<div class="level-head"><span class="lv">{level_en}</span>'
        f'<div class="ti">{title_he}</div></div>',
        unsafe_allow_html=True,
    )


def hud(label_en: str, value: str, sub: str = "", color: str = CYAN) -> None:
    st.markdown(
        f'<div class="hud-card" style="--bc:{color}">'
        f'<span class="hud-label">{label_en}</span>'
        f'<div class="hud-value">{value}</div>'
        f'<div class="hud-sub">{sub}</div></div>',
        unsafe_allow_html=True,
    )


def insight(text_html: str, tag: str = "&gt; WHAT THE DATA SAYS") -> None:
    st.markdown(
        f'<div class="insight"><span class="tag">{tag}</span>'
        f'<div class="body">{text_html}</div></div>',
        unsafe_allow_html=True,
    )


def note(text_html: str) -> None:
    st.markdown(f'<div class="note">{text_html}</div>', unsafe_allow_html=True)


def pixel_bar(pct: float, blocks: int = 20, color: str = CYAN) -> str:
    """מד בריאות פיקסלי — מחזיר HTML."""
    pct = max(0.0, min(1.0, float(pct)))
    filled = round(pct * blocks)
    return (f'<span class="pxbar" style="color:{color}">{"█" * filled}'
            f'<span style="color:{GRID}">{"█" * (blocks - filled)}</span></span>')
