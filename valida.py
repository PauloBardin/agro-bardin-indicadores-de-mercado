"""Confere o indicadores.json antes de publicar. Uso: python3 valida.py [arquivo_anterior.json] [--correcao]
Sai com código 1 (e não deve haver commit) se encontrar qualquer problema."""
import json, re, sys, datetime

erros = []
def erro(msg): erros.append(msg)
def num(v): return isinstance(v, (int, float)) and not isinstance(v, bool) and v == v and abs(v) != float('inf')
def url(u): return isinstance(u, str) and re.fullmatch(r'https://[^\s"\'<>`]+', u) is not None
def data_br(t):
    try: return datetime.datetime.strptime(t, '%d/%m/%Y').date()
    except Exception: return None
def limpo(v, onde='raiz'):
    if isinstance(v, str):
        if len(v) >= 400 or re.search(r'[<>"`]', v): erro(f'texto proibido em {onde}: {v[:60]!r}')
    elif isinstance(v, list):
        for i, x in enumerate(v): limpo(x, f'{onde}[{i}]')
    elif isinstance(v, dict):
        for k, x in v.items(): limpo(x, f'{onde}.{k}')

j = json.load(open('indicadores.json', encoding='utf-8'))
arqs = [a for a in sys.argv[1:] if not a.startswith('--')]
ant = json.load(open(arqs[0], encoding='utf-8')) if arqs else None
limpo(j)
if j.get('versao') != 2: erro('versao deve ser 2')
hoje = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3))).date()
at = data_br(j.get('atualizado'))
if not at: erro('atualizado deve ser dd/mm/aaaa')
elif at > hoje: erro('atualizado está no futuro')

C = j['cepea_mensal']; S = C['serie']
if not (isinstance(S, list) and len(S) >= 2): erro('serie do Cepea vazia')
meses = set()
for i, x in enumerate(S):
    if not (isinstance(x, list) and len(x) == 3 and re.fullmatch(r'\d{4}-\d{2}-\d{2}', str(x[0])) and num(x[1]) and num(x[2])):
        erro(f'serie[{i}] fora do formato: {x}'); continue
    d = datetime.date.fromisoformat(x[0])
    if d.weekday() > 4: erro(f'serie[{i}] {x[0]} cai em fim de semana')
    if (d.year, d.month) in meses: erro(f'serie[{i}] repete o mês {x[0][:7]}')
    meses.add((d.year, d.month))
    if i and x[0] <= S[i-1][0]: erro(f'serie fora de ordem em {x[0]}')
    if not (5 <= x[1] <= 300 and 5 <= x[2] <= 300): erro(f'serie[{i}] com valor fora da faixa plausível (R$/cx): {x}')
    if (d.year, d.month) >= (hoje.year, hoje.month): erro(f'serie[{i}] {x[0]} é de um mês que ainda não terminou')
U = C['ultimo']
du = data_br(U.get('data'))
if not du: erro('ultimo.data deve ser dd/mm/aaaa')
if not (num(U.get('industria')) and num(U.get('pera')) and 5 <= U['industria'] <= 300 and 5 <= U['pera'] <= 300): erro('ultimo com valores inválidos')
for k in ('industria_var', 'pera_var'):
    if k in U and not re.fullmatch(r'[+-]?\d+,\d{2}%', str(U[k])): erro(f'ultimo.{k} deve ser como +0,11%')
if du and S and du < datetime.date.fromisoformat(S[-1][0]): erro('ultimo.data é anterior ao último fim de mês da serie')
R = U.get('recente')
if not isinstance(R, dict): erro('falta ultimo.recente (cotação mais recente de cada série, com a própria data)')
else:
    for k in ('industria', 'pera'):
        r = R.get(k)
        if not (isinstance(r, dict) and data_br(r.get('data')) and num(r.get('valor')) and 5 <= r['valor'] <= 300):
            erro(f'ultimo.recente.{k} fora do formato: {r}'); continue
        if 'var' in r and not re.fullmatch(r'[+-]?\d+,\d{2}%', str(r['var'])): erro(f'ultimo.recente.{k}.var deve ser como +0,11%')
        if data_br(r['data']) > hoje: erro(f'ultimo.recente.{k}.data está no futuro')
        if du and data_br(r['data']) < du: erro(f'ultimo.recente.{k}.data é anterior a ultimo.data')
if not (url(C['links']['industria']) and url(C['links']['pera'])): erro('links do Cepea inválidos')

