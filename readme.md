# Scrapy TCC

## Processo de desenvolvimento

1. Primeiramente precisei entender qual seria a pipeline do script para coletar os dados do site.
2. Depois de entender a pipeline, criei uma função que gera dinamicamente o código do script.
3. Por fim, usei o modelo Gemini para gerar o código do script baseado na função que criei.

Tempo de execução com função armazenada: Function script() {} Took 1.3606 seconds
Tempo de execução gerando função dinamica: Function script() {} Took 15.7843 seconds

## Proximos passos

1. Adicionar suporte a sites com JavaScript (dinâmicos) — usando por exemplo Playwright.
2. Salvar os scrapers + metadata (URL, prompt, data de criação) em um banco leve como SQLite.
3. Interface CLI com Typer (ou até um front)
4. Validação automática do código gerado pela LLM (testar se compila e retorna algo).
5. Limpeza automática do HTML antes de mandar para o modelo — usando readability ou algo similar.
6. Cache de respostas da LLM — para economizar tokens/tempo.

## Extras pro TCC

1. Criar um site modelo para testar o scraper e suas funcionalidades/limites.

## Adicionais que seriam bem vindos

1. Adicionar suporte a sites com autenticação (login e session management).
2. Adicionar suporte a sites com múltiplas páginas (paginação).
3. Adicionar suporte a sites com formulários (inputs).
4. Adicionar suporte à hospedagem dos scrapers (deploy) assim como criação de rotinas de execução.
5. Adicionar suporte a sites com APIs (para coletar dados de forma mais eficiente).
