import pandas as pd
from tkinter import messagebox, filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
from ttkbootstrap import Style
from ttkbootstrap.widgets import Button, Label
from pathlib import Path
import chardet

# Import your own URL processing function
from backend import tratar_urls  # keep your implementation


def read_txt(path: str) -> pd.DataFrame:
    """Detect encoding and read a .txt file (one URL per line) into a DataFrame."""
    with open(path, "rb") as f:
        raw = f.read()
        enc = chardet.detect(raw).get("encoding") or "utf-8"

    with open(path, encoding=enc, errors="ignore") as f:
        urls = [line.strip() for line in f if line.strip()]

    return pd.DataFrame({"url": urls})


def normalize_dnd_path(raw_path: str) -> Path:
    """
    Normalize a path coming from drag-and-drop (may include braces or quotes).
    Example: '{C:/Users/me/Desktop/file.csv}' -> Path('C:/Users/me/Desktop/file.csv')
    """
    cleaned = raw_path.strip().strip("{").strip("}").strip().strip('"').strip("'")
    return Path(cleaned)


def process_file(path_str: str) -> None:
    """Load CSV or TXT, run treatment, and save output next to the input file."""
    try:
        if not path_str:
            return  # user canceled the dialog

        p = normalize_dnd_path(path_str)
        if not p.exists():
            messagebox.showerror("Error", f"File not found:\n{p}")
            return

        # Read input
        if p.suffix.lower() == ".txt":
            df = read_txt(str(p))
        else:
            # Try to detect encoding for CSV as well
            try:
                with open(p, "rb") as f:
                    enc = chardet.detect(f.read()).get("encoding") or "utf-8"
                df = pd.read_csv(p, encoding=enc)
            except Exception:
                # Fallback to default pandas behavior
                df = pd.read_csv(p)

        # Process using your backend function
        df_processed = tratar_urls(df)

        # Output path
        out_path = p.with_name(p.stem + "_clean.csv")
        df_processed.to_csv(out_path, index=False, sep=";", encoding="utf-8")


        messagebox.showinfo("Done", f"Processing completed!\nSaved as:\n{out_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to process the file:\n{e}")
# ---------------- GUI ----------------
app = TkinterDnD.Tk()
app.title("URL Processing")
app.geometry("420x260")

style = Style("flatly")

label = Label(app, text="Drag and drop your .CSV or .TXT file", font=("Arial", 12))
label.pack(pady=20)

drop_area = Label(
    app,
    text="Drop here",
    bootstyle="info",
    relief="ridge",
    padding=2,
)
drop_area.pack(padx=50, pady=10, fill="both")
drop_area.drop_target_register(DND_FILES)
drop_area.dnd_bind("<<Drop>>", lambda e: process_file(e.data))

btn = Button(
    app,
    text="Select file",
    command=lambda: process_file(
        filedialog.askopenfilename(
            title="Choose a file",
            filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt"), ("All files", "*.*")],
        )
    ),
)
btn.pack(pady=10)

app.mainloop()
