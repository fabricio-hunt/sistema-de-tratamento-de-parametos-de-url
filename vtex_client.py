"""
vtex_client.py — Cliente HTTP isolado para API VTEX

Responsabilidade: toda comunicação com a API VTEX.
Nunca expõe credenciais — lê do config.py.
"""

from __future__ import annotations

import logging
from typing import Any

import requests
from requests import Response

from config import VtexConfig, get_vtex_config

logger = logging.getLogger(__name__)

# Timeout padrão em segundos (connect, read)
DEFAULT_TIMEOUT = (5, 30)


class VtexAPIError(Exception):
    """Erro retornado pela API VTEX com status != 2xx."""

    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        self.message = message
        super().__init__(f"[HTTP {status_code}] {message}")


class VtexClient:
    """
    Cliente VTEX com autenticação por headers (App Key + App Token).

    Uso:
        client = VtexClient()
        redirects = client.listar_redirects()
    """

    def __init__(self, cfg: VtexConfig | None = None) -> None:
        self._cfg = cfg or get_vtex_config()
        self._session = requests.Session()
        self._session.headers.update({
            "X-VTEX-API-AppKey": self._cfg.app_key,
            "X-VTEX-API-AppToken": self._cfg.app_token,
            "Content-Type": "application/json",
            "Accept": "application/json",
        })

    # ------------------------------------------------------------------
    # Helpers internos
    # ------------------------------------------------------------------

    def _get(self, path: str, params: dict | None = None) -> Any:
        url = f"{self._cfg.base_url}{path}"
        logger.debug("GET %s params=%s", url, params)
        resp = self._session.get(url, params=params, timeout=DEFAULT_TIMEOUT)
        self._raise_for_status(resp)
        return resp.json()

    def _post(self, path: str, payload: dict) -> Any:
        url = f"{self._cfg.base_url}{path}"
        logger.debug("POST %s payload_size=%d", url, len(str(payload)))
        resp = self._session.post(url, json=payload, timeout=DEFAULT_TIMEOUT)
        self._raise_for_status(resp)
        return resp.json() if resp.content else {}

    def _delete(self, path: str) -> None:
        url = f"{self._cfg.base_url}{path}"
        logger.debug("DELETE %s", url)
        resp = self._session.delete(url, timeout=DEFAULT_TIMEOUT)
        self._raise_for_status(resp)

    @staticmethod
    def _raise_for_status(resp: Response) -> None:
        if not resp.ok:
            raise VtexAPIError(
                status_code=resp.status_code,
                message=resp.text[:300],
            )

    # ------------------------------------------------------------------
    # Endpoints de Redirect (VTEX Rewriter)
    # ------------------------------------------------------------------

    def criar_redirect(
        self,
        origem: str,
        destino: str = "/superoferta",
        tipo: str = "permanent",
    ) -> dict:
        """
        Cria um redirect 301 no VTEX Rewriter.

        Args:
            origem: Path de origem (ex: /produto-slug-p123456).
            destino: Path de destino (default: /superoferta).
            tipo: 'permanent' (301) ou 'temporary' (302).

        Returns:
            Resposta JSON da API.
        """
        payload = {
            "from": origem,
            "to": destino,
            "type": tipo,
            "endDate": None,
        }
        logger.info("Criando redirect: %s → %s", origem, destino)
        return self._post("/api/rewriter/routes/redirects", payload)

    def criar_redirects_em_lote(
        self,
        redirects: list[dict],
        destino: str = "/superoferta",
    ) -> tuple[int, list[dict]]:
        """
        Cria múltiplos redirects e retorna (sucessos, erros).

        Args:
            redirects: Lista de dicts com chave 'from' (e opcionalmente 'to').
            destino: Destino padrão caso 'to' não esteja no dict.

        Returns:
            (total_criados, lista_de_erros)
        """
        sucessos = 0
        erros: list[dict] = []

        for item in redirects:
            origem = item.get("from", "")
            to = item.get("to", destino)
            if not origem:
                logger.warning("Item sem 'from': %s", item)
                continue
            try:
                self.criar_redirect(origem, to)
                sucessos += 1
            except VtexAPIError as exc:
                logger.error("Falha ao criar redirect '%s': %s", origem, exc)
                erros.append({"from": origem, "erro": str(exc)})
            except requests.Timeout:
                logger.error("Timeout ao criar redirect '%s'.", origem)
                erros.append({"from": origem, "erro": "timeout"})

        logger.info(
            "Lote concluído: %d criados, %d erros.", sucessos, len(erros)
        )
        return sucessos, erros

    def listar_redirects(self, page: int = 1, page_size: int = 100) -> dict:
        """Lista redirects existentes com paginação."""
        return self._get(
            "/api/rewriter/routes/redirects",
            params={"page": page, "pageSize": page_size},
        )

    def deletar_redirect(self, origem: str) -> None:
        """Remove um redirect pelo path de origem."""
        logger.info("Deletando redirect: %s", origem)
        self._delete(f"/api/rewriter/routes/redirects/{origem.lstrip('/')}")

    # ------------------------------------------------------------------
    # Endpoint de produto (consulta)
    # ------------------------------------------------------------------

    def buscar_produto(self, product_id: str) -> dict:
        """Busca detalhes de um produto pelo ID."""
        return self._get(f"/api/catalog/pvt/product/{product_id}")
