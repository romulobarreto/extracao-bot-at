"""
Transformação dos dados de consumo.

Responsável por:
- Remover duplicidades
- Pivotar tipos de consumo em colunas
- Criar coluna de status de leitura
"""

import pandas as pd


def transform_consumo(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforma dados de consumo para formato consolidado por mês.

    :param df: DataFrame original de consumo
    :return: DataFrame transformado
    """

    # ✅ 1. Garantir tipos
    df["MES"] = df["MES"].astype(str)
    df["CONSUMO"] = pd.to_numeric(df["CONSUMO"], errors="coerce")

    # ✅ 2. Criar coluna de leitura
    df["LEITURA"] = df["NOTA_LEITURA"].apply(
        lambda x: "SIM" if x == "A01" else "NAO"
    )

    # ✅ 3. Remover duplicidade (ESSENCIAL)
    df = df.drop_duplicates(
        subset=["INSTALACAO", "MES", "TIPO_REGISTRO"],
        keep="first"
    )

    # ✅ 4. Pivotar consumo
    df_pivot = df.pivot(
        index=["INSTALACAO", "MES"],
        columns="TIPO_REGISTRO",
        values="CONSUMO"
    )

    # ✅ 5. Resetar índice
    df_pivot = df_pivot.reset_index()

    # ✅ 6. Ajustar nomes (remove nome do eixo)
    df_pivot.columns.name = None

    # ✅ 7. Garantir colunas mesmo se faltar dado
    for col in ["CONSUMO_ATIVO_FP", "CONSUMO_ATIVO_NP"]:
        if col not in df_pivot.columns:
            df_pivot[col] = None

    # ✅ 8. Recuperar leitura (por mês)
    leitura_df = (
        df.groupby(["INSTALACAO", "MES"])["LEITURA"]
        .max()  # SIM > NAO
        .reset_index()
    )

    # ✅ 9. Merge leitura
    df_final = df_pivot.merge(
        leitura_df,
        on=["INSTALACAO", "MES"],
        how="left"
    )

    # ✅ 10. Ordenação final
    df_final = df_final.sort_values(
        by=["INSTALACAO", "MES"]
    )

    return df_final