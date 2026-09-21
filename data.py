"""שכבת נתונים — טעינה, ניקוי ופיצ'רים נגזרים (pandas)."""
from pathlib import Path

import pandas as pd
import streamlit as st

DATA_PATH = Path(__file__).parent / "data" / "ames.csv"

# עמודות שבהן "NA" בקובץ המקור פירושו "אין תכונה כזו" ולא "נתון חסר"
NONE_MEANS_ABSENT = [
    "Alley", "BsmtQual", "BsmtCond", "BsmtExposure", "BsmtFinType1", "BsmtFinType2",
    "FireplaceQu", "GarageType", "GarageFinish", "GarageQual", "GarageCond",
    "PoolQC", "Fence", "MiscFeature", "MasVnrType",
]

# תרגום עברי לשמות עמודות שמוצגים למשתמש
HE = {
    "SalePrice": "מחיר מכירה",
    "GrLivArea": "שטח מגורים (רגל״ר)",
    "OverallQual": "ציון איכות כללי",
    "OverallCond": "ציון מצב כללי",
    "GarageCars": "מקומות חניה",
    "GarageArea": "שטח מוסך",
    "TotalBsmtSF": "שטח מרתף",
    "1stFlrSF": "שטח קומה ראשונה",
    "2ndFlrSF": "שטח קומה שנייה",
    "FullBath": "חדרי אמבט מלאים",
    "HalfBath": "חדרי שירותים",
    "TotRmsAbvGrd": "סך חדרים מעל הקרקע",
    "BedroomAbvGr": "חדרי שינה",
    "YearBuilt": "שנת בנייה",
    "YearRemodAdd": "שנת שיפוץ",
    "GarageYrBlt": "שנת בניית מוסך",
    "Fireplaces": "אחים (קמינים)",
    "LotArea": "שטח מגרש",
    "LotFrontage": "חזית מגרש",
    "MasVnrArea": "חיפוי אבן",
    "WoodDeckSF": "דק עץ",
    "OpenPorchSF": "מרפסת פתוחה",
    "EnclosedPorch": "מרפסת סגורה",
    "ScreenPorch": "מרפסת רשת",
    "PoolArea": "שטח בריכה",
    "MoSold": "חודש מכירה",
    "YrSold": "שנת מכירה",
    "KitchenAbvGr": "מטבחים",
    "MSSubClass": "קוד סוג נכס",
    "BsmtFullBath": "אמבט מלא במרתף",
    "BsmtHalfBath": "שירותים במרתף",
    "BsmtFinSF1": "מרתף גמור א׳",
    "BsmtFinSF2": "מרתף גמור ב׳",
    "BsmtUnfSF": "מרתף לא גמור",
    "LowQualFinSF": "גמר באיכות נמוכה",
    "3SsnPorch": "מרפסת 3 עונות",
    "MiscVal": "שווי תוספות",
    "TotalSF": "שטח בנוי כולל",
    "HouseAge": "גיל הבית במכירה",
    "TotalBath": "סך חדרי רחצה",
    "PricePerSF": "מחיר לרגל״ר",
    "RemodAge": "שנים מאז שיפוץ",
    "Neighborhood": "שכונה",
    "HouseStyle": "סגנון הבית",
    "SaleCondition": "סוג העסקה",
    "CentralAir": "מיזוג מרכזי",
    "PoolQC": "איכות בריכה",
    "MiscFeature": "תוספת מיוחדת",
    "Alley": "גישה מסמטה",
    "Fence": "גדר",
    "FireplaceQu": "איכות הקמין",
    "GarageType": "סוג מוסך",
    "GarageFinish": "גמר מוסך",
    "GarageQual": "איכות מוסך",
    "GarageCond": "מצב מוסך",
    "BsmtQual": "איכות מרתף",
    "BsmtCond": "מצב מרתף",
    "BsmtExposure": "חשיפת מרתף",
    "BsmtFinType1": "גמר מרתף א׳",
    "BsmtFinType2": "גמר מרתף ב׳",
    "Electrical": "מערכת חשמל",
    "MasVnrType": "סוג חיפוי אבן",
    "BldgType": "סוג מבנה",
}

