"""
Módulo responsável por salvar dados em SQLite.
"""

from pathlib import Path
import sqlite3
import time
import logging

import pandas as pd

logger = logging.getLogger(__name__)

OUTPUT_DIR = Path(__file__).parent.parent.parent / "output"
DB_PATH = OUTPUT_DIR / "bot_at.db"


def ensure_output_dir() -> None:
    """Garante que a pasta output exista."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def create_connection() -> sqlite3.Connection:
    """Cria conexão com banco SQLite."""
    return sqlite3.connect(DB_PATH)


def load_dataframe(df: pd.DataFrame, table_name: str) -> None:
    """
    Salva um DataFrame em uma tabela SQLite.

    :param df: DataFrame
    :param table_name: Nome da tabela
    """

    logger.info(
        f"[LOAD] Salvando tabela '{table_name}' com {len(df)} linhas..."
    )

    start = time.time()

    with create_connection() as conn:
        df.to_sql(
            table_name,
            conn,
            if_exists="replace",  # recria sempre
            index=False
        )

    elapsed = round(time.time() - start, 2)

    logger.info(
        f"[LOAD] Tabela '{table_name}' salva em {elapsed}s"
    )


def load_all(
    df_cadastro: pd.DataFrame,
    df_equipamentos: pd.DataFrame,
    df_final: pd.DataFrame
) -> None:
    """
    Faz carga completa no SQLite.

    :param df_cadastro: cadastro
    :param df_equipamentos: equipamentos
    :param df_final: dados finais consumo + demanda
    """

    logger.info("[LOAD] Iniciando carga no SQLite...")

    start = time.time()

    ensure_output_dir()

    logger.info(f"[LOAD] Diretório de saída: {OUTPUT_DIR}")
    logger.info(f"[LOAD] Banco alvo: {DB_PATH}")

    # =========================
    # 1. Cadastro
    # =========================
    load_dataframe(df_cadastro, "cadastro")

    # =========================
    # 2. Equipamentos
    # =========================
    load_dataframe(df_equipamentos, "equipamentos")

    # =========================
    # 3. Consumo + Demanda
    # =========================
    load_dataframe(df_final, "consumo_demanda")

    elapsed = round(time.time() - start, 2)

    logger.info(
        f"[LOAD] Carga finalizada com sucesso em {elapsed}s"
    )