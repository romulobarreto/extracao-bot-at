"""
Transformação dos dados de demanda lida.

Responsável por:
- Resolver duplicidades escolhendo a MAIOR demanda
- Pivotar tipos de demanda em colunas
"""

import logging
import time
import pandas as pd

logger = logging.getLogger(__name__)


def transform_demanda_lida(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforma dados de demanda lida para formato consolidado por mês.
    """

    logger.info("[TRANSFORM][DEMANDA_LIDA] Iniciando transformação...")

    start = time.time()

    # =========================
    # 1. Tipagem
    # =========================
    logger.info("[DEMANDA_LIDA] Ajustando tipos...")

    df["MES"] = df["MES"].astype(str)
    df["DEMANDA"] = pd.to_numeric(df["DEMANDA"], errors="coerce")

    logger.info(f"[DEMANDA_LIDA] Linhas iniciais: {len(df)}")

    # =========================
    # ✅ 2. RESOLVER DUPLICIDADE CORRETAMENTE
    # =========================
    logger.info("[DEMANDA_LIDA] Consolidando duplicidades (pegando MAIOR demanda)...")

    before = len(df)

    df = (
        df.groupby(["INSTALACAO", "MES", "TIPO_DEMANDA"], as_index=False)
        .agg({
            "DEMANDA": "max"  # ✅ regra de negócio
        })
    )

    after = len(df)

    logger.info(f"[DEMANDA_LIDA] Linhas após consolidação: {after} (antes: {before})")

    # =========================
    # 3. Pivot
    # =========================
    logger.info("[DEMANDA_LIDA] Pivotando dados...")

    df_pivot = df.pivot_table(
        index=["INSTALACAO", "MES"],
        columns="TIPO_DEMANDA",
        values="DEMANDA",
        aggfunc="max"  # segurança extra
    ).reset_index()

    df_pivot.columns.name = None

    logger.info(f"[DEMANDA_LIDA] Linhas após pivot: {len(df_pivot)}")

    # =========================
    # 4. Renomear colunas
    # =========================
    rename_map = {
        "DEMANDA_FP": "DEMANDA_LIDA_FP",
        "DEMANDA_NP": "DEMANDA_LIDA_NP",
        "DEMANDA_RESERVA": "DEMANDA_LIDA_RESERVA"
    }

    df_pivot = df_pivot.rename(columns=rename_map)

    # =========================
    # 5. Garantir colunas padrão
    # =========================
    logger.info("[DEMANDA_LIDA] Garantindo colunas padrão...")

    expected_cols = [
        "DEMANDA_LIDA_FP",
        "DEMANDA_LIDA_NP",
        "DEMANDA_LIDA_RESERVA"
    ]

    for col in expected_cols:
        if col not in df_pivot.columns:
            df_pivot[col] = None

    # =========================
    # 6. Ordenação final
    # =========================
    df_final = df_pivot.sort_values(
        by=["INSTALACAO", "MES"]
    ).reset_index(drop=True)

    elapsed = round(time.time() - start, 2)

    logger.info(
        f"[TRANSFORM][DEMANDA_LIDA] Finalizado com "
        f"{len(df_final)} linhas em {elapsed}s"
    )

    return df_final
