"""
Transformação final.

Responsável por:
- Unir consumo, demanda lida e demanda contratada
- Calcular ultrapassagem
- Retornar dataset pronto para o bot
"""

import pandas as pd


def calcular_ultrapassagem(lida, contratada):
    """Retorna 'SIM' se ultrapassou, senão 'NAO'."""
    if pd.isna(lida) or pd.isna(contratada):
        return "NAO"
    return "SIM" if lida > contratada else "NAO"


def transform_final(
    df_consumo: pd.DataFrame,
    df_demanda_lida: pd.DataFrame,
    df_demanda_contratada: pd.DataFrame
) -> pd.DataFrame:
    """
    Monta dataset final consolidado.

    :return: DataFrame final
    """

    # ✅ 1. Base = consumo
    df = df_consumo.copy()

    # ✅ 2. Merge demanda lida
    df = df.merge(
        df_demanda_lida,
        on=["INSTALACAO", "MES"],
        how="left"
    )

    # ✅ 3. Merge demanda contratada
    df = df.merge(
        df_demanda_contratada,
        on=["INSTALACAO", "MES"],
        how="left"
    )

    # ✅ 4. Garantir colunas existen
    cols_padrao = [
        "DEMANDA_LIDA_FP",
        "DEMANDA_LIDA_NP",
        "DEMANDA_LIDA_RESERVA",
        "DEMANDA_CONT_FP",
        "DEMANDA_CONT_NP",
        "DEMANDA_CONT_RESERVA"
    ]

    for col in cols_padrao:
        if col not in df.columns:
            df[col] = None

    # ✅ 5. Calcular ultrapassagem
    df["ULTRA_DEM_FP"] = df.apply(
        lambda x: calcular_ultrapassagem(
            x["DEMANDA_LIDA_FP"], x["DEMANDA_CONT_FP"]
        ),
        axis=1
    )

    df["ULTRA_DEM_NP"] = df.apply(
        lambda x: calcular_ultrapassagem(
            x["DEMANDA_LIDA_NP"], x["DEMANDA_CONT_NP"]
        ),
        axis=1
    )

    df["ULTRA_DEM_RES"] = df.apply(
        lambda x: calcular_ultrapassagem(
            x["DEMANDA_LIDA_RESERVA"], x["DEMANDA_CONT_RESERVA"]
        ),
        axis=1
    )

    # ✅ 6. Ordenar
    df = df.sort_values(
        by=["INSTALACAO", "MES"]
    )

    # ✅ 7. Reset index
    df = df.reset_index(drop=True)

    return df