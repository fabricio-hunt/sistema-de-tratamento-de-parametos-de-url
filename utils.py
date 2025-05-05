import unicodedata
import re
from urllib.parse import quote

def url_encode(caminho_url):
    """
    Faz URL encode padrão: espaços e caracteres especiais viram códigos (%20, etc).
    Ex: "/minha página" → "/minha%20p%C3%A1gina"
    """
    return quote(caminho_url, safe="/")

def gerar_slug(texto):
    """
    Transforma texto em URL amigável (slug), removendo acentos e espaços.
    Ex: "Olá, Mundo!" → "ola-mundo"
    """
    texto = unicodedata.normalize("NFKD", texto).encode("ASCII", "ignore").decode("utf-8")
    texto = texto.lower()
    texto = re.sub(r"\s+", "-", texto)             # espaço → hífen
    texto = re.sub(r"[^\w\-]", "", texto)          # remove símbolos especiais
    texto = re.sub(r"-{2,}", "-", texto)           # múltiplos hífens viram 1
    return texto.strip("-")
