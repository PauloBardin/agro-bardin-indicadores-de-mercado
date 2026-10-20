# Como atualizar o indicadores.json

Instruções para a coleta diária (dias úteis, fim da tarde). O app da Agro Bardin lê `indicadores.json` deste repositório quando alguém clica em **Atualizar indicadores**.

## Regras que valem sempre

1. **Nunca invente nem estime nenhum número.** Todo valor tem de ter sido lido na fonte indicada, na data indicada. Não converta unidades, não arredonde além do que a fonte publica e não preencha lacunas.
2. Se uma fonte não abrir, mudar de formato, estiver ambígua ou trouxer uma data diferente da esperada, **mantenha o bloco anterior daquela fonte sem mudanças** e registre o motivo na mensagem do commit. As outras fontes seguem normalmente.
3. Não mude a estrutura do arquivo (nomes de campos, ordem das colunas, `versao: 2`). O app recusa arquivos fora do formato.
4. Leia as páginas com a ferramenta de busca de páginas (WebFetch). O acesso direto por `curl` costuma ser bloqueado por esses sites.
5. Antes de publicar, rode `python3 valida.py indicadores.anterior.json` (a versão que estava no repositório). Se aparecer INVÁLIDO, corrija o que estiver errado ou volte o bloco problemático para a versão anterior. **Nunca faça commit de um arquivo inválido.**

## 0. Antes de começar

Guarde a versão atual para comparação: `cp indicadores.json indicadores.anterior.json` (esse arquivo não vai para o repositório; está no `.gitignore`).

## 1. Cepea · cotação do dia (`cepea_mensal.ultimo`)

- Laranja indústria: https://www.noticiasagricolas.com.br/cotacoes/laranja/laranja-industria
- Laranja pera in natura: https://www.noticiasagricolas.com.br/cotacoes/laranja/laranja-pera-in-natura

Cada página tem a tabela `Data | R$/Caixa 40,8 kg | Variação Dia (%)`. Pegue a **data mais recente que aparece nas duas páginas** e preencha:

- `data`: essa data, `dd/mm/aaaa`
- `industria` e `pera`: o preço em R$/caixa 40,8 kg (número com ponto decimal, ex.: 27.8)
- `industria_var` e `pera_var`: a variação do dia como texto com sinal e vírgula, ex.: `"+0,11%"`, `"-0,68%"` (sem sinal na fonte = positivo, use `+`)

## 2. Cepea · fechamento de cada mês (`cepea_mensal.serie`)

Cada item é `["aaaa-mm-dd", indústria, pera]`, com a cotação do **último dia útil com cotação** de um mês já encerrado.

- Só acrescente meses que **já terminaram** e que ainda não estão na lista. Nunca altere nem apague itens antigos.
- Para o mês que falta, abra as páginas por data, começando no último dia útil do mês:
  `https://www.noticiasagricolas.com.br/cotacoes/laranja/laranja-industria/aaaa-mm-dd` e
  `https://www.noticiasagricolas.com.br/cotacoes/laranja/laranja-pera-in-natura/aaaa-mm-dd`
- Confira que a página mostra `Fechamento: dd/mm/aaaa` com exatamente essa data e uma linha com essa data. Se não houver cotação nesse dia (feriado), tente o dia útil anterior. Use a mesma data para indústria e pera.

## 3. Hortifruti/Cepea · preços de mesa (`hf_mesa`)

Fonte: https://www.hfbrasil.org.br/br/estatistica/citros.aspx (tabela `Produto | Região | Unidade | datas...`).

Atualize só as linhas que já existem no arquivo, com o valor da **coluna mais recente** da tabela:

| Produto no arquivo | Linha na fonte | Regiões | Unidade |
|---|---|---|---|
| Laranja lima · Árvore | Laranja Lima - Árvore - Mercado | Araraquara, Bebedouro | R$/cx 40,8 kg |
| Laranja pera · Árvore | Laranja Pêra - Árvore - Mercado | Araraquara, Bebedouro, Limeira, Mogiana | R$/cx 40,8 kg |
| Lima ácida tahiti · Colhida | Lima Ácida Tahiti - Colhida - Mercado | Araraquara, Bebedouro, Mogiana | R$/cx 27 kg |
| Tangerina ponkan · Árvore | Tangerina Ponkan - Árvore - Mercado | Araraquara | R$/cx 27 kg |

- `data`: a data da coluna mais recente, em `dd/mm/aaaa`.
- Se uma linha estiver sem valor (`- - -`) na coluna mais recente, retire essa linha do arquivo nesta coleta (não repita o valor antigo com data nova).
- Se a página não tiver a coluna de uma data mais nova que a atual, não mude nada neste bloco.

## 4. Ceasas · preços no atacado (`ceasas`)

- Laranja: https://www.noticiasagricolas.com.br/cotacoes/laranja/laranja-ceasas (tabela `Tipo | Preço (R$/Kg) | Variação (%)`, com blocos `Fechamento: dd/mm/aaaa` e as praças Ceasa Campinas/SP, Ceasa Belo Horizonte/MG e Ceagesp/SP)
- Demais frutas (limão tahiti, tangerinas murcott e ponkan, abacate, mamão formosa): https://www.noticiasagricolas.com.br/cotacoes/frutas

Atualize as linhas existentes (`[produto, classificação, praça, preço R$/kg]`) com o preço do **fechamento mais recente**. Preço sempre em R$/kg, como publicado. Se uma linha não aparecer no fechamento mais recente, retire-a nesta coleta. `data` = data desse fechamento.

## 5. Fundecitrus · safra e greening (`fundecitrus`)

Confira as notícias em https://www.fundecitrus.com.br/noticias/ (e, se houver, a página de estimativa de safra). Só mude este bloco quando o Fundecitrus publicar algo novo e oficial:

- **Nova estimativa, reestimativa ou produção final de safra:** acrescente ao fim de `safras` um item `{"safra":"aaaa/aa","valor":milhões de caixas,"tipo":"Estimativa inicial (maio)" | "Reestimativa (mês)" | "Produção final","fonte":"Fundecitrus, dd/mm/aaaa","data":"dd/mm/aaaa","link":"url da notícia ou do relatório"}`. Mantenha os itens antigos. Se a publicação trouxer a taxa de queda de frutos, acrescente em `queda` `{"rotulo":"aaaa/aa (tipo)","valor":número}`.
- **Novo levantamento de doenças (greening):** substitua `greening` inteiro com os números impressos no relatório: `ano`, `incidencia` (média do cinturão, %), `ano_anterior`, `incidencia_anterior`, `severidade`, `severidade_anterior`, `regioes` (`[nome da região, % de incidência]`, do maior para o menor, com os nomes como o Fundecitrus escreve), `fonte` e `link` do relatório.

## 6. Fechamento

1. `atualizado`: a data de hoje em `dd/mm/aaaa` (horário de Brasília).
2. Rode `python3 valida.py indicadores.anterior.json` e só siga se aparecer `OK`.
3. Commit em `main` com a mensagem `Coleta dd/mm/aaaa: ` + o que mudou (ex.: `Cepea 21/10; HF 21/10; Ceasas 21/10; sem novidade no Fundecitrus`) e, se houver, o motivo de cada bloco mantido. Faça o push.