# תרגום ערכים קטגוריים נפוצים
SALE_COND_HE = {
    "Normal": "מכירה רגילה",
    "Partial": "בנייה לא הושלמה",
    "Abnorml": "מכירה חריגה",
    "Family": "מכירה במשפחה",
    "Alloca": "הקצאה",
    "AdjLand": "קרקע צמודה",
}
HOUSE_STYLE_HE = {
    "1Story": "קומה אחת",
    "2Story": "שתי קומות",
    "1.5Fin": "קומה וחצי (גמור)",
    "1.5Unf": "קומה וחצי (לא גמור)",
    "SLvl": "מפלסים מפוצלים",
    "SFoyer": "כניסה מפוצלת",
    "2.5Unf": "2.5 קומות (לא גמור)",
    "2.5Fin": "2.5 קומות (גמור)",
}
YESNO_HE = {"Y": "יש", "N": "אין"}


def he(col: str) -> str:
    """שם עברי לעמודה, עם נפילה לשם המקורי."""
    return HE.get(col, col)


@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    """טוען את הקובץ, מנקה ומוסיף פיצ'רים נגזרים."""
    df = pd.read_csv(DATA_PATH, keep_default_na=True)

    # "NA" = אין תכונה כזו
    for col in NONE_MEANS_ABSENT:
        if col in df.columns:
            df[col] = df[col].astype("object").fillna("None")

    # חוסרים מספריים אמיתיים
    df["LotFrontage"] = df["LotFrontage"].fillna(df["LotFrontage"].median())
    df["MasVnrArea"] = df["MasVnrArea"].fillna(0)
    df["GarageYrBlt"] = df["GarageYrBlt"].fillna(df["YearBuilt"])
    if df["Electrical"].isna().any():
        df["Electrical"] = df["Electrical"].fillna(df["Electrical"].mode()[0])

    # פיצ'רים נגזרים
    df["TotalSF"] = df["TotalBsmtSF"] + df["1stFlrSF"] + df["2ndFlrSF"]
    df["TotalBath"] = (
        df["FullBath"] + 0.5 * df["HalfBath"]
        + df["BsmtFullBath"] + 0.5 * df["BsmtHalfBath"]
    )
    df["HouseAge"] = (df["YrSold"] - df["YearBuilt"]).clip(lower=0)
    df["RemodAge"] = (df["YrSold"] - df["YearRemodAdd"]).clip(lower=0)
    df["PricePerSF"] = df["SalePrice"] / df["GrLivArea"]
    df["Decade"] = (df["YearBuilt"] // 10 * 10).astype(int)
    df["SaleCondHe"] = df["SaleCondition"].map(SALE_COND_HE).fillna(df["SaleCondition"])
    df["HouseStyleHe"] = df["HouseStyle"].map(HOUSE_STYLE_HE).fillna(df["HouseStyle"])
    df["CentralAirHe"] = df["CentralAir"].map(YESNO_HE).fillna(df["CentralAir"])

    return df


@st.cache_data(show_spinner=False)
def raw_missing() -> pd.DataFrame:
    """דוח חוסרים על הקובץ הגולמי, לפני הניקוי."""
    raw = pd.read_csv(DATA_PATH)
    miss = raw.isna().sum()
    miss = miss[miss > 0].sort_values(ascending=False)
    out = pd.DataFrame({
        "עמודה": miss.index,
        "חסרים": miss.to_numpy(),
        "אחוז": (miss.to_numpy() / len(raw) * 100).round(1),
    })
    out["משמעות"] = [
        "אין תכונה כזו בנכס" if c in NONE_MEANS_ABSENT else "נתון חסר אמיתי"
        for c in out["עמודה"]
    ]
    out["שם עברי"] = [HE.get(c, c) for c in out["עמודה"]]
    return out


def apply_filters(df: pd.DataFrame, price_range, neighborhoods,
                  year_range, sale_conditions) -> pd.DataFrame:
    """מסנן את הדאטהפריים לפי בחירות הסיידבר."""
    mask = (
        df["SalePrice"].between(*price_range)
        & df["YearBuilt"].between(*year_range)
    )
    if neighborhoods:
        mask &= df["Neighborhood"].isin(neighborhoods)
    if sale_conditions:
        mask &= df["SaleCondition"].isin(sale_conditions)
    return df[mask]
