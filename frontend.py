# frontend.py
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from backend import tratar_urls

def carregar_csv():
    caminho = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if not caminho:
        return

    df = pd.read_csv(caminho)
    df_tratado = tratar_urls(df)
    df_tratado.to_csv("output.csv", index=False)

    messagebox.showinfo("Concluído", "Tratamento finalizado. Arquivo salvo como output.csv")

janela = tk.Tk()
janela.title("Tratador de URLs")

botao = tk.Button(janela, text="Selecionar CSV", command=carregar_csv)
botao.pack(padx=20, pady=20)

janela.mainloop()
