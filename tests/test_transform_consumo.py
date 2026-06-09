from src.transform.consumo import transform_consumo


def test_transform_consumo() -> None:
    """Testa transformação de consumo."""

    import pandas as pd

    data = {
        "INSTALACAO": [1, 1],
        "MES": ["202601", "202601"],
        "TIPO_REGISTRO": ["CONSUMO_ATIVO_FP", "CONSUMO_ATIVO_NP"],
        "CONSUMO": [100, 50],
        "NOTA_LEITURA": ["A01", "A01"]
    }

    df = pd.DataFrame(data)

    result = transform_consumo(df)

    # ✅ não vazio
    assert not result.empty

    # ✅ colunas existentes
    assert "CONSUMO_ATIVO_FP" in result.columns
    assert "CONSUMO_ATIVO_NP" in result.columns
    assert "LEITURA" in result.columns

    # ✅ valores corretos
    assert result.iloc[0]["CONSUMO_ATIVO_FP"] == 100
    assert result.iloc[0]["CONSUMO_ATIVO_NP"] == 50

    # ✅ leitura correta
    assert result.iloc[0]["LEITURA"] == "SIM"