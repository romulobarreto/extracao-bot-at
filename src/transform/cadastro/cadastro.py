import pandas as pd
from src.utils.clean import clean_key_column, clean_numeric_column


def transform_cadastro(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # =========================
    # 🔑 CHAVES
    # =========================
    df["INSTALACAO"] = clean_key_column(df["INSTALACAO"])
    df["MEDIDOR"] = clean_key_column(df["MEDIDOR"])

    # =========================
    # 🔢 NUMÉRICOS
    # =========================
    cols_numeric = ["ANO", "IRREG"]

    for col in cols_numeric:
        if col in df.columns:
            df[col] = clean_numeric_column(df[col])

    return df
