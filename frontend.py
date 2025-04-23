# frontend.py
import pandas as pd
from tkinter import messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from ttkbootstrap import Style
from ttkbootstrap.widgets import Button, Label
from backend import tratar_urls

def processar_arquivo(path):
    try:
        df = pd.read_csv(path.strip())
        df_tratado = tratar_urls(df)
        df_tratado.to_csv("output.csv", index=False)
        messagebox.showinfo("Concluído", "Tratamento finalizado! Arquivo salvo como output.csv")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao processar o arquivo:\n{str(e)}")

# Janela principal com ttkbootstrap
janela = TkinterDnD.Tk()
janela.title("Tratamento de URLs")
janela.geometry("400x250")

style = Style("flatly")  # Você pode testar: cosmo, morph, darkly, etc.

# Label de instrução
label = Label(janela, text="Arraste seu arquivo .CSV aqui", font=("Arial", 12))
label.pack(pady=20)

# Área de drop
drop_area = Label(janela, text="🗂️ Solte aqui", bootstyle="info", relief="ridge", padding=20)
drop_area.pack(padx=50, pady=10, fill="both")

# Habilita o DND
drop_area.drop_target_register(DND_FILES)
drop_area.dnd_bind("<<Drop>>", lambda e: processar_arquivo(e.data))

# Botão alternativo
btn = Button(janela, text="Selecionar arquivo", command=lambda: processar_arquivo(filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])))
btn.pack(pady=10)

janela.mainloop()
