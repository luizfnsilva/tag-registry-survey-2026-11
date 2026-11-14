# Tag errada × registro de pacotes — pré-registro (14/11/2026, antes de qualquer consulta)

Pergunta (de um comentário público, 14/11): das tags que apontaram para o commit errado, quantas já
tinham chegado a um registro de pacotes?

## Unidade e fonte (fixas)
Os 117 episódios codificados **REAL** na auditoria de precisão da varredura de tags de 2026
(auditoria de precisão da varredura de tags de 2026, repositório privado; [caminho removido nesta cópia pública]; codificação
dupla, κ 0,808). Um episódio = (repo, tag) em que a tag nomeia uma versão e o arquivo de versão do
commit declara outra. Nenhum episódio entra ou sai depois desta linha. Os 159 ARTEFATO não entram.

## Registro de cada episódio (regra fixa)
- `random-pypi`, `corpus100`, `ext` → PyPI, nome do projeto da coluna 2 da lista de origem.
- `random-npm` → npm; `random-rubygems` → RubyGems; `random-pubdev` → pub.dev; `rust` → crates.io;
  `fdroid`, `random-fdroid` → F-Droid (id do app), índice principal + arquivo.
- `stars`, `flutter` (sem registro na lista): ler o manifesto na tag (pyproject/setup.cfg, package.json,
  Cargo.toml, pubspec.yaml, gemspec) e consultar o registro dele pelo nome declarado; tag com prefixo
  de pacote (`@escopo/pkg@x`) usa esse pacote. Sem manifesto publicável ou nome ausente do registro →
  `sem_registro`.

## Versão procurada
V = a versão que a tag nomeia (sem `v`, sem prefixo de pacote). Comparação normalizada no registro:
PEP 440 no PyPI, igualdade de semver no npm/crates/pub.dev/RubyGems, `versionName` no F-Droid.

## Desfechos (um por episódio)
- `chegou` — V existe no registro (yank/deprecação conta como chegou, e é anotado).
- `nao_chegou` — o pacote existe no registro e V não.
- `sem_registro` — o projeto não publica naquele registro (ou em nenhum, para stars/flutter).
- `inconclusivo` — a API não respondeu após 3 tentativas espaçadas.

## Números a reportar
1. Por ecossistema e total: chegou / (chegou + nao_chegou), com IC de Wilson 95%. `sem_registro` e
   `inconclusivo` ficam fora do denominador e são relatados com contagem.
2. Para `chegou`: data de publicação de V − data da tag (dias), mediana e faixa, onde o registro der data.
3. Só PyPI, secundário e descritivo: para `chegou`, se o `.py` principal publicado em V é igual ao da
   árvore da tag (sim/não/não_conferível).

## O que isto NÃO mede
"Antes de alguém notar": não há data de percepção. Medimos se a versão chegou ao registro, não quem
percebeu ou quando. A amostra é de até 40 repos por braço com 1 episódio cada; não é taxa de população.

## Previsão (escrita antes)
Esperamos `chegou` alto no F-Droid (o F-Droid constrói da própria tag) e mais baixo no PyPI/npm, onde o
registro recusa versão repetida e o publish costuma falhar ou ser refeito. Sem número previsto.
