from src.transform.demanda_lida import transform_demanda_lida


def test_transform_demanda_lida() -> None:
    """Testa transformação de demanda lida."""

    import pandas as pd

    data = {
        "INSTALACAO": [1, 1],
        "MES": ["202601", "202601"],
        "TIPO_DEMANDA": ["DEMANDA_FP", "DEMANDA_NP"],
        "DEMANDA": [120, 80]
    }

    df = pd.DataFrame(data)

    result = transform_demanda_lida(df)

    assert not result.empty

    assert "DEMANDA_LIDA_FP" in result.columns
    assert "DEMANDA_LIDA_NP" in result.columns

