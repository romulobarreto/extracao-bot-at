"""
Testes do módulo de extração.
"""

from src.extract.extract import (
    extract_cadastro,
    extract_equipamentos,
    extract_consumo,
    extract_demanda_lida,
    extract_demanda_contratada,
)


def test_extract_cadastro() -> None:
    """Valida extração de cadastro."""
    df = extract_cadastro()

    assert not df.empty
    assert "INSTALACAO" in df.columns


def test_extract_equipamentos() -> None:
    """Valida extração de equipamentos."""
    df = extract_equipamentos()

    assert not df.empty
    assert "INSTALACAO" in df.columns


def test_extract_consumo() -> None:
    """Valida extração de consumo."""
    df = extract_consumo()

    assert not df.empty
    assert "INSTALACAO" in df.columns
    assert "MES" in df.columns


def test_extract_demanda_lida() -> None:
    """Valida extração de demanda lida."""
    df = extract_demanda_lida()

    assert not df.empty
    assert "INSTALACAO" in df.columns
    assert "DEMANDA" in df.columns


def test_extract_demanda_contratada() -> None:
    """Valida extração de demanda contratada."""
    df = extract_demanda_contratada()

    assert not df.empty
    assert "INSTALACAO" in df.columns
    assert "DEMANDA_CONTRATADA" in df.columns
