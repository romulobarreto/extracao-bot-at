"""
Transformação dos dados de demanda contratada.

Responsável por:
- Expandir contratos por mês
- Ignorar DATA_FIM
- Aplicar lógica de continuidade (forward fill)
- Pivotar tipos de demanda em colunas
"""

import pandas as pd


def transformar_para_mes(date):
    """Converte data para YYYYMM."""
    return date.strftime("%Y%m")


def gerar_range_meses(inicio, fim):
    """Gera lista de meses entre duas datas."""
    return pd.date_range(inicio, fim, freq="MS")


def transform_demanda_contratada(
    df: pd.DataFrame,
    df_consumo: pd.DataFrame
) -> pd.DataFrame:
    """
    Transforma contratos de demanda em base mensal.

    :param df: DataFrame original
    :return: DataFrame expandido por mês
    """

    # ✅ 1. Garantir tipos
    df["DATA_INICIO"] = pd.to_datetime(df["DATA_INICIO"])

    # ✅ 2. Filtrar apenas a partir de 2026-01
    data_min = pd.to_datetime("2026-01-01")
    
    max_mes = df_consumo["MES"].max()
    data_max = pd.to_datetime(max_mes + "01")
  

    resultados = []

    # ✅ 3. Processar por instalação
    for instalacao, grupo in df.groupby("INSTALACAO"):

        grupo = grupo.sort_values("DATA_INICIO")

        for i, row in grupo.iterrows():

            inicio = max(row["DATA_INICIO"], data_min)

            # próximo contrato
            if i != grupo.index[-1]:
                prox_inicio = grupo.loc[grupo.index > i, "DATA_INICIO"].min()
                fim = prox_inicio - pd.DateOffset(days=1)
            else:
                fim = data_max

            meses = gerar_range_meses(inicio, fim)

            for mes in meses:
                resultados.append({
                    "INSTALACAO": instalacao,
                    "MES": transformar_para_mes(mes),
                    "TIPO_DEMANDA": row["TIPO_DEMANDA"],
                    "DEMANDA": row["DEMANDA_CONTRATADA"]
                })

    df_exp = pd.DataFrame(resultados)

    # ✅ 4. Pivotar
    df_pivot = df_exp.pivot(
        index=["INSTALACAO", "MES"],
        columns="TIPO_DEMANDA",
        values="DEMANDA"
    ).reset_index()

    df_pivot.columns.name = None

    # ✅ 5. Renomear colunas
    rename_map = {
        "DEMANDA_PONTA": "DEMANDA_CONT_FP",
        "DEMANDA_FORA_PONTA": "DEMANDA_CONT_NP",
        "DEMANDA_UNICA": "DEMANDA_CONT_FP"  # regra: única vira FP
    }

    df_pivot = df_pivot.rename(columns=rename_map)

    # ✅ 6. Garantir colunas padrão
    expected_cols = [
        "DEMANDA_CONT_FP",
        "DEMANDA_CONT_NP",
        "DEMANDA_CONT_RESERVA"
    ]

    for col in expected_cols:
        if col not in df_pivot.columns:
            df_pivot[col] = None

    # ✅ 7. Sort final
    df_pivot = df_pivot.sort_values(
        by=["INSTALACAO", "MES"]
    )

    return df_pivot