"""
config.py — versão atualizada que lê tanto de .env quanto de st.secrets (Streamlit Cloud).
"""

from __future__ import annotations

import os
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


def _load_env():
    """Tenta carregar .env (dev local). Em produção, já há vars de ambiente."""
    try:
        from dotenv import load_dotenv
        load_dotenv(override=False)
    except ImportError:
        pass  # python-dotenv não instalado — ok em Cloud


def _require_env(key: str) -> str:
    """
    Lê variável de ambiente.
    Em Streamlit Cloud, tenta st.secrets antes do os.environ.
    """
    # Tenta st.secrets (Streamlit Cloud)
    try:
        import streamlit as st
        val = st.secrets.get(key)
        if val:
            return str(val)
    except Exception:
        pass

    # Tenta variável de ambiente clássica
    value = os.getenv(key)
    if not value:
        raise EnvironmentError(
            f"Variável '{key}' não definida. "
            "Configure no arquivo .env (local) ou nos Secrets do Streamlit Cloud / Databricks."
        )
    return value


@dataclass(frozen=True)
class DatabricksConfig:
    host: str
    http_path: str
    token: str
    port: int = 443


@dataclass(frozen=True)
class VtexConfig:
    account: str
    environment: str
    app_key: str
    app_token: str

    @property
    def base_url(self) -> str:
        return f"https://{self.account}.{self.environment}.com"


def get_databricks_config() -> DatabricksConfig:
    _load_env()
    return DatabricksConfig(
        host=_require_env("DATABRICKS_HOST"),
        http_path=_require_env("DATABRICKS_HTTP_PATH"),
        token=_require_env("DATABRICKS_TOKEN"),
    )


def get_vtex_config() -> VtexConfig:
    _load_env()
    return VtexConfig(
        account=_require_env("VTEX_ACCOUNT"),
        environment=_require_env("VTEX_ENVIRONMENT"),
        app_key=_require_env("VTEX_APP_KEY"),
        app_token=_require_env("VTEX_APP_TOKEN"),
    )
