"""מנוע תובנות — מחשב מהנתונים (pandas) ומנסח משפט עברי ברור."""
import numpy as np
import pandas as pd

import data as D

# עמודות שאין טעם להציג בניתוח קורלציות (מזהים / קודים)
CORR_EXCLUDE = {"Id", "MSSubClass", "MoSold", "YrSold", "Decade",
                "GarageYrBlt", "PricePerSF"}


def _m(v) -> str:
    return f"${v:,.0f}"


def price_corr(df: pd.DataFrame, k: int = 15) -> pd.Series:
    """k המשתנים המספריים עם הקשר החזק ביותר למחיר (בערך מוחלט)."""
    num = df.select_dtypes("number").drop(
        columns=[c for c in CORR_EXCLUDE if c in df.columns], errors="ignore")
    corr = num.corr(numeric_only=True)["SalePrice"].drop("SalePrice")
    corr = corr.dropna()
    return corr.reindex(corr.abs().sort_values(ascending=False).index).head(k)


def overview(df: pd.DataFrame) -> str:
    s = df["SalePrice"]
    med, mean = s.median(), s.mean()
    skew_pct = (mean / med - 1) * 100
    top10 = s.quantile(.9)
    share = s[s >= top10].sum() / s.sum() * 100
    return (
        f"בין {int(df['YrSold'].min())} ל-{int(df['YrSold'].max())} נמכרו כאן "
        f"<b>{len(df):,}</b> בתים. המחיר החציוני הוא <b>{_m(med)}</b>, אבל הממוצע "
        f"<b>{_m(mean)}</b> — גבוה ממנו ב-<b>{skew_pct:.0f}%</b>. "
        f"זה הסימן הקלאסי לשוק עם זנב עליון: מיעוט בתי יוקרה מושכים את הממוצע כלפי מעלה. "
        f"עשירון הבתים היקרים לבדו אחראי ל-<b>{share:.0f}%</b> מכלל כסף העסקאות. "
        f"המסקנה המעשית: החציון הוא המדד הנכון לתאר \"בית טיפוסי\", לא הממוצע."
    )


def neighborhoods(df: pd.DataFrame) -> str:
    agg = df.groupby("Neighborhood")["SalePrice"].agg(["count", "median"])
    agg = agg[agg["count"] >= 5]
    if agg.empty:
        return "אין מספיק עסקאות בשכונות שנבחרו כדי להשוות."
    top, bot = agg["median"].idxmax(), agg["median"].idxmin()
    ratio = agg["median"].max() / agg["median"].min()
    top5_share = agg.nlargest(5, "count")["count"].sum() / agg["count"].sum() * 100
    within = df.groupby("Neighborhood")["SalePrice"].agg(
        lambda x: x.quantile(.75) - x.quantile(.25)).median()
    return (
        f"המיקום הוא המשתנה היחיד שאי אפשר לשפץ. <b>{top}</b> היא השכונה היקרה "
        f"(חציון {_m(agg['median'].max())}), לעומת <b>{bot}</b> ({_m(agg['median'].min())}) — "
        f"פי <b>{ratio:.1f}</b> הבדל על אותו סוג מוצר. "
        f"אבל שימו לב לגרף הפיזור: הטווח הפנימי בתוך שכונה ממוצעת הוא כ-<b>{_m(within)}</b>, "
        f"כך שבית זול בשכונה יקרה יכול לעלות פחות מבית מעולה בשכונה בינונית. "
        f"5 השכונות הגדולות מרכזות <b>{top5_share:.0f}%</b> מהעסקאות."
    )


def drivers(df: pd.DataFrame) -> str:
    corr = price_corr(df, 6)
    top = corr.index[0]
    lines = " · ".join(f"{D.he(c)} ({v:+.2f})" for c, v in corr.head(3).items())
    r2 = corr.iloc[0] ** 2
    return (
        f"שלושת הגורמים הקשורים ביותר למחיר: <b>{lines}</b>. "
        f"המוביל הוא <b>{D.he(top)}</b> — הוא לבדו מסביר כ-<b>{r2 * 100:.0f}%</b> "
        f"מהשונות במחיר. "
        f"התמונה שמצטיירת פשוטה: <b>איכות הבנייה וגודל השטח</b> הם מנוע המחיר, "
        f"וכל השאר (מוסך, מרתף, אמבטיות) הוא במידה רבה נגזרת שלהם — בתים גדולים ואיכותיים "
        f"ממילא מגיעים עם יותר מהכול. שימו לב: קורלציה אינה סיבתיות."
    )


