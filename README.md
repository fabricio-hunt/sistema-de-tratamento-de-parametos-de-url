# 🧹 Sistema de Tratamento de URLs

Este projeto em Python oferece uma interface gráfica moderna com funcionalidade de **arrastar e soltar** para importar um arquivo `.csv` contendo URLs. O sistema realiza o tratamento dessas URLs e gera um novo arquivo com as URLs limpas e padronizadas.

---

## 🚀 Funcionalidades

- ✅ Interface com **drag and drop**
- ✅ Inteiramente feita em Python
- ✅ Remove **domínio e parâmetros** das URLs
- ✅ Converte tudo para **letras minúsculas**
- ✅ Elimina **URLs duplicadas**
- ✅ Gera automaticamente um arquivo **output.csv**
- ✅ Comentários em **português** no código para facilitar entendimento

---

## 📸 Interface

A interface é feita com `tkinterdnd2` + `ttkbootstrap`, proporcionando:
- Tema moderno (flatly, morph, darkly, entre outros)
- Área de "soltar arquivo"
- Botão alternativo de seleção

---

## 🖥️ Tecnologias Utilizadas

- [Python 3.11+](https://www.python.org/)
- [pandas](https://pandas.pydata.org/)
- [tkinter](https://docs.python.org/3/library/tkinter.html)
- [tkinterdnd2](https://pypi.org/project/tkinterdnd2/)
- [ttkbootstrap](https://ttkbootstrap.readthedocs.io/en/latest/)

---

## 📦 Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/seu-repositorio.git
cd seu-repositorio
```

python -m venv venv
venv\Scripts\activate  # no Windows
pip install -r requirements.txt
pip install pandas tkinterdnd2 ttkbootstrap

## Como Usar 
python frontend.py
Na janela que abrir:

🗂️ Arraste e solte o seu arquivo .csv, ou

🖱️ Clique no botão “Selecionar arquivo”.

O sistema tratará as URLs e salvará o resultado em um arquivo chamado output.csv no mesmo diretório.

url_tratamento/
│
├── frontend.py        # Interface gráfica com tkinter + drag & drop
├── backend.py         # Lógica de tratamento das URLs
├── output.csv         # Arquivo final gerado
├── requirements.txt   # Arquivo com dependências
└── README.md          # Este documento

📜 Licença
Este projeto está licenciado sob a Licença MIT.
Sinta-se livre para copiar, modificar e distribuir com atribuição.

👨‍💻 Autor
Fabricio Baraúna
💼 Bemol S/A
📧 fabriciomacedo@bemol.com.br
🚀 Projeto educacional e de automação pessoal



