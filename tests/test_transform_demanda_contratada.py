from src.transform.consumo_demanda.demanda_contratada import transform_demanda_contratada
from src.transform.consumo_demanda.consumo import transform_consumo


def test_transform_demanda_contratada() -> None:
    """Testa expansão e consistência da demanda contratada."""

    import pandas as pd

    # ✅ consumo define o range de meses (202601 até 202603)
    consumo_data = {
        "INSTALACAO": [1, 1, 1],
        "MES": ["202601", "202602", "202603"],
        "TIPO_REGISTRO": ["CONSUMO_ATIVO_FP", "CONSUMO_ATIVO_FP", "CONSUMO_ATIVO_FP"],
        "CONSUMO": [100, 200, 300],
        "NOTA_LEITURA": ["A01", "A01", "A01"]
    }

    df_consumo = transform_consumo(pd.DataFrame(consumo_data))

    # ✅ dois contratos (mudança no meio)
    data = {
        "INSTALACAO": [1, 1],
        "DATA_INICIO": ["2025-12-01", "2026-02-01"],
        "DATA_FIM": ["9999-12-31", "9999-12-31"],
        "TIPO_DEMANDA": ["DEMANDA_UNICA", "DEMANDA_UNICA"],
        "DEMANDA_CONTRATADA": [150, 200]
    }

    df = pd.DataFrame(data)

    result = transform_demanda_contratada(df, df_consumo)

    # ✅ não vazio
    assert not result.empty

    # ✅ tem meses esperados
    meses = set(result["MES"])
    assert "202601" in meses
    assert "202602" in meses
    assert "202603" in meses

    # ✅ forward fill funcionando
    jan = result[result["MES"] == "202601"].iloc[0]
    fev = result[result["MES"] == "202602"].iloc[0]

    assert jan["DEMANDA_CONT_FP"] == 150
    assert fev["DEMANDA_CONT_FP"] == 200

    # ✅ 1 linha por mês
    assert result.groupby(["INSTALACAO", "MES"]).size().max() == 1
