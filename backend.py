import pandas as pd
from urllib.parse import urlparse


def tratar_urls(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and transform a DataFrame with a 'url' column into the format:
    from;to;type;endDate

    Steps:
    1. Detect the 'url' column ignoring case.
    2. Extract the URL path (lowercased), discarding domain and query params.
    3. Remove duplicates and invalid rows.
    4. Build a DataFrame with the required columns:
       - from     -> cleaned path
       - to       -> always empty (can be customized)
       - type     -> fixed value 'superoferta'
       - endDate  -> fixed value 'PERMANENT'
    """
    # Detect 'url' column case-insensitively
    url_col = next((c for c in df.columns if c.lower() == "url"), None)
    if not url_col:
        raise ValueError("Column 'url' not found in the DataFrame.")

    cleaned_paths = []
    for u in df[url_col].fillna("").astype(str):
        try:
            path = urlparse(u).path.lower()
            if path:
                cleaned_paths.append(path)
        except Exception:
            # Skip malformed URLs silently
            pass

    # Remove duplicates and reset index
    unique_paths = pd.Series(cleaned_paths).drop_duplicates().reset_index(drop=True)

    # Build final DataFrame in the exact required format
    final_df = pd.DataFrame({
        "from": unique_paths,
        "to": "/superoferta",
        "type": "PERMANENT",
        "endDate": ""
    })

    # Save with semicolon as the field separator
    final_df.to_csv("output.csv", index=False, sep=";", encoding="utf-8")

    # Ensure semicolon as separator when saving
    return final_df
