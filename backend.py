import pandas as pd
from urllib.parse import urlparse

def tratar_urls(df: pd.DataFrame) -> pd.DataFrame:
    """
    Keep only URLs whose *path* ends with:
      - '/p' + digits   (e.g., '/p123', '/category/p456')
      - '-p' + digits   (e.g., '/some-slug-p1058146')
    Query strings like '?v=...' are ignored by urlparse and do not affect matching.

    Output CSV columns: from;to;type;endDate
    """

    # 1) Find the 'url' column (case-insensitive)
    url_col = next((c for c in df.columns if c.lower() == "url"), None)
    if not url_col:
        raise ValueError("Column 'url' not found in the DataFrame.")

    # 2) Extract lowercase paths (domain/query removed)
    cleaned_paths = []
    for u in df[url_col].fillna("").astype(str):
        try:
            path = urlparse(u).path.lower().strip()
            if path:
                cleaned_paths.append(path)
        except Exception:
            continue  # skip malformed URLs

    # 3) Deduplicate
    unique_paths = pd.Series(cleaned_paths).drop_duplicates().reset_index(drop=True)

    # 4) Build output frame
    final_df = pd.DataFrame({
        "from": unique_paths,
        "to": "/superoferta",
        "type": "PERMANENT",
        "endDate": ""
    })

    # 5) Keep ONLY paths that end with '/p<digits>' OR '-p<digits>'
    #    Regex explanation:
    #    - '.*'  : any text before last segment
    #    - '-?p' : optional hyphen then 'p'
    #    - '\d+' : one or more digits
    #    - '/?$' : optional trailing slash at the very end
    final_df = final_df[
        final_df["from"].str.match(r".*/.*-?p\d+/?$", na=False)
    ].reset_index(drop=True)

    # 6) Save CSV with semicolon separator
    final_df.to_csv("output.csv", index=False, sep=";", encoding="utf-8")
    return final_df
        