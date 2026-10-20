# Indicadores de mercado · Agro Bardin

Este repositório guarda só **dados públicos de mercado** usados na aba **Indicadores** do app de Produção e Venda da Agro Bardin:

- Cepea/Esalq: laranja indústria e laranja pera in natura (via Notícias Agrícolas)
- Hortifruti/Cepea (HF Brasil): preços de citros por região
- Ceasas Campinas, Belo Horizonte e Ceagesp (via Notícias Agrícolas)
- Fundecitrus: estimativas de safra e levantamento de greening

Nenhum dado interno da empresa (carregamentos, clientes, volumes ou preços de venda) fica aqui.

O arquivo `indicadores.json` é atualizado todo dia útil por uma tarefa agendada no Claude, seguindo `COMO_ATUALIZAR.md`, e conferido por `valida.py` antes de cada publicação. O botão **Atualizar indicadores** do app lê este arquivo.
