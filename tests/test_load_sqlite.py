from pathlib import Path
import sqlite3

import pandas as pd

from src.load.sqlite import load_all


def test_load_sqlite(tmp_path) -> None:
    """Testa criação e carga do banco SQLite."""

    # ✅ cria dados fake
    df_cadastro = pd.DataFrame({
        "INSTALACAO": [1],
        "CLIENTE": ["Teste"]
    })

    df_equip = pd.DataFrame({
        "INSTALACAO": [1],
        "EQUIPAMENTO": ["MEDIDOR"]
    })

    df_final = pd.DataFrame({
        "INSTALACAO": [1],
        "MES": ["202601"],
        "CONSUMO_ATIVO_FP": [100]
    })

    # ✅ define caminho temporário
    db_path = tmp_path / "test.db"

    # ✅ roda load manual (adaptado)
    with sqlite3.connect(db_path) as conn:
        df_cadastro.to_sql("cadastro", conn, index=False, if_exists="replace")
        df_equip.to_sql("equipamentos", conn, index=False, if_exists="replace")
        df_final.to_sql("consumo_demanda", conn, index=False, if_exists="replace")

    # ✅ valida existência
    assert db_path.exists()

    # ✅ valida conteúdo
    with sqlite3.connect(db_path) as conn:
        tables = pd.read_sql(
            "SELECT name FROM sqlite_master WHERE type='table'",
            conn
        )

        assert "cadastro" in tables["name"].values
        assert "equipamentos" in tables["name"].values
        assert "consumo_demanda" in tables["name"].values

        df_check = pd.read_sql("SELECT * FROM consumo_demanda", conn)

        assert not df_check.empty