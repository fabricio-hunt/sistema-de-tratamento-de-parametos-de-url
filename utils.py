import unicodedata
import re

def gerar_slug(texto):
    """
    Converte uma string em uma URL amigável (slug).
    Exemplo: "Olá, Mundo!" -> "ola-mundo"
    """
    # Normaliza para remover acentos
    texto = unicodedata.normalize("NFKD", texto).encode("ASCII", "ignore").decode("utf-8")
    # Converte para minúsculo
    texto = texto.lower()
    # Substitui espaços por hífen
    texto = re.sub(r"\s+", "-", texto)
    # Remove caracteres não alfanuméricos e hífen
    texto = re.sub(r"[^\w\-]", "", texto)
    # Remove múltiplos hífens seguidos
    texto = re.sub(r"-{2,}", "-", texto)
    # Remove hífens do início ou fim
    texto = texto.strip("-")
    return texto
