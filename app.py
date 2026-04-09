"""
app.py — Streamlit: Tratamento de URLs e Redirecionamento VTEX
Fluxo: usuário cola URLs → filtro de produto → redirect 301 → /superoferta
"""

from __future__ import annotations

import io
import logging
import time

import pandas as pd
import streamlit as st

from backend import tratar_urls
from vtex_client import VtexClient, VtexAPIError

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(name)s | %(message)s")
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Redirecionamento VTEX — BEMOL",
    page_icon="🔀",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────
# Estilos
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Fundo geral */
.stApp {
    background: #0a0a14;
}

/* Hero */
.hero {
    background: linear-gradient(135deg, #0f0f23 0%, #1a1040 50%, #0f1a35 100%);
    border: 1px solid rgba(130, 80, 255, 0.2);
    border-radius: 20px;
    padding: 2.5rem 3rem;
    text-align: center;
    margin-bottom: 2rem;
}
.hero h1 {
    color: #fff;
    font-size: 2.2rem;
    font-weight: 800;
    margin: 0 0 0.5rem;
    letter-spacing: -0.5px;
}
.hero h1 span { color: #8250ff; }
.hero p { color: rgba(255,255,255,0.55); margin: 0; font-size: 1rem; }

/* Etapas */
.step-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(130,80,255,0.12);
    border: 1px solid rgba(130,80,255,0.3);
    color: #a87fff;
    border-radius: 8px;
    padding: 6px 14px;
    font-size: 0.82rem;
    font-weight: 600;
    margin-bottom: 0.75rem;
}

/* Cards de métricas */
.metrics-row {
    display: flex;
    gap: 1rem;
    margin: 1.5rem 0;
}
.metric-card {
    flex: 1;
    background: linear-gradient(135deg, #12122a, #1c1040);
    border: 1px solid rgba(130,80,255,0.2);
    border-radius: 14px;
    padding: 1.25rem;
    text-align: center;
}
.metric-card .val {
    font-size: 2rem;
    font-weight: 800;
    color: #8250ff;
    display: block;
}
.metric-card .lbl {
    font-size: 0.75rem;
    color: rgba(255,255,255,0.45);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-top: 4px;
}

/* Alert de erro */
.err-row {
    background: rgba(220,70,70,0.1);
    border: 1px solid rgba(220,70,70,0.3);
    border-radius: 8px;
    padding: 0.6rem 1rem;
    color: #ff8080;
    font-size: 0.82rem;
    font-family: monospace;
    margin-bottom: 4px;
}

/* Botão principal */
.stButton > button {
    background: linear-gradient(135deg, #8250ff, #5c37cc) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    padding: 0.65rem 2rem !important;
    transition: all 0.2s ease !important;
    width: 100%;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(130,80,255,0.4) !important;
}
.stButton > button:disabled {
    opacity: 0.4 !important;
    transform: none !important;
}

/* Textarea */
textarea {
    background: #0d0d20 !important;
    border: 1px solid rgba(130,80,255,0.25) !important;
    border-radius: 10px !important;
    color: #ccc !important;
    font-family: 'Courier New', monospace !important;
    font-size: 0.85rem !important;
}

/* Tabela */
.stDataFrame { border-radius: 10px; overflow: hidden; }

/* Divider */
hr { border-color: rgba(255,255,255,0.06) !important; }

/* Chip de status */
.chip-ok  { background:#14532d; color:#4ade80; padding:2px 10px; border-radius:20px; font-size:0.78rem; font-weight:600; }
.chip-err { background:#4a1a1a; color:#f87171; padding:2px 10px; border-radius:20px; font-size:0.78rem; font-weight:600; }
.chip-info{ background:#1e3a5f; color:#60a5fa; padding:2px 10px; border-radius:20px; font-size:0.78rem; font-weight:600; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# Hero
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>🔀 Redirecionamento <span>VTEX</span></h1>
    <p>Cole as URLs antigas · O sistema filtra os produtos · Cria 301 → <strong>/superoferta</strong></p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# Estado da sessão
# ─────────────────────────────────────────────────────────────
if "df_resultado" not in st.session_state:
    st.session_state.df_resultado = None
if "processado" not in st.session_state:
    st.session_state.processado = False


# ─────────────────────────────────────────────────────────────
# ETAPA 1 — Entrada de URLs
# ─────────────────────────────────────────────────────────────
st.markdown('<div class="step-badge">① Entrada de URLs</div>', unsafe_allow_html=True)

modo = st.radio(
    "Como deseja inserir as URLs?",
    ["✏️  Colar no campo de texto", "📁  Upload de arquivo (CSV ou TXT)"],
    horizontal=True,
    label_visibility="collapsed",
)

df_input: pd.DataFrame | None = None

if modo == "✏️  Colar no campo de texto":
    raw_text = st.text_area(
        "URLs (uma por linha)",
        placeholder="https://www.bemol.com.br/televisor-samsung-p1234567\nhttps://www.bemol.com.br/geladeira-lg-p9876543\n...",
        height=220,
        key="txt_urls",
    )
    if raw_text.strip():
        linhas = [ln.strip() for ln in raw_text.splitlines() if ln.strip()]
        df_input = pd.DataFrame({"url": linhas})
        st.caption(f"**{len(linhas)}** URLs detectadas no campo de texto.")

else:  # Upload
    uploaded = st.file_uploader(
        "Arraste ou selecione",
        type=["csv", "txt"],
        help="CSV com coluna 'url' ou TXT com uma URL por linha.",
        label_visibility="collapsed",
    )
    if uploaded:
        try:
            if uploaded.name.endswith(".txt"):
                content = uploaded.read().decode("utf-8", errors="ignore")
                linhas = [ln.strip() for ln in content.splitlines() if ln.strip()]
                df_input = pd.DataFrame({"url": linhas})
            else:
                df_input = pd.read_csv(uploaded)
            st.caption(f"✅ **{uploaded.name}** carregado — {len(df_input)} linhas brutas.")
        except Exception as e:
            st.error(f"Erro ao ler o arquivo: {e}")

# ─────────────────────────────────────────────────────────────
# ETAPA 2 — Processar URLs
# ─────────────────────────────────────────────────────────────
st.divider()
st.markdown('<div class="step-badge">② Tratar URLs</div>', unsafe_allow_html=True)

col_btn, col_info = st.columns([1, 2])

with col_btn:
    btn_processar = st.button(
        "⚡ Processar URLs",
        disabled=(df_input is None or df_input.empty),
        key="btn_processar",
    )

if btn_processar and df_input is not None:
    with st.spinner("Aplicando filtros de produto..."):
        try:
            df_res = tratar_urls(df_input, destino="/superoferta")
            st.session_state.df_resultado = df_res
            st.session_state.processado = True
        except Exception as exc:
            st.error(f"Erro no processamento: {exc}")
            st.session_state.processado = False

# Exibe resultado se já processado
if st.session_state.processado and st.session_state.df_resultado is not None:
    df_res = st.session_state.df_resultado
    n_bruto = len(df_input) if df_input is not None else "—"
    n_filtrado = len(df_res)
    taxa = f"{n_filtrado/len(df_input)*100:.1f}%" if df_input is not None and len(df_input) > 0 else "—"

    # Métricas
    st.markdown(f"""
    <div class="metrics-row">
        <div class="metric-card">
            <span class="val">{n_bruto}</span>
            <div class="lbl">URLs brutas</div>
        </div>
        <div class="metric-card">
            <span class="val">{n_filtrado}</span>
            <div class="lbl">Redirects gerados</div>
        </div>
        <div class="metric-card">
            <span class="val">{taxa}</span>
            <div class="lbl">Aproveitamento</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if df_res.empty:
        st.warning("⚠️ Nenhuma URL correspondeu ao padrão de produto (`-p\\d+`). Verifique as URLs inseridas.")
    else:
        with st.expander("📋 Ver redirects gerados", expanded=True):
            st.dataframe(
                df_res[["from", "to", "type"]],
                use_container_width=True,
                hide_index=True,
                height=min(300, 38 + 35 * len(df_res)),
            )

        # Download
        csv_bytes = df_res.to_csv(index=False, sep=";", encoding="utf-8").encode()
        st.download_button(
            "⬇️ Baixar CSV de redirects",
            data=csv_bytes,
            file_name="redirects_superoferta.csv",
            mime="text/csv",
            use_container_width=True,
        )

# ─────────────────────────────────────────────────────────────
# ETAPA 3 — Enviar para VTEX
# ─────────────────────────────────────────────────────────────
st.divider()
st.markdown('<div class="step-badge">③ Enviar Redirects para VTEX</div>', unsafe_allow_html=True)

df_para_enviar = st.session_state.df_resultado

if df_para_enviar is None or df_para_enviar.empty:
    st.info("⬆️ Processe as URLs na etapa anterior para liberar o envio.")
else:
    # Verifica credenciais VTEX
    try:
        from config import get_vtex_config
        vtex_cfg = get_vtex_config()
        col_ok, _ = st.columns([1, 3])
        with col_ok:
            st.markdown(
                f'<span class="chip-ok">✅ VTEX: {vtex_cfg.account}</span>',
                unsafe_allow_html=True,
            )
    except EnvironmentError as e:
        st.error(f"⚠️ Credenciais VTEX não encontradas: {e}")
        st.stop()

    st.markdown(f"**{len(df_para_enviar)}** redirects prontos para envio → `/superoferta`")

    confirmar = st.checkbox(
        "✅ Confirmo que quero criar estes redirects permanentes (301) na VTEX",
        key="confirmar_envio",
    )

    btn_enviar = st.button(
        "🚀 Enviar para VTEX agora",
        disabled=not confirmar,
        key="btn_enviar",
    )

    if btn_enviar and confirmar:
        client = VtexClient()
        total = len(df_para_enviar)
        sucessos = 0
        erros: list[dict] = []

        progress_bar = st.progress(0, text="Iniciando envio...")
        status_placeholder = st.empty()

        for i, row in enumerate(df_para_enviar.itertuples(index=False), start=1):
            origem = row.__getattribute__("from") if hasattr(row, "__getattribute__") else getattr(row, "from", "")
            destino = getattr(row, "to", "/superoferta")

            try:
                client.criar_redirect(origem, destino)
                sucessos += 1
            except VtexAPIError as exc:
                erros.append({"URL": origem, "Erro": str(exc)})
            except Exception as exc:
                erros.append({"URL": origem, "Erro": str(exc)})

            pct = i / total
            progress_bar.progress(pct, text=f"Enviando {i}/{total}...")
            time.sleep(0.05)  # evita rate-limit

        progress_bar.empty()

        # Resultado final
        if sucessos == total:
            st.success(f"🎉 Todos os **{sucessos}** redirects criados com sucesso na VTEX!")
        elif sucessos > 0:
            st.warning(f"⚠️ **{sucessos}** criados com sucesso · **{len(erros)}** com erro.")
        else:
            st.error(f"❌ Nenhum redirect foi criado. Verifique os erros abaixo.")

        status_placeholder.markdown(
            f'<span class="chip-ok">✅ {sucessos} criados</span>&nbsp;&nbsp;'
            f'<span class="chip-err">❌ {len(erros)} erros</span>',
            unsafe_allow_html=True,
        )

        if erros:
            with st.expander(f"❌ Ver {len(erros)} erros", expanded=len(erros) < 20):
                for err in erros:
                    st.markdown(
                        f'<div class="err-row"><b>{err["URL"]}</b> · {err["Erro"]}</div>',
                        unsafe_allow_html=True,
                    )

# ─────────────────────────────────────────────────────────────
# Footer
# ─────────────────────────────────────────────────────────────
st.divider()
st.markdown(
    "<center><small style='color:#333'>BEMOL · URL Treatment v2.0 · Streamlit + VTEX API</small></center>",
    unsafe_allow_html=True,
)
