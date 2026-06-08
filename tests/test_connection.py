"""
Testa a conexão ODBC com o Snowflake.
"""

import pyodbc


def get_connection() -> pyodbc.Connection:
    """Cria e retorna uma conexão ODBC com o Snowflake."""
    connection_string = (
        "DSN=Snowflake_EQTL;"
        "authenticator=externalbrowser;"
    )

    return pyodbc.connect(
        connection_string,
        autocommit=True,
    )


def test_connection() -> None:
    """Valida a conexão executando uma query simples."""
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            CURRENT_USER(),
            CURRENT_ROLE(),
            CURRENT_WAREHOUSE()
        """
    )

    result = cursor.fetchone()

    assert result is not None

    cursor.close()
    connection.close()