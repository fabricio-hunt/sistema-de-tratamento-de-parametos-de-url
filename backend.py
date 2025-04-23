import pandas as pd
from urllib.parse import urlparse

def tratar_urls(df):
    """
    Função que trata as URLs conforme especificado:
    1. Remove domínio e parâmetros, deixando apenas o caminho da URL.
    2. Converte para letras minúsculas.
    3. Remove URLs duplicadas.
    """
    urls_tratadas = []

    for url in df["URL"]:
        try:
            # Extrai o caminho da URL (remove domínio e parâmetros)
            caminho = urlparse(url).path
            # Converte para minúsculo
            caminho = caminho.lower()
            urls_tratadas.append(caminho)
        except Exception as e:
            urls_tratadas.append("erro")

    # Cria DataFrame com a coluna tratada
    df_tratado = pd.DataFrame({"URL_TRATADA": urls_tratadas})

    # Remove URLs duplicadas
    df_tratado = df_tratado.drop_duplicates()

    return df_tratado