def anatomy(df: pd.DataFrame) -> str:
    q = df.groupby("OverallQual")["SalePrice"].median()
    if len(q) >= 2:
        lo, hi = q.index.min(), q.index.max()
        jump = q.loc[hi] / q.loc[lo]
        step_lo = q.diff().head(len(q) // 2).mean()
        step_hi = q.diff().tail(len(q) // 2).mean()
        accel = (step_hi / step_lo) if step_lo and step_lo > 0 else np.nan
    else:
        return "אין מספיק טווח איכות בנתונים שסוננו."
    by_year = df.groupby("YrSold")["SalePrice"].median()
    trend = (by_year.iloc[-1] / by_year.iloc[0] - 1) * 100 if len(by_year) > 1 else 0
    accel_txt = (f"כל נקודת איכות בקצה העליון שווה בערך פי <b>{accel:.1f}</b> "
                 f"מנקודת איכות בקצה התחתון. ") if np.isfinite(accel) else ""
    return (
        f"המעבר מציון איכות {int(lo)} לציון {int(hi)} מכפיל את המחיר החציוני פי "
        f"<b>{jump:.1f}</b>, והסולם אינו ליניארי — {accel_txt}"
        f"במקביל, המחיר החציוני בשוק כולו <b>{'ירד' if trend < 0 else 'עלה'} "
        f"ב-{abs(trend):.1f}%</b> בין {int(by_year.index[0])} ל-{int(by_year.index[-1])} — "
        f"בדיוק חלון הזמן של משבר הדיור בארה״ב."
    )


def feature_uplift(df: pd.DataFrame):
    """מחזיר רשימת (תווית, חציון עם, חציון בלי, אחוז תוספת)."""
    specs = [
        ("מיזוג אוויר מרכזי", df["CentralAir"] == "Y"),
        ("מרתף", df["TotalBsmtSF"] > 0),
        ("קמין", df["Fireplaces"] > 0),
        ("מוסך ל-2 רכבים ומעלה", df["GarageCars"] >= 2),
        ("קומה שנייה", df["2ndFlrSF"] > 0),
        ("שיפוץ ב-20 השנים האחרונות", df["RemodAge"] <= 20),
    ]
    rows = []
    for label, mask in specs:
        a, b = df.loc[mask, "SalePrice"], df.loc[~mask, "SalePrice"]
        if len(a) >= 10 and len(b) >= 10:
            rows.append((label, a.median(), b.median(),
                         (a.median() / b.median() - 1) * 100))
    return sorted(rows, key=lambda r: r[3], reverse=True)


def profiles(df: pd.DataFrame):
    """שלושה פרופילי בית מנורמלים ל-0..100 עבור תרשים הראדאר."""
    axes = ["GrLivArea", "OverallQual", "TotalBsmtSF",
            "GarageArea", "TotalBath", "YearBuilt"]
    axes_he = ["שטח מגורים", "איכות בנייה", "שטח מרתף",
               "שטח מוסך", "חדרי רחצה", "חדשנות הבית"]
    q1, q3 = df["SalePrice"].quantile([.25, .75])
    groups = {
        "רבעון תחתון": df[df["SalePrice"] <= q1],
        "אמצע השוק": df[(df["SalePrice"] > q1) & (df["SalePrice"] < q3)],
        "רבעון עליון": df[df["SalePrice"] >= q3],
    }
    lo = df[axes].quantile(.02)
    hi = df[axes].quantile(.98)
    out = {}
    for name, g in groups.items():
        if g.empty:
            continue
        med = g[axes].median()
        norm = ((med - lo) / (hi - lo) * 100).clip(0, 100)
        out[name] = norm.to_numpy()
    return out, axes_he


def outliers(df: pd.DataFrame) -> pd.DataFrame:
    """החריגים המפורסמים: בתים ענקיים שנמכרו זול (בנייה שלא הושלמה)."""
    return df[(df["GrLivArea"] > 4000) & (df["SalePrice"] < 300000)]
