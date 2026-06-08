"""
Testes básicos de qualidade de dados.
"""

from src.extract.extract import extract_consumo


def test_consumo_nao_negativo() -> None:
    """Consumo não deve conter valores negativos."""
    df = extract_consumo()

    assert (df["CONSUMO"] >= 0).all()


def test_mes_formato() -> None:
    """MES deve estar no formato YYYYMM."""
    df = extract_consumo()

    assert df["MES"].astype(str).str.len().eq(6).all()
