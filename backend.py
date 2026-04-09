"""
backend.py — Camada de Serviço (Business Logic)

Contém regras de negócio para tratamento de URLs.
Não acessa banco diretamente — usa o DAL (dal.py).
"""

from __future__ import annotations

import logging
import re
from urllib.parse import urlparse

import pandas as pd

logger = logging.getLogger(__name__)

# Regex: paths que terminam com /p<dígitos> ou -p<dígitos>
_PATTERN_PRODUTO = re.compile(r".*/.*-?p\d+/?$", re.IGNORECASE)


# ---------------------------------------------------------------------------
# Funções de transformação (puras — sem I/O)
# ---------------------------------------------------------------------------

def extrair_paths(urls: pd.Series) -> pd.Series:
    """
    Extrai e normaliza o path de cada URL (remove domínio e query string).

    Args:
        urls: Série com URLs completas ou paths.

    Returns:
        Série com paths em lowercase, deduplizados.
    """
    paths: list[str] = []

    for raw in urls.fillna("").astype(str):
        try:
            path = urlparse(raw).path.lower().strip()
            if path:
                paths.append(path)
        except Exception:
            logger.warning("URL malformada ignorada: %s", raw[:80])
            continue

    return pd.Series(paths).drop_duplicates().reset_index(drop=True)


def filtrar_urls_produto(paths: pd.Series) -> pd.Series:
    """
    Mantém apenas paths que correspondem ao padrão de produto VTEX:
      - /slug-p123456  ou  /categoria/slug-p123456

    Exemplo aceito:   /televisor-samsung-75-p1058146
    Exemplo rejeitado: /eletronicos  ou  /busca?q=tv
    """
    mask = paths.str.match(_PATTERN_PRODUTO, na=False)
    resultado = paths[mask].reset_index(drop=True)
    logger.info(
        "Filtro produto: %d/%d paths mantidos.", len(resultado), len(paths)
    )
    return resultado


def montar_redirects(paths: pd.Series, destino: str = "/superoferta") -> pd.DataFrame:
    """
    Constrói DataFrame de redirects no formato esperado pelo VTEX Rewriter.

    Args:
        paths: Série de paths de origem (já filtrados).
        destino: URL de destino (default: /superoferta).

    Returns:
        DataFrame com colunas: from, to, type, endDate.
    """
    if paths.empty:
        logger.warning("Nenhum path válido para gerar redirects.")
        return pd.DataFrame(columns=["from", "to", "type", "endDate"])

    df = pd.DataFrame({
        "from": paths,
        "to": destino,
        "type": "PERMANENT",
        "endDate": "",
    })
    logger.info("Montados %d redirects → '%s'.", len(df), destino)
    return df


def tratar_urls(df: pd.DataFrame, destino: str = "/superoferta") -> pd.DataFrame:
    """
    Pipeline completo: recebe DataFrame com coluna 'url',
    retorna DataFrame de redirects pronto para uso.

    Mantém compatibilidade com o frontend antigo (Tkinter).

    Args:
        df: DataFrame com coluna 'url'.
        destino: URL de destino dos redirects.

    Returns:
        DataFrame [from, to, type, endDate] salvo também como output.csv.
    """
    url_col = next((c for c in df.columns if c.lower() == "url"), None)
    if not url_col:
        raise ValueError("Coluna 'url' não encontrada no DataFrame.")

    paths = extrair_paths(df[url_col])
    paths_filtrados = filtrar_urls_produto(paths)
    redirects = montar_redirects(paths_filtrados, destino)

    # Mantém saída CSV por compatibilidade
    redirects.to_csv("output.csv", index=False, sep=";", encoding="utf-8")
    logger.info("output.csv salvo com %d linhas.", len(redirects))

    return redirects


# ---------------------------------------------------------------------------
# Pipeline completo com Databricks (novo fluxo)
# ---------------------------------------------------------------------------

def processar_com_databricks(
    conn,
    tabela_origem: str = "url_tratamento.urls_brutas",
    tabela_destino: str = "url_tratamento.redirects_processados",
    destino_redirect: str = "/superoferta",
    dry_run: bool = False,
) -> pd.DataFrame:
    """
    Pipeline end-to-end: lê URLs do Databricks, processa e persiste redirects.

    Args:
        conn: Conexão Databricks ativa.
        tabela_origem: Tabela com URLs brutas.
        tabela_destino: Tabela destino no Delta Lake.
        destino_redirect: URL de destino dos redirects.
        dry_run: Se True, não persiste no banco.

    Returns:
        DataFrame de redirects gerados nesta execução.
    """
    from dal import fetch_urls_brutas, salvar_redirects

    logger.info("Iniciando pipeline Databricks...")

    df_urls = fetch_urls_brutas(conn, tabela=tabela_origem)
    redirects = tratar_urls(df_urls, destino=destino_redirect)

    if dry_run:
        logger.info("DRY RUN — redirects não salvos no banco.")
    elif not redirects.empty:
        salvar_redirects(conn, redirects, tabela=tabela_destino)

    return redirects