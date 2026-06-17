
"""
Transformação dos dados de demanda contratada.

Responsável por:
- Expandir contratos mês a mês
- Ignorar DATA_FIM completamente
- Aplicar forward fill baseado em DATA_INICIO
"""

import logging
import time
from datetime import datetime
import pandas as pd
from tqdm import tqdm

logger = logging.getLogger(__name__)


def gerar_calendario(mes_inicio: str, mes_fim: str) -> pd.DataFrame:
    inicio = pd.to_datetime(mes_inicio + "01")
    fim = pd.to_datetime(mes_fim + "01")

    meses = pd.date_range(inicio, fim, freq="MS")

    return pd.DataFrame({
        "MES": meses.strftime("%Y%m")
    })


def transform_demanda_contratada(
    df: pd.DataFrame,
    df_consumo: pd.DataFrame,
) -> pd.DataFrame:

    logger.info("[TRANSFORM][DEMANDA_CONT] Iniciando transformação...")
    start = time.time()

    # =========================
    # 1. Tipagem + limpeza
    # =========================
    df["DATA_INICIO"] = pd.to_datetime(df["DATA_INICIO"])
    df = df.dropna(subset=["DATA_INICIO"])

    logger.info(f"[DEMANDA_CONT] Linhas válidas: {len(df)}")

    # =========================
    # 2. Criar calendário
    # =========================
    mes_min = "202601" 
    mes_atual = datetime.now().strftime("%Y%m")
    mes_max = min(df_consumo["MES"].max(), mes_atual)


    calendario = gerar_calendario(mes_min, mes_max)

    resultados = []

    # =========================
    # 3. Loop por instalação
    # =========================
    logger.info("[DEMANDA_CONT] Aplicando forward fill por instalação...")

    for instalacao, grupo in tqdm(
        df.groupby("INSTALACAO"),
        desc="Processando instalações",
        unit="instalacao",
    ):

        grupo = grupo.sort_values("DATA_INICIO").copy()

        # converter DATA_INICIO -> MES
        grupo["MES"] = grupo["DATA_INICIO"].dt.strftime("%Y%m")

        grupo = grupo[
            ["INSTALACAO", "MES", "TIPO_DEMANDA", "DEMANDA_CONTRATADA"]
        ]

        # =========================
        # ✅ AQUI ESTÁ O AJUSTE CRÍTICO 🔥
        # =========================
        mes_inicio_calendario = calendario["MES"].min()

        contratos_anteriores = grupo[grupo["MES"] < mes_inicio_calendario]

        if not contratos_anteriores.empty:
            ultimo = contratos_anteriores.sort_values("MES").iloc[-1]

            grupo = pd.concat([
                grupo,
                pd.DataFrame([{
                    "INSTALACAO": ultimo["INSTALACAO"],
                    "MES": mes_inicio_calendario,
                    "TIPO_DEMANDA": ultimo["TIPO_DEMANDA"],
                    "DEMANDA_CONTRATADA": ultimo["DEMANDA_CONTRATADA"]
                }])
            ], ignore_index=True)

        # =========================
        # Base mensal
        # =========================
        base = calendario.copy()
        base["INSTALACAO"] = instalacao

        # merge com base mensal
        df_merge = base.merge(
            grupo,
            on=["INSTALACAO", "MES"],
            how="left"
        )

        # ordenar
        df_merge = df_merge.sort_values("MES")

        # forward fill
        df_merge["TIPO_DEMANDA"] = df_merge["TIPO_DEMANDA"].ffill()
        df_merge["DEMANDA_CONTRATADA"] = df_merge["DEMANDA_CONTRATADA"].ffill()

        resultados.append(df_merge)

    df_exp = pd.concat(resultados, ignore_index=True)

    logger.info(f"[DEMANDA_CONT] Linhas após expansão: {len(df_exp)}")

    # =========================
    # 4. Resolver duplicidade
    # =========================
    logger.info("[DEMANDA_CONT] Resolvendo duplicidades (max)...")

    df_exp = (
        df_exp.groupby(
            ["INSTALACAO", "MES", "TIPO_DEMANDA"],
            as_index=False
        )
        .agg({
            "DEMANDA_CONTRATADA": "max"
        })
    )

    # =========================
    # 5. Pivot
    # =========================
    logger.info("[DEMANDA_CONT] Pivotando dados...")

    df_pivot = df_exp.pivot_table(
        index=["INSTALACAO", "MES"],
        columns="TIPO_DEMANDA",
        values="DEMANDA_CONTRATADA",
        aggfunc="max"
    ).reset_index()

    df_pivot.columns.name = None

    logger.info(f"[DEMANDA_CONT] Linhas após pivot: {len(df_pivot)}")

    # =========================
    # 6. Renomear colunas
    # =========================
    rename_map = {
        "DEMANDA_PONTA": "DEMANDA_CONT_FP",
        "DEMANDA_FORA_PONTA": "DEMANDA_CONT_NP",
        "DEMANDA_UNICA": "DEMANDA_CONT_FP",
    }

    df_pivot = df_pivot.rename(columns=rename_map)

    # =========================
    # 7. Garantir colunas padrão
    # =========================
    expected_cols = [
        "DEMANDA_CONT_FP",
        "DEMANDA_CONT_NP",
        "DEMANDA_CONT_RESERVA",
    ]

    for col in expected_cols:
        if col not in df_pivot.columns:
            df_pivot[col] = None

    # =========================
    # 8. Final
    # =========================
    df_final = df_pivot.sort_values(
        by=["INSTALACAO", "MES"]
    ).reset_index(drop=True)

    elapsed = round(time.time() - start, 2)

    logger.info(
        f"[TRANSFORM][DEMANDA_CONT] Finalizado com {len(df_final)} linhas em {elapsed}s"
    )

    return df_final