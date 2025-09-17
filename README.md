# 🧹 URL Cleaning & Processing System

A modern **Python** application with a graphical interface for **drag & drop** file input.  
It cleans and standardizes URLs from a `.csv` or `.txt` file and generates a final `output.csv` in the format:

```
from;to;type;endDate
```

---

## 🚀 Key Features

- ✅ **Drag & drop** interface for quick file input  
- ✅ Pure **Python** implementation  
- ✅ Strips **domain names and query parameters**  
- ✅ Converts URLs to **lowercase**  
- ✅ Removes **duplicate** URLs  
- ✅ Generates `output.csv` with exact **from;to;type;endDate** format  
- ✅ Clear **English comments** throughout the code  

---

## 📸 User Interface

Built with `tkinterdnd2` and `ttkbootstrap` for a modern, clean look:

- Stylish themes (`flatly`, `morph`, `darkly`, etc.)
- Drag-and-drop area
- Optional **Select File** button

---

## 🖥️ Tech Stack

- [Python 3.11+](https://www.python.org/)  
- [pandas](https://pandas.pydata.org/)  
- [tkinter](https://docs.python.org/3/library/tkinter.html)  
- [tkinterdnd2](https://pypi.org/project/tkinterdnd2/)  
- [ttkbootstrap](https://ttkbootstrap.readthedocs.io/en/latest/)  
- [chardet](https://pypi.org/project/chardet/) – encoding detection  

---

## 📦 Installation

Clone the repository and set up a virtual environment:

```bash
git clone https://github.com/your-username/your-repository.git
cd your-repository

python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

If you don’t have a requirements file yet, install directly:

```bash
pip install pandas tkinterdnd2 ttkbootstrap chardet
```

---

## ▶️ How to Run

```bash
python frontend.py
```

Then simply:

- 🗂️ Drag and drop a `.csv` or `.txt` file, **or**
- 🖱️ Click **Select File** to browse.

The system processes the URLs and saves the result as `output.csv` in the same folder.

---

## 📂 Project Structure

```
url_cleaning/
│
├── frontend.py        # GUI with drag & drop and ttkbootstrap styling
├── backend.py         # URL processing logic (from;to;type;endDate)
├── output.csv         # Generated cleaned file
├── requirements.txt   # Python dependencies
└── README.md          # Project documentation
```

---

## ⚙️ Continuous Integration (GitHub Actions)

The project includes a **headless CI pipeline** that tests only the backend, ensuring no GUI pop-ups during checks.

### What the CI does

- Installs **Python 3.12**, `pandas`, and `chardet`
- Imports and runs `tratar_urls` on sample data
- Confirms that `output.csv` is generated
- Publishes the file as a downloadable artifact

### Enable It

Create `.github/workflows/ci.yml` with:

```yaml
name: CI - Backend Check

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install pandas chardet

      - name: Test backend and create output.csv
        run: |
          python - <<'PY'
          import pandas as pd
          from backend import tratar_urls
          df = pd.DataFrame({"url": ["https://example.com/store/item?id=123"]})
          tratar_urls(df).to_csv("output.csv", index=False, sep=";", encoding="utf-8")
          print("✔ output.csv created successfully")
          PY

      - name: Verify output.csv
        run: test -f output.csv

      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: output
          path: output.csv
```

---

## 🧪 Local Backend Test

Run the backend alone (no GUI):

```bash
python - <<'PY'
import pandas as pd
from backend import tratar_urls
df = pd.DataFrame({"url": ["https://example.com/store/item?id=123"]})
tratar_urls(df).to_csv("output.csv", index=False, sep=";", encoding="utf-8")
print("✔ Local test passed")
PY
```

---

## 📜 License

Licensed under the [MIT License](LICENSE).  
You’re free to use, copy, modify, and distribute with attribution.

---

## 👨‍💻 Author

**Fabricio Baraúna**  
Bemol S/A – [fabriciomacedo@bemol.com.br](mailto:fabriciomacedo@bemol.com.br)  
Educational & automation project.
