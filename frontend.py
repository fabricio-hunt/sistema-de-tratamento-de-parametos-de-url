import pandas as pd
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox, filedialog
from tkinterdnd2 import TkinterDnD, DND_FILES
from pathlib import Path
import chardet

from backend import tratar_urls


# =========================
# File handling
# =========================

def detect_encoding(path: Path) -> str:
    """Detect file encoding using chardet."""
    with open(path, "rb") as f:
        return chardet.detect(f.read()).get("encoding") or "utf-8"


def read_txt(path: Path) -> pd.DataFrame:
    """Read TXT file (one URL per line) into DataFrame."""
    encoding = detect_encoding(path)
    with open(path, encoding=encoding, errors="ignore") as f:
        urls = [line.strip() for line in f if line.strip()]
    return pd.DataFrame({"url": urls})


def read_csv(path: Path) -> pd.DataFrame:
    """Read CSV file with encoding detection."""
    try:
        encoding = detect_encoding(path)
        return pd.read_csv(path, encoding=encoding)
    except Exception:
        return pd.read_csv(path)


def normalize_dnd_path(raw_path: str) -> Path:
    """Normalize drag-and-drop path."""
    cleaned = raw_path.strip().strip("{}").strip('"').strip("'")
    return Path(cleaned)


# =========================
# Processing
# =========================

def process_file(path_str: str) -> None:
    """Load file, process URLs, and save output."""
    if not path_str:
        return

    try:
        path = normalize_dnd_path(path_str)

        if not path.exists():
            messagebox.showerror("Error", f"File not found:\n{path}")
            return

        if path.suffix.lower() == ".txt":
            df = read_txt(path)
        elif path.suffix.lower() == ".csv":
            df = read_csv(path)
        else:
            messagebox.showerror("Error", "Unsupported file format.")
            return

        df_processed = tratar_urls(df)

        output_path = path.with_name(f"{path.stem}_clean.csv")
        df_processed.to_csv(output_path, index=False, sep=";", encoding="utf-8")

        messagebox.showinfo(
            "Success",
            f"Processing completed successfully!\n\nSaved as:\n{output_path}",
        )

    except Exception as exc:
        messagebox.showerror("Error", f"Processing failed:\n{exc}")


# =========================
# GUI
# =========================

def create_app() -> None:
    app = TkinterDnD.Tk()
    app.title("URL Processing")
    app.geometry("420x260")
    app.resizable(False, False)

    tb.Style(theme="flatly")

    title = tb.Label(
        app,
        text="URL Processing Tool",
        font=("Segoe UI", 14, "bold"),
    )
    title.pack(pady=(15, 5))

    subtitle = tb.Label(
        app,
        text="Drag & drop a CSV or TXT file",
        font=("Segoe UI", 10),
    )
    subtitle.pack()

    drop_area = tb.Label(
        app,
        text="Drop file here",
        bootstyle=INFO,
        relief="ridge",
        padding=15,
    )
    drop_area.pack(padx=40, pady=15, fill="both")
    drop_area.drop_target_register(DND_FILES)
    drop_area.dnd_bind("<<Drop>>", lambda e: process_file(e.data))

    btn = tb.Button(
        app,
        text="Select file",
        bootstyle=PRIMARY,
        width=20,
        command=lambda: process_file(
            filedialog.askopenfilename(
                title="Choose a file",
                filetypes=[
                    ("CSV files", "*.csv"),
                    ("Text files", "*.txt"),
                    ("All files", "*.*"),
                ],
            )
        ),
    )
    btn.pack(pady=10)

    app.mainloop()


# =========================
# Entry point
# =========================

if __name__ == "__main__":
    create_app()
