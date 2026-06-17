import pandas as pd
from src.utils.clean import clean_key_column, clean_numeric_column


def transform_equipamentos(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # =========================
    # 🔑 CHAVES
    # =========================
    df["INSTALACAO"] = clean_key_column(df["INSTALACAO"])

    # =========================
    # 🔢 NUMÉRICOS
    # =========================
    cols_numeric = [
        "NUM_EQUIPAMENTO",
        "ANO",
        "PRIM_CORRENTE",
        "SEC_CORRENTE",
        "PRIM_TENSAO",
        "SEC_TENSAO",
    ]

    for col in cols_numeric:
        if col in df.columns:
            df[col] = clean_numeric_column(df[col])

    return df
