"""
Transformação dos dados de consumo.

Responsável por:
- Resolver duplicidades escolhendo o MAIOR consumo
- Pivotar tipos de consumo em colunas
- Criar coluna de status de leitura
"""

import logging
import time
import pandas as pd

logger = logging.getLogger(__name__)


def transform_consumo(df: pd.DataFrame) -> pd.DataFrame:

    logger.info("[TRANSFORM][CONSUMO] Iniciando transformação...")

    start = time.time()

    # =========================
    # 1. Tipagem
    # =========================
    logger.info("[CONSUMO] Ajustando tipos...")

    df["MES"] = df["MES"].astype(str)
    df["CONSUMO"] = pd.to_numeric(df["CONSUMO"], errors="coerce")

    logger.info(f"[CONSUMO] Linhas iniciais: {len(df)}")

    # =========================
    # 2. Criar leitura
    # =========================
    logger.info("[CONSUMO] Criando coluna LEITURA...")

    df["LEITURA"] = df["NOTA_LEITURA"].apply(
        lambda x: "SIM" if x == "A01" else "NAO"
    )

    # =========================
    # ✅ 3. RESOLVER DUPLICIDADE CORRETAMENTE
    # =========================
    logger.info("[CONSUMO] Consolidando duplicidades (pegando MAIOR consumo)...")

    before = len(df)

    df = (
        df.groupby(["INSTALACAO", "MES", "TIPO_REGISTRO"], as_index=False)
        .agg({
            "CONSUMO": "max",      # ✅ pega o maior valor
            "LEITURA": "max"       # ✅ se tiver pelo menos um SIM, vira SIM
        })
    )

    after = len(df)

    logger.info(f"[CONSUMO] Linhas após consolidação: {after} (antes: {before})")

    # =========================
    # 4. Pivot
    # =========================
    logger.info("[CONSUMO] Pivotando dados...")

    df_pivot = df.pivot_table(
        index=["INSTALACAO", "MES"],
        columns="TIPO_REGISTRO",
        values="CONSUMO",
        aggfunc="max"  # segurança extra
    ).reset_index()

    df_pivot.columns.name = None

    logger.info(f"[CONSUMO] Linhas após pivot: {len(df_pivot)}")

    # =========================
    # 5. Garantir colunas
    # =========================
    logger.info("[CONSUMO] Garantindo colunas padrão...")

    for col in ["CONSUMO_ATIVO_FP", "CONSUMO_ATIVO_NP"]:
        if col not in df_pivot.columns:
            df_pivot[col] = None

    # =========================
    # 6. Leitura final por mês
    # =========================
    logger.info("[CONSUMO] Consolidando leitura...")

    leitura_df = (
        df.groupby(["INSTALACAO", "MES"])["LEITURA"]
        .max()
        .reset_index()
    )

    # =========================
    # 7. Merge leitura
    # =========================
    df_final = df_pivot.merge(
        leitura_df,
        on=["INSTALACAO", "MES"],
        how="left"
    )

    # =========================
    # 8. Ordenação
    # =========================
    df_final = df_final.sort_values(
        by=["INSTALACAO", "MES"]
    ).reset_index(drop=True)

    elapsed = round(time.time() - start, 2)

    logger.info(
        f"[TRANSFORM][CONSUMO] Finalizado com {len(df_final)} linhas em {elapsed}s"
    )

    return df_final