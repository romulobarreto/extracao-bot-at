"""
Transformação das coordenadas.

Responsável por:
- Ler arquivos KMZ
- Ler base XLSX
- Consolidar com base do banco
- Priorizar: KMZ > XLSX > SQL
"""

import logging
import zipfile
import re
from pathlib import Path
import xml.etree.ElementTree as ET

import pandas as pd

logger = logging.getLogger(__name__)

INPUT_DIR = Path(__file__).resolve().parents[3] / "input"


# =========================
# 🔹 1. PARSER KMZ
# =========================
def parse_kmz_file(file_path: Path) -> pd.DataFrame:
    """Extrai coordenadas de um KMZ ou KML."""

    registros = []

    try:
        # 🔹 se for KMZ (zip)
        if file_path.suffix == ".kmz":
            with zipfile.ZipFile(file_path, 'r') as z:
                kml_file = [f for f in z.namelist() if f.endswith(".kml")][0]
                with z.open(kml_file) as f:
                    tree = ET.parse(f)
                    root = tree.getroot()

        # 🔹 se for KML direto
        elif file_path.suffix == ".kml":
            tree = ET.parse(file_path)
            root = tree.getroot()

        else:
            return pd.DataFrame()

    except Exception as e:
        logger.warning(f"[COORD] Erro ao ler {file_path.name}: {e}")
        return pd.DataFrame()

    ns = {"kml": "http://www.opengis.net/kml/2.2"}

    
    for placemark in root.iter():
        if "Placemark" not in placemark.tag:
            continue

        name_elem = None
        coord_elem = None

        for elem in placemark.iter():
            if "name" in elem.tag:
                name_elem = elem
            if "coordinates" in elem.tag:
                coord_elem = elem


        if name_elem is None or coord_elem is None:
            continue

        name = name_elem.text or ""
        coord_text = coord_elem.text or ""

        
        print(f"DEBUG NAME: {name}")
        print(f"DEBUG COORD: {coord_text}")


        instalacoes = re.findall(r"\b\d{6,10}\b", name)

        if not instalacoes:
            continue

        try:
            lon, lat = coord_text.strip().split(",")[0:2]
            lon = float(lon)
            lat = float(lat)
        except Exception:
            continue

        for inst in instalacoes:
            registros.append({
                "INSTALACAO": str(inst),
                "LATITUDE": lat,
                "LONGITUDE": lon
            })

    return pd.DataFrame(registros)


# =========================
# 🔹 2. CONSOLIDAR KMZ
# =========================
def transform_kmz() -> pd.DataFrame:
    """Processa todos os arquivos KMZ."""

    logger.info("[COORD] Lendo arquivos KMZ...")

    kmz_files = list(INPUT_DIR.glob("*.kmz")) + list(INPUT_DIR.glob("*.kml"))

    if not kmz_files:
        logger.warning("[COORD] Nenhum KMZ encontrado.")
        return pd.DataFrame(columns=["INSTALACAO", "LATITUDE", "LONGITUDE"])

    dfs = [parse_kmz_file(f) for f in kmz_files]

    dfs = [df for df in dfs if not df.empty]

    if not dfs:
        logger.warning("[COORD] KMZ/KML não gerou dados válidos.")
        return pd.DataFrame(columns=["INSTALACAO", "LATITUDE", "LONGITUDE"])

    df_kmz = pd.concat(dfs, ignore_index=True)

    # remover duplicidade (pegar primeiro válido)
    
    if not df_kmz.empty:
        df_kmz = df_kmz.dropna(subset=["LATITUDE", "LONGITUDE"])

    df_kmz = df_kmz.drop_duplicates(
        subset=["INSTALACAO"],
        keep="first"
    )

    logger.info(f"[COORD] KMZ consolidado: {len(df_kmz)} instalações")

    return df_kmz


# =========================
# 🔹 3. XLSX
# =========================
def transform_xlsx() -> pd.DataFrame:
    """Lê base XLSX de coordenadas."""

    logger.info("[COORD] Lendo XLSX...")

    xlsx_path = INPUT_DIR / "COORDENADAS.xlsx"

    if not xlsx_path.exists():
        logger.warning("[COORD] XLSX não encontrado.")
        return pd.DataFrame(columns=["INSTALACAO", "LATITUDE", "LONGITUDE"])

    df = pd.read_excel(xlsx_path)

    df["INSTALACAO"] = df["INSTALACAO"].astype(str)

    return df[["INSTALACAO", "LATITUDE", "LONGITUDE"]]


# =========================
# 🔹 4. CONSOLIDAÇÃO FINAL
# =========================
def transform_coordenadas(
    df_sql: pd.DataFrame
) -> pd.DataFrame:
    """
    Consolida coordenadas com prioridade:
    KMZ > XLSX > SQL
    """

    logger.info("[COORD] Iniciando consolidação...")

    # padronizar SQL
    df_sql = df_sql.copy()
    df_sql["INSTALACAO"] = df_sql["INSTALACAO"].astype(str)

    df_kmz = transform_kmz()
    df_xlsx = transform_xlsx()

    # juntar tudo
    df = pd.concat([
        df_kmz.assign(FONTE="KMZ"),
        df_xlsx.assign(FONTE="XLSX"),
        df_sql.assign(FONTE="SQL")
    ], ignore_index=True)

    
    logger.info("[COORD] Distribuição por fonte (antes de prioridade):")
    logger.info("\n" + df["FONTE"].value_counts().to_string())


    # ordem de prioridade
    prioridade = {
        "KMZ": 1,
        "XLSX": 2,
        "SQL": 3
    }

    df["PRIORIDADE"] = df["FONTE"].map(prioridade)

    # remover nulos
    df = df.dropna(subset=["LATITUDE", "LONGITUDE"])

    # ordenar por prioridade
    df = df.sort_values(["INSTALACAO", "PRIORIDADE"])

    # manter melhor coordenada
    df_final = df.drop_duplicates(
        subset=["INSTALACAO"],
        keep="first"
    )
    
    logger.info("[COORD] Distribuição FINAL por fonte:")
    logger.info("\n" + df_final["FONTE"].value_counts().to_string())


    return df_final[["INSTALACAO", "LATITUDE", "LONGITUDE"]]