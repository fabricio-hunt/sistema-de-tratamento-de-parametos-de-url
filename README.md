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

# CI – Backend headless (GitHub Actions)


## Visão geral
Este pipeline de **CI (Continuous Integration)** valida o backend do projeto sem abrir a GUI (Tkinter).  
Ele:
- instala **Python 3.12** + **pandas** + **chardet**;
- importa `tratar_urls` do backend;
- processa uma URL de exemplo;
- **gera `output.csv`**;
- falha se o arquivo não for criado e publica o arquivo como *artifact* quando passa.

> A GUI **não** é executada no CI. O teste é headless (somente backend).

---

## Estrutura esperada
- Um módulo Python com a função:
  ```python
  from backend import tratar_urls  # ajuste o caminho se seu arquivo/pacote for diferente
  ```
- A função deve receber um `pandas.DataFrame` com a coluna `url` e retornar um `DataFrame`.

Se seu backend estiver em outro caminho, ajuste o import no YAML (ex.: `from src.backend import tratar_urls`).

---

## Como habilitar

Crie o arquivo **`.github/workflows/ci-simples.yml`** com o conteúdo abaixo:

```yaml
name: CI simples (gera output)

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]
  workflow_dispatch:

jobs:
  run:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Instalar deps mínimas
        run: |
          python -m pip install --upgrade pip
          pip install pandas chardet

      - name: Gerar output.csv usando o backend
        run: |
          python - <<'PY'
          import pandas as pd
          # AJUSTE O IMPORT SE PRECISAR:
          from backend import tratar_urls
          df = pd.DataFrame({"url": ["https://exemplo.com/Loja/Produto?a=1&b=2"]})
          out = tratar_urls(df)
          out.to_csv("output.csv", index=False, encoding="utf-8")
          print("OK: output.csv gerado")
          PY

      - name: Conferir arquivo
        run: |
          test -f output.csv || (echo "ERRO: não gerou output.csv" && exit 1)

      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: output
          path: output.csv
```

**Pronto!** Ao fazer push/PR para `main`/`master` ou rodar manualmente (Workflow → *Run workflow*), o CI executa.

---

## O que valida exatamente?
1. Dependências mínimas são instaladas.
2. O backend é importado sem erro.
3. `tratar_urls` processa uma entrada simples.
4. O arquivo `output.csv` existe no final.

Se qualquer etapa falhar, o job **falha**.

---

## Baixar o resultado
Abra **Actions → execução do workflow → Artifacts → `output`** e baixe o `output.csv`.

---

## Personalizações rápidas
- **Salvar como `.txt`**  
  Troque:
  ```python
  out.to_csv("output.csv", index=False, encoding="utf-8")
  ```
  por:
  ```python
  out.to_csv("output.txt", index=False, header=False, encoding="utf-8")
  ```
  e atualize o passo “Conferir arquivo”/“Upload artifact” para `output.txt`.

- **Mudar a branch alvo**  
  Edite `branches: [ main, master ]`.

- **Rodar também testes unitários (`pytest`)**  
  Adicione um passo antes de “Gerar output.csv”:
  ```yaml
  - name: Instalar pytest
    run: pip install pytest

  - name: Rodar testes (se existirem)
    run: |
      if [ -d tests ] && compgen -G "tests/*.py" > /dev/null; then
        pytest -q
      else
        echo "Sem testes em tests/*.py; seguindo..."
      fi
  ```

---

## Dicas para evitar problemas
- **ImportError no backend** → ajuste o caminho do import no YAML (ex.: `from backend import tratar_urls` → `from src.backend import tratar_urls`).
- **Dependência faltando** → adicione `pip install <pacote>` ao passo “Instalar deps mínimas” ou crie um `requirements.txt` e instale com `pip install -r requirements.txt`.
- **GUI abrindo no CI** → não importe arquivos que criam `Tk()` no nível de módulo; isole a GUI em `if __name__ == "__main__":`.

---

## Rodar localmente (opcional)
```bash
python -m venv .venv
# Windows
.venv\Scripts\pip install -U pip pandas chardet
# Linux/macOS
source .venv/bin/activate && pip install -U pip pandas chardet

python - <<'PY'
import pandas as pd
from backend import tratar_urls
df = pd.DataFrame({"url": ["https://exemplo.com/Loja/Produto?a=1&b=2"]})
tratar_urls(df).to_csv("output.csv", index=False, encoding="utf-8")
print("OK local")
PY
```


📜 Licença
Este projeto está licenciado sob a Licença MIT.
Sinta-se livre para copiar, modificar e distribuir com atribuição.

👨‍💻 Autor
Fabricio Baraúna
💼 Bemol S/A
📧 fabriciomacedo@bemol.com.br
🚀 Projeto educacional e de automação pessoal