H = j['hf_mesa']
if not data_br(H.get('data')): erro('hf_mesa.data deve ser dd/mm/aaaa')
if not (isinstance(H['linhas'], list) and H['linhas'] and all(isinstance(l, list) and len(l) == 5 and num(l[4]) and l[4] > 0 for l in H['linhas'])): erro('hf_mesa.linhas fora do formato')
if not url(H.get('link')): erro('hf_mesa.link inválido')
E = j['ceasas']
if not data_br(E.get('data')): erro('ceasas.data deve ser dd/mm/aaaa')
if not (isinstance(E['linhas'], list) and E['linhas'] and all(isinstance(l, list) and len(l) == 4 and num(l[3]) and 0 < l[3] < 100 for l in E['linhas'])): erro('ceasas.linhas fora do formato (preço em R$/kg)')
if not (isinstance(E.get('links'), list) and len(E['links']) >= 2 and all(url(u) for u in E['links'])): erro('ceasas.links inválidos')
LD = E.get('linhas_datadas')
if not (isinstance(LD, list) and LD): erro('falta ceasas.linhas_datadas (cada linha com a data do seu fechamento)')
else:
    for l in LD:
        if not (isinstance(l, list) and len(l) == 5 and num(l[3]) and 0 < l[3] < 100 and data_br(l[4])): erro(f'ceasas.linhas_datadas fora do formato: {l}')
        elif data_br(l[4]) > hoje: erro(f'ceasas.linhas_datadas com data no futuro: {l}')
    chaves = [tuple(l[:3]) for l in LD if isinstance(l, list)]
    if len(chaves) != len(set(chaves)): erro('ceasas.linhas_datadas repete produto/classificação/praça')

F = j['fundecitrus']
if not (isinstance(F['safras'], list) and len(F['safras']) >= 2): erro('fundecitrus.safras precisa de ao menos 2 itens')
for s in F['safras']:
    if not (isinstance(s.get('safra'), str) and re.fullmatch(r'\d{4}/\d{2}', s['safra']) and isinstance(s.get('tipo'), str) and num(s.get('valor')) and 50 <= s['valor'] <= 600 and url(s.get('link')) and data_br(s.get('data'))):
        erro(f'safra fora do formato: {s}')
if not any(re.search('final', s['tipo'], re.I) for s in F['safras']): erro('falta uma safra com produção final')
if not all(isinstance(q.get('rotulo'), str) and num(q.get('valor')) for q in F['queda']): erro('queda fora do formato')
G = F['greening']
for k in ('ano', 'incidencia', 'ano_anterior', 'incidencia_anterior', 'severidade', 'severidade_anterior'):
    if not num(G.get(k)): erro(f'greening.{k} inválido')
if num(G.get('ano')) and num(G.get('ano_anterior')) and G['ano_anterior'] != G['ano'] - 1: erro('greening.ano_anterior deve ser ano - 1')
if not (isinstance(G['regioes'], list) and G['regioes'] and all(isinstance(r, list) and len(r) == 2 and isinstance(r[0], str) and num(r[1]) and 0 <= r[1] <= 100 for r in G['regioes'])): erro('greening.regioes fora do formato')
if not url(G.get('link')): erro('greening.link inválido')

# comparação com a versão anterior: nada publicado antes pode sumir ou mudar sem motivo
if ant:
    velhos = {x[0]: x for x in ant['cepea_mensal']['serie']}
    novos = {x[0]: x for x in S}
    for d, x in velhos.items():
        if d not in novos: erro(f'fim de mês {d} foi apagado da serie')
        elif novos[d] != x: erro(f'fim de mês {d} mudou de {x} para {novos[d]} (só altere se a fonte corrigiu; nesse caso, rode com --correcao)')
    if len(F['safras']) < len(ant['fundecitrus']['safras']): erro('uma estimativa de safra do Fundecitrus foi apagada')
    if data_br(j['atualizado']) and data_br(ant['atualizado']) and data_br(j['atualizado']) < data_br(ant['atualizado']): erro('atualizado ficou mais antigo que a versão anterior')

if '--correcao' in sys.argv: erros = [e for e in erros if 'mudou de' not in e]
if erros:
    print('INVÁLIDO:'); [print(' -', e) for e in erros]; sys.exit(1)
print(f"OK · coleta de {j['atualizado']} · Cepea {U['data']} · {len(S)} fins de mês · HF {H['data']} · Ceasas {E['data']}")
