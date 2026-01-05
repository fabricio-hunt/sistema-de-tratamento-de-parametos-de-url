# SEO-URL-Automator: Ferramenta de Normalização e Tratamento de Redirecionamentos

![Build Status](https://img.shields.io/github/actions/workflow/status/fabricio-hunt/sistema-de-tratamento-de-parametos-de-url/ci.yml)
![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Visão Geral
O **SEO-URL-Automator** é uma solução de software desenvolvida para mitigar a incidência de erros 404 (Not Found) em plataformas de e-commerce de grande porte. A ferramenta automatiza a ingestão, limpeza e normalização de URLs legadas, gerando tabelas de redirecionamento (301) compatíveis com plataformas de gestão de conteúdo (CMS).

Este projeto foi desenvolvido no contexto de otimização de *Crawl Budget* e Governança de Dados, visando reduzir o esforço manual em auditorias de SEO Técnico.

## Definição do Problema
Em migrações de plataforma ou alterações de arquitetura da informação, URLs antigas frequentemente geram erros de rastreamento. A identificação manual de padrões em datasets com milhares de entradas é ineficiente e propensa a erros humanos.

Esta ferramenta resolve o problema através de:
1.  **Ingestão Agnóstica:** Suporte a arquivos `.csv` e `.txt` com detecção automática de encoding (via `chardet`).
2.  **Normalização Algorítmica:** Padronização de strings para *lowercase* e remoção de *query parameters*.
3.  **Filtragem por Expressão Regular:** Identificação precisa de SKUs e categorias de produtos.

## Lógica de Processamento
A validação das URLs candidatas ao redirecionamento segue estritamente o padrão de identificação de produtos (SKUs) ou categorias baseadas em sufixos numéricos.

A função de filtragem $f(u)$ aceita uma URL se, e somente se:
$$
u \in \{ s \in \Sigma^* \mid s \text{ termina em } (/p \cup -p) \cdot d^+, d \in [0-9] \}
$$

Implementação em Python (Backend):
```python
# Regex para captura de padrões de produto (/p123 ou -p123)
final_df = final_df[
    final_df["from"].str.match(r".*/.*-?p\d+/?$", na=False)
].reset_index(drop=True)
