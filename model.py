"""מודל ניבוי מחיר — Gradient Boosting על פיצ'רים נבחרים."""
import numpy as np
import pandas as pd
import streamlit as st
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

NUM_FEATURES = ["GrLivArea", "OverallQual", "OverallCond", "TotalBsmtSF",
                "GarageCars", "TotalBath", "YearBuilt", "YearRemodAdd",
                "LotArea", "Fireplaces", "BedroomAbvGr", "TotRmsAbvGrd"]


@st.cache_resource(show_spinner="מאמן את המודל...")
def train(_df: pd.DataFrame):
    """מאמן על כל הדאטה (בלי החריגים הידועים) ומחזיר מודל + מדדי דיוק."""
    df = _df[~((_df["GrLivArea"] > 4000) & (_df["SalePrice"] < 300000))]
    X = pd.get_dummies(
        df[NUM_FEATURES + ["Neighborhood", "CentralAir"]],
        columns=["Neighborhood", "CentralAir"], dtype=float)
    y = np.log(df["SalePrice"])

    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=.2, random_state=42)
    model = GradientBoostingRegressor(
        n_estimators=400, learning_rate=.05, max_depth=3,
        subsample=.9, random_state=42)
    model.fit(Xtr, ytr)

    pred = np.exp(model.predict(Xte))
    truth = np.exp(yte)
    metrics = {
        "r2": r2_score(truth, pred),
        "mae": mean_absolute_error(truth, pred),
        "mape": float(np.mean(np.abs(pred - truth) / truth) * 100),
        "n_train": len(Xtr),
        "n_test": len(Xte),
    }
    importances = pd.Series(model.feature_importances_, index=X.columns)
    return model, list(X.columns), metrics, importances


def build_row(columns, values: dict, neighborhood: str, central_air: str) -> pd.DataFrame:
    """בונה שורת קלט אחת בפורמט שהמודל אומן עליו."""
    row = pd.DataFrame(0.0, index=[0], columns=columns)
    for k, v in values.items():
        if k in row.columns:
            row.at[0, k] = float(v)
    for col, val in [(f"Neighborhood_{neighborhood}", 1.0),
                     (f"CentralAir_{central_air}", 1.0)]:
        if col in row.columns:
            row.at[0, col] = val
    return row


def predict(model, row: pd.DataFrame) -> float:
    return float(np.exp(model.predict(row)[0]))


def contributions(model, columns, values: dict, neighborhood: str,
                  central_air: str, baseline: dict) -> list:
    """תרומה בדולרים לכל פיצ'ר: כמה משתנה התחזית כשמחליפים אותו בערך הבסיס."""
    full = build_row(columns, values, neighborhood, central_air)
    base_pred = predict(model, full)
    out = []
    for k, v in values.items():
        if k not in baseline:
            continue
        alt = values.copy()
        alt[k] = baseline[k]
        out.append((k, base_pred - predict(
            model, build_row(columns, alt, neighborhood, central_air))))
    alt_row = build_row(columns, values, "NAmes", central_air)
    out.append(("Neighborhood", base_pred - predict(model, alt_row)))
    return out
