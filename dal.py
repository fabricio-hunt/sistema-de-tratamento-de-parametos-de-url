"""
dal.py — Data Access Layer (Camada de Acesso a Dados)

Responsabilidade exclusiva: abrir conexão com Databricks e executar SQL.
Não contém regras de negócio — apenas I/O com o banco.
"""

from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Generator

import pandas as pd
from databricks import sql

from config import DatabricksConfig, get_databricks_config

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Conexão
# ---------------------------------------------------------------------------

@contextmanager
def get_connection(cfg: DatabricksConfig | None = None) -> Generator:
    """
    Context manager que abre e fecha a conexão com Databricks SQL Warehouse.

    Uso:
        with get_connection() as conn:
            df = query_dataframe(conn, "SELECT 1")
    """
    cfg = cfg or get_databricks_config()
    logger.info("Conectando ao Databricks SQL Warehouse...")

    conn = sql.connect(
        server_hostname=cfg.host,
        http_path=cfg.http_path,
        access_token=cfg.token,
    )
    try:
        yield conn
        logger.info("Conexão Databricks encerrada com sucesso.")
    except Exception:
        logger.exception("Erro durante uso da conexão Databricks.")
        raise
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Funções de leitura
# ---------------------------------------------------------------------------

def query_dataframe(conn, query: str, params: list | None = None) -> pd.DataFrame:
    """
    Executa uma query e retorna um DataFrame pandas.

    Args:
        conn: Conexão Databricks ativa (do context manager).
        query: SQL a ser executado.
        params: Parâmetros posicionais opcionais (ex: [valor1, valor2]).

    Returns:
        pd.DataFrame com os resultados.
    """
    logger.debug("Executando query: %s", query[:120])
    with conn.cursor() as cursor:
        cursor.execute(query, params or [])
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
    df = pd.DataFrame(rows, columns=columns)
    logger.info("Query retornou %d linhas.", len(df))
    return df


def fetch_urls_brutas(
    conn,
    tabela: str = "url_tratamento.urls_brutas",
    limit: int | None = None,
) -> pd.DataFrame:
    """
    Busca URLs brutas da tabela principal no Databricks.

    Args:
        conn: Conexão ativa.
        tabela: Nome completo da tabela (schema.tabela).
        limit: Limite de linhas (None = sem limite).

    Returns:
        DataFrame com coluna 'url'.
    """
    limit_clause = f"LIMIT {limit}" if limit else ""
    query = f"SELECT url FROM {tabela} {limit_clause}"  # noqa: S608
    return query_dataframe(conn, query)


def fetch_redirects_existentes(
    conn,
    tabela: str = "url_tratamento.redirects_processados",
) -> pd.DataFrame:
    """
    Busca redirects já processados/registrados para evitar duplicatas.

    Returns:
        DataFrame com colunas: from, to, type, endDate.
    """
    query = f"SELECT `from`, `to`, `type`, endDate FROM {tabela}"  # noqa: S608
    return query_dataframe(conn, query)


def salvar_redirects(
    conn,
    df: pd.DataFrame,
    tabela: str = "url_tratamento.redirects_processados",
    modo: str = "APPEND",
) -> None:
    """
    Persiste DataFrame de redirects no Delta Lake via INSERT.

    Args:
        conn: Conexão ativa.
        df: DataFrame com colunas [from, to, type, endDate].
        tabela: Destino no Delta Lake.
        modo: 'APPEND' (padrão) ou 'OVERWRITE'.
    """
    if df.empty:
        logger.warning("DataFrame vazio — nada a salvar.")
        return

    # Garante colunas esperadas
    required = {"from", "to", "type", "endDate"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Colunas ausentes no DataFrame: {missing}")

    rows_inserted = 0
    with conn.cursor() as cursor:
        for _, row in df.iterrows():
            cursor.execute(
                f"INSERT INTO {tabela} (`from`, `to`, `type`, endDate) "  # noqa: S608
                "VALUES (?, ?, ?, ?)",
                [row["from"], row["to"], row["type"], row.get("endDate", "")],
            )
            rows_inserted += 1

    logger.info("%d redirect(s) salvos em '%s'.", rows_inserted, tabela)
