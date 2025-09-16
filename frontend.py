import pandas as pd
from tkinter import messagebox, filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
from ttkbootstrap import Style
from ttkbootstrap.widgets import Button, Label
from backend import tratar_urls
from pathlib import Path
import chardet

def ler_txt(path):
    # Detecta encoding
    with open(path, "rb") as f:
        raw = f.read()
        enc = chardet.detect(raw)["encoding"] or "utf-8"
    # Lê linhas e monta DataFrame
    with open(path, encoding=enc, errors="ignore") as f:
        urls = [linha.strip() for linha in f if linha.strip()]
    return pd.DataFrame({"url": urls})

def processar_arquivo(path):
    try:
        p = Path(path.strip().strip("{").strip("}"))  # remove eventuais chaves do DND
        if p.suffix.lower() == ".txt":
            df = ler_txt(str(p))
        else:
            df = pd.read_csv(str(p))
        df_tratado = tratar_urls(df)
        df_tratado.to_csv("output.csv", index=False)
        messagebox.showinfo("Concluído", "Tratamento finalizado! Arquivo salvo como output.csv veja aqui!")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao processar o arquivo:\n{e}")

# --- GUI igual ao seu original ---
janela = TkinterDnD.Tk()
janela.title("Tratamento de URLs")
janela.geometry("400x250")

style = Style("flatly")
label = Label(janela, text="Arraste seu arquivo .CSV ou .TXT", font=("Arial", 12))
label.pack(pady=20)

drop_area = Label(janela, text="🗂️ Solte aqui ok", bootstyle="info", relief="ridge", padding=20)
drop_area.pack(padx=50, pady=10, fill="both")
drop_area.drop_target_register(DND_FILES)
drop_area.dnd_bind("<<Drop>>", lambda e: processar_arquivo(e.data))

btn = Button(janela, text="Selecionar arquivo", 
             command=lambda: processar_arquivo(
                 filedialog.askopenfilename(
                     filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt")]
                 )
             ))
btn.pack(pady=10)

janela.mainloop()
