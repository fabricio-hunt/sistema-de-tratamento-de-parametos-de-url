import pandas as pd
from urllib.parse import urlparse


def tratar_urls(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and transform a DataFrame that contains a 'url' column.
    The function keeps only rows whose path ends with '/p' followed by digits
    (e.g., '/p123456', '/electronics/p98765') and removes all others.

    Output CSV format:
        from;to;type;endDate

    Steps:
    1. Detect the 'url' column (case-insensitive).
    2. Extract only the URL path (lowercase, without domain or query params).
    3. Remove duplicates.
    4. Keep only paths that match '/p' + digits pattern.
    5. Build the final DataFrame with required columns.
    6. Export the result to 'output.csv'.
    """

    # 1️⃣ Find the column that matches 'url' (ignore upper/lower case)
    url_col = next((c for c in df.columns if c.lower() == "url"), None)
    if not url_col:
        raise ValueError("Column 'url' not found in the DataFrame.")

    # 2️⃣ Extract the path from each URL (ignore domain, query, etc.)
    cleaned_paths = []
    for u in df[url_col].fillna("").astype(str):
        try:
            # Parse URL and extract lowercase path
            path = urlparse(u).path.lower().strip()
            if path:
                cleaned_paths.append(path)
        except Exception:
            # Skip malformed URLs silently
            continue

    # 3️⃣ Remove duplicates and reset the index
    unique_paths = pd.Series(cleaned_paths).drop_duplicates().reset_index(drop=True)

    # 4️⃣ Build the final DataFrame structure
    final_df = pd.DataFrame({
        "from": unique_paths,
        "to": "/superoferta",
        "type": "PERMANENT",
        "endDate": ""
    })

    # 5️⃣ Keep ONLY URLs ending with '/p' + digits (e.g., /p123, /category/p456)
    #     This automatically excludes '/p', '/video', '/banheiro', etc.
    final_df = final_df[final_df["from"].str.match(r".*/p\d+$", na=False)].reset_index(drop=True)

    # 6️⃣ Export the cleaned data to a CSV file using semicolon as separator
    final_df.to_csv("output.csv", index=False, sep=";", encoding="utf-8")

    return final_df
