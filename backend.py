import pandas as pd
from urllib.parse import urlparse

def tratar_urls(df):
    """
    1. Detecta a coluna 'url' independentemente da capitalização.
    2. Remove domínio e parâmetros, deixando apenas o caminho.
    3. Converte para minúsculas.
    4. Remove duplicatas e descarta linhas inválidas.
    """
    # Detecta coluna 'url'
    coluna_url = next((c for c in df.columns if c.lower() == "url"), None)
    if not coluna_url:
        raise ValueError("Coluna 'url' não encontrada no DataFrame.")

    urls_tratadas = []
    for u in df[coluna_url].fillna("").astype(str):
        try:
            caminho = urlparse(u).path.lower()
            if caminho:
                urls_tratadas.append(caminho)
        except Exception:
            # opcional: registrar o erro
            pass

    df_tratado = pd.DataFrame({"URL_TRATADA": urls_tratadas})
    return df_tratado.drop_duplicates().reset_index(drop=True)
