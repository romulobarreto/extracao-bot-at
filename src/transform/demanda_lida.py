"""
Transformação dos dados de demanda lida.

Responsável por:
- Remover duplicidades
- Pivotar tipos de demanda em colunas
"""

import pandas as pd


def transform_demanda_lida(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforma dados de demanda lida para formato consolidado por mês.

    :param df: DataFrame original de demanda lida
    :return: DataFrame transformado
    """

    # ✅ 1. Garantir tipos
    df["MES"] = df["MES"].astype(str)
    df["DEMANDA"] = pd.to_numeric(df["DEMANDA"], errors="coerce")

    # ✅ 2. Remover duplicidade
    df = df.drop_duplicates(
        subset=["INSTALACAO", "MES", "TIPO_DEMANDA"],
        keep="first"
    )

    # ✅ 3. Pivotar demanda
    df_pivot = df.pivot(
        index=["INSTALACAO", "MES"],
        columns="TIPO_DEMANDA",
        values="DEMANDA"
    )

    # ✅ 4. Resetar índice
    df_pivot = df_pivot.reset_index()

    # ✅ 5. Ajustar nome do eixo
    df_pivot.columns.name = None

    # ✅ 6. Renomear colunas
    rename_map = {
        "DEMANDA_FP": "DEMANDA_LIDA_FP",
        "DEMANDA_NP": "DEMANDA_LIDA_NP",
        "DEMANDA_RESERVA": "DEMANDA_LIDA_RESERVA"
    }

    df_pivot = df_pivot.rename(columns=rename_map)

    # ✅ 7. Garantir colunas padrão
    expected_cols = [
        "DEMANDA_LIDA_FP",
        "DEMANDA_LIDA_NP",
        "DEMANDA_LIDA_RESERVA"
    ]

    for col in expected_cols:
        if col not in df_pivot.columns:
            df_pivot[col] = None

    # ✅ 8. Ordenação final
    df_pivot = df_pivot.sort_values(
        by=["INSTALACAO", "MES"]
    )

    return df_pivot