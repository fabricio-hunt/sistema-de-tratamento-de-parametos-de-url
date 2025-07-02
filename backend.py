import pandas as pd
from urllib.parse import urlparse

def tratar_urls(df):
    """
    Função que trata as URLs conforme especificado:
    1. Detecta a coluna 'url' independentemente da capitalização.
    2. Remove domínio e parâmetros, deixando apenas o caminho da URL.
    3. Converte para letras minúsculas.
    4. Remove URLs duplicadas.
    """
    urls_tratadas = []

    # Detecta a coluna 'url' com qualquer capitalização
    coluna_url = next((col for col in df.columns if col.lower() == "url"), None)

    if not coluna_url:
        raise ValueError("Coluna 'url' não encontrada no DataFrame.")

    for url in df[coluna_url]:
        try:
            # Extrai o caminho da URL (remove domínio e parâmetros)
            caminho = urlparse(url).path
            # Converte para minúsculo
            caminho = caminho.lower()
            urls_tratadas.append(caminho)
        except Exception:
            urls_tratadas.append("erro")

    # Cria DataFrame com a coluna tratada
    df_tratado = pd.DataFrame({"URL_TRATADA": urls_tratadas})

    # Remove URLs duplicadas
    df_tratado = df_tratado.drop_duplicates()

    return df_tratado
