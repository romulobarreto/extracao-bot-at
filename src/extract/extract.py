"""
Módulo responsável pela extração de dados do Snowflake via ODBC.
"""

from pathlib import Path
from typing import Final

import pandas as pd
import pyodbc

SQL_DIR: Final[Path] = Path(__file__).parent.parent / "sql"
DSN_NAME: Final[str] = "Snowflake_EQTL"


def get_connection() -> pyodbc.Connection:
    """
    Cria e retorna uma conexão ODBC com o Snowflake.

    Utiliza autenticação via external browser.
    """
    connection_string = (
        f"DSN={DSN_NAME};"
        "authenticator=externalbrowser;"
        "CLIENT_SESSION_KEEP_ALIVE=true;"
    )

    return pyodbc.connect(
        connection_string,
        autocommit=True,
        timeout=120,
    )


def read_sql_file(sql_file_name: str) -> str:
    """Lê um arquivo SQL e retorna o conteúdo como string."""
    sql_path = SQL_DIR / sql_file_name

    if not sql_path.exists():
        raise FileNotFoundError(
            f"Arquivo SQL não encontrado: {sql_path.resolve()}"
        )

    return sql_path.read_text(encoding="utf-8")


def run_query(sql_file_name: str) -> pd.DataFrame:
    """
    Executa uma query SQL e retorna o resultado em DataFrame.

    O SQL é carregado a partir de um arquivo na pasta sql/.
    """
    query = read_sql_file(sql_file_name)

    print(f"[EXTRACT] Executando {sql_file_name}...")

    with get_connection() as connection:
        dataframe = pd.read_sql_query(query, connection)

    print(f"[EXTRACT] {sql_file_name} carregado ({len(dataframe)} linhas)")

    return dataframe


def extract_cadastro() -> pd.DataFrame:
    """Extrai os dados de cadastro de clientes."""
    return run_query("cadastro.sql")


def extract_equipamentos() -> pd.DataFrame:
    """Extrai os dados de equipamentos."""
    return run_query("equipamentos.sql")


def extract_consumo() -> pd.DataFrame:
    """Extrai os dados de consumo."""
    return run_query("consumo.sql")


def extract_demanda_lida() -> pd.DataFrame:
    """Extrai os dados de demanda lida."""
    return run_query("demanda/demanda_lida.sql")


def extract_demanda_contratada() -> pd.DataFrame:
    """Extrai os dados de demanda contratada."""
    return run_query("demanda/demanda_contratada.sql")