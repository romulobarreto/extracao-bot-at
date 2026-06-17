"""
Transformação final.

Responsável por:
- Construir base completa (instalação x mês)
- Unir consumo, demanda lida e demanda contratada
- Calcular ultrapassagem
"""

import logging
import time
from datetime import datetime
import pandas as pd
from src.utils.clean import clean_key_column

logger = logging.getLogger(__name__)


def gerar_calendario(mes_inicio: str, mes_fim: str) -> pd.DataFrame:
    inicio = pd.to_datetime(mes_inicio + "01")
    fim = pd.to_datetime(mes_fim + "01")

    meses = pd.date_range(inicio, fim, freq="MS")

    return pd.DataFrame({"MES": meses.strftime("%Y%m")})


def transform_final(
    df_cadastro: pd.DataFrame,
    df_consumo: pd.DataFrame,
    df_demanda_lida: pd.DataFrame,
    df_demanda_contratada: pd.DataFrame,
) -> pd.DataFrame:

    logger.info("[TRANSFORM][FINAL] Iniciando consolidação...")
    start = time.time()


    # =========================
    # 🔥 PADRONIZAR CHAVES
    # =========================

    
    df_cadastro["INSTALACAO"] = clean_key_column(df_cadastro["INSTALACAO"])
    df_consumo["INSTALACAO"] = clean_key_column(df_consumo["INSTALACAO"])
    df_demanda_lida["INSTALACAO"] = clean_key_column(df_demanda_lida["INSTALACAO"])
    df_demanda_contratada["INSTALACAO"] = clean_key_column(df_demanda_contratada["INSTALACAO"])


    df_consumo["MES"] = df_consumo["MES"].astype(str)
    df_demanda_lida["MES"] = df_demanda_lida["MES"].astype(str)
    df_demanda_contratada["MES"] = df_demanda_contratada["MES"].astype(str)
    


    # =========================
    # 1. BASE COMPLETA
    # =========================
    logger.info("[FINAL] Construindo base completa...")

    instalacoes = df_cadastro["INSTALACAO"].dropna().unique()
    mes_min = "202601"
    
    df_consumo["MES"] = df_consumo["MES"].astype(str)

    mes_atual = datetime.now().strftime("%Y%m")

    mes_max = min(df_consumo["MES"].max(), mes_atual)


    calendario = gerar_calendario(mes_min, mes_max)
    base = pd.DataFrame({"INSTALACAO": instalacoes}).merge(calendario, how="cross")

    logger.info(f"[FINAL] Linhas base: {len(base)}")

    # =========================
    # 2. MERGES (CONTROLADOS)
    # =========================
    logger.info("[FINAL] Merge consumo...")
    base = base.merge(df_consumo, on=["INSTALACAO", "MES"], how="left")

    logger.info("[FINAL] Merge demanda lida...")
    base = base.merge(df_demanda_lida, on=["INSTALACAO", "MES"], how="left")

    logger.info("[FINAL] Merge demanda contratada...")
    base = base.merge(df_demanda_contratada, on=["INSTALACAO", "MES"], how="left")

    # =========================
    # ✅ CRÍTICO: LIMPAR COLUNAS DUPLICADAS
    # =========================
    logger.info("[FINAL] Removendo colunas duplicadas...")
    base = base.loc[:, ~base.columns.duplicated()]

    # =========================
    # 3. GARANTIR COLUNAS
    # =========================
    cols = [
        "CONSUMO_ATIVO_FP",
        "CONSUMO_ATIVO_NP",
        "DEMANDA_LIDA_FP",
        "DEMANDA_LIDA_NP",
        "DEMANDA_LIDA_RESERVA",
        "DEMANDA_CONT_FP",
        "DEMANDA_CONT_NP",
        "DEMANDA_CONT_RESERVA",
    ]

    for col in cols:
        if col not in base.columns:
            base[col] = None

    # =========================
    # 4. TIPAGEM (SIMPLES E ROBUSTA)
    # =========================
    logger.info("[FINAL] Convertendo para numérico...")

    for col in cols:
        base[col] = pd.to_numeric(base[col], errors="coerce")

    # =========================
    # 5. ULTRAPASSAGEM (SEM FRESCURA ✅)
    # =========================
    logger.info("[FINAL] Calculando ultrapassagem...")

    base["ULTRA_DEM_FP"] = "NAO"
    base["ULTRA_DEM_NP"] = "NAO"
    base["ULTRA_DEM_RES"] = "NAO"

    base.loc[
        base["DEMANDA_LIDA_FP"] > base["DEMANDA_CONT_FP"],
        "ULTRA_DEM_FP"
    ] = "SIM"

    base.loc[
        base["DEMANDA_LIDA_NP"] > base["DEMANDA_CONT_NP"],
        "ULTRA_DEM_NP"
    ] = "SIM"

    base.loc[
        base["DEMANDA_LIDA_RESERVA"] > base["DEMANDA_CONT_RESERVA"],
        "ULTRA_DEM_RES"
    ] = "SIM"

    # =========================
    # 6. FINAL
    # =========================
    base = base.sort_values(["INSTALACAO", "MES"]).reset_index(drop=True)

    elapsed = round(time.time() - start, 2)

    logger.info(f"[TRANSFORM][FINAL] OK | {len(base)} linhas | {elapsed}s")

    return base