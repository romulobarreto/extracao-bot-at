"""
Pipeline principal de execução da ETL.

Responsável por:
- Orquestrar extract, transform e load
- Gerar logs da execução
"""

from pathlib import Path
import logging
import time
import sys

# =========================
# EXTRACT
# =========================
from src.extract.extract import (
    extract_cadastro,
    extract_equipamentos,
    extract_consumo,
    extract_demanda_lida,
    extract_demanda_contratada,
    extract_coordenadas,
)

# =========================
# TRANSFORM
# =========================
from src.transform.cadastro.cadastro import transform_cadastro
from src.transform.equipamentos.equipamentos import transform_equipamentos

from src.transform.consumo_demanda.consumo import transform_consumo
from src.transform.consumo_demanda.demanda_lida import transform_demanda_lida
from src.transform.consumo_demanda.demanda_contratada import transform_demanda_contratada
from src.transform.consumo_demanda.final import transform_final

from src.transform.cadastro.coordenadas import transform_coordenadas

# =========================
# LOAD
# =========================
from src.load.sqlite import load_all


# =========================
# LOG CONFIG
# =========================
LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "etl.log"


def setup_logging() -> None:
    """Configura logging em arquivo e console."""

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # evita duplicação
    if logger.handlers:
        return

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


# =========================
# PIPELINE
# =========================
def main() -> None:
    """Executa pipeline completo."""

    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("🚀 INICIANDO PIPELINE ETL")
    total_start = time.time()

    try:
        # =========================
        # EXTRACT
        # =========================
        logger.info("📥 [ETAPA] EXTRACT")
        start = time.time()

        df_cadastro = extract_cadastro()
        df_equipamentos = extract_equipamentos()
        df_consumo = extract_consumo()
        df_demanda_lida = extract_demanda_lida()
        df_demanda_contratada = extract_demanda_contratada()
        df_coord_sql = extract_coordenadas()

        logger.info(f"[EXTRACT] Concluído em {round(time.time() - start, 2)}s")

        # =========================
        # TRANSFORM
        # =========================
        logger.info("🔄 [ETAPA] TRANSFORM")
        start = time.time()

        # 🔥 NOVO: limpeza padronizada
        df_cadastro = transform_cadastro(df_cadastro)
        df_equipamentos = transform_equipamentos(df_equipamentos)

        df_consumo_t = transform_consumo(df_consumo)
        df_demanda_lida_t = transform_demanda_lida(df_demanda_lida)
        df_demanda_contratada_t = transform_demanda_contratada(
            df_demanda_contratada,
            df_consumo_t
        )

        df_coord = transform_coordenadas(df_coord_sql)

        # =========================
        # 🔥 ENRIQUECER CADASTRO
        # =========================
        df_cadastro = df_cadastro.merge(
            df_coord,
            on="INSTALACAO",
            how="left"
        )

        # =========================
        # FINAL
        # =========================
        df_final = transform_final(
            df_cadastro,
            df_consumo_t,
            df_demanda_lida_t,
            df_demanda_contratada_t
        )

        logger.info(f"[TRANSFORM] Concluído em {round(time.time() - start, 2)}s")

        # =========================
        # LOAD
        # =========================
        logger.info("💾 [ETAPA] LOAD")
        start = time.time()

        load_all(
            df_cadastro,
            df_equipamentos,
            df_final
        )

        logger.info(f"[LOAD] Concluído em {round(time.time() - start, 2)}s")

        # =========================
        # FINAL
        # =========================
        total_elapsed = round(time.time() - total_start, 2)

        logger.info(
            f"✅ PIPELINE FINALIZADA COM SUCESSO em {total_elapsed}s"
        )

    except Exception:
        logger.exception("❌ ERRO NA PIPELINE")
        raise


if __name__ == "__main__":
    main()
