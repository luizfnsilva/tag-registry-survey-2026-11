# Resultados — tag errada × registro (14/11/2026)

Unidade: 117 episódios REAL da auditoria de 2026 (pré-registro b16e6ca; emendas 1 b11ff6a e 2 1b33563).
Brutos: `results.jsonl` (primário), `results_fdroid_a2.jsonl` (emenda 2, fdroiddata a64de301), `results_commit_a1.jsonl` (emenda 1).

## Chegou ao registro (artefato disponível)

| registro | chegou / (chegou + não chegou) | IC 95% (Wilson) | fora do denominador |
|---|---|---|---|
| PyPI | 8 / 34 | 0,12–0,40 | — |
| npm | 8 / 20 | 0,22–0,61 | 1 sem registro |
| pub.dev | 4 / 5 | 0,38–0,96 | — |
| RubyGems | 1 / 5 | 0,04–0,62 | — |
| crates.io | 1 / 2 | 0,10–0,91 | — |
| F-Droid (post hoc, emenda 2) | 1 / 16 | 0,01–0,28 | 28 apps ainda fora do F-Droid na data da tag |
| nenhum registro (stars/flutter) | — | — | 6 |
| **total** | **23 / 82 (28%)** | **0,20–0,39** | 35 |

Sem F-Droid: 22 / 66 (33%). Uma das 23 foi retirada depois (pytest-timeout 2.5.0, yank).
Tempo da tag à publicação, onde o registro dá data (22 casos): mediana 0 dias, faixa −1 a 6.

## De onde o artefato veio (emenda 1; só onde o registro guarda)

- npm, `gitHead`: 3 do commit da tag, 2 de outro commit, 3 não registrado.
- crates.io, `.cargo_vcs_info.json`: 1 de outro commit (smallvec 1.16.0).
- F-Droid, `commit:` do build: 1 (linxshare 1.6).
- PyPI (conteúdo, não commit): 4 com todo `.py` igual à árvore da tag, 4 com diferença.
- pub.dev, RubyGems: não registrado (5).

Logo, das 23 que chegaram, a origem só é conhecida em 7 por commit e em 8 por conteúdo. Nas outras 8, não se sabe.

## O que isto não diz
- Não mede "antes de alguém notar"; não há data de percepção.
- Amostra de até 40 repos por braço, 1 episódio por repo; não é taxa de população.
- F-Droid: o índice só retém versões recentes (achado pelo controle positivo); a fonte passou ao fdroiddata,
  depois de ver o resultado. Leitura dependente disso é post hoc.

## Previsão × resultado
Previsto: F-Droid alto, PyPI/npm baixos. Errado no F-Droid: entre apps já presentes, 1 de 16 — o F-Droid
quase nunca publicou a versão de uma tag errada. PyPI 24%, npm 40%.
