from src.transform.consumo_demanda.final import transform_final


def test_transform_final() -> None:
    """Testa merge final completo e regras de ultrapassagem."""

    import pandas as pd

    # ✅ consumo (base)
    df_consumo = pd.DataFrame({
        "INSTALACAO": [1],
        "MES": ["202601"],
        "CONSUMO_ATIVO_FP": [100],
        "CONSUMO_ATIVO_NP": [50],
        "LEITURA": ["SIM"]
    })

    # ✅ demanda lida
    df_demanda_lida = pd.DataFrame({
        "INSTALACAO": [1],
        "MES": ["202601"],
        "DEMANDA_LIDA_FP": [120],
        "DEMANDA_LIDA_NP": [40],
        "DEMANDA_LIDA_RESERVA": [0]
    })

    # ✅ demanda contratada
    df_demanda_cont = pd.DataFrame({
        "INSTALACAO": [1],
        "MES": ["202601"],
        "DEMANDA_CONT_FP": [100],
        "DEMANDA_CONT_NP": [50],
        "DEMANDA_CONT_RESERVA": [0]
    })

    result = transform_final(
        df_consumo,
        df_demanda_lida,
        df_demanda_cont
    )

    # ✅ não vazio
    assert not result.empty

    # ✅ merge correto (mesma linha)
    assert len(result) == 1

    # ✅ ultrapassagem
    assert result.iloc[0]["ULTRA_DEM_FP"] == "SIM"   # 120 > 100
    assert result.iloc[0]["ULTRA_DEM_NP"] == "NAO"   # 40 < 50
    assert result.iloc[0]["ULTRA_DEM_RES"] == "NAO"

    # ✅ leitura mantida
    assert result.iloc[0]["LEITURA"] == "SIM"


def test_transform_final_com_null() -> None:
    """Testa comportamento com valores nulos."""

    import pandas as pd

    df_consumo = pd.DataFrame({
        "INSTALACAO": [1],
        "MES": ["202601"],
        "CONSUMO_ATIVO_FP": [100],
        "CONSUMO_ATIVO_NP": [50],
        "LEITURA": ["SIM"]
    })

    # demanda lida faltando
    df_demanda_lida = pd.DataFrame({
        "INSTALACAO": [1],
        "MES": ["202601"],
    })

    df_demanda_cont = pd.DataFrame({
        "INSTALACAO": [1],
        "MES": ["202601"],
        "DEMANDA_CONT_FP": [100]
    })

    result = transform_final(
        df_consumo,
        df_demanda_lida,
        df_demanda_cont
    )

    # ✅ não quebra
    assert not result.empty

    # ✅ ultrapassagem segura
    assert result.iloc[0]["ULTRA_DEM_FP"] == "NAO"