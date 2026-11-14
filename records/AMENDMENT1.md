# Emenda 1 (14/11, durante a coleta; vistos só 6 desfechos: L001, L003, L006, L007, L009, L011)

Motivo: separar três coisas que o desfecho `chegou` mistura — (a) a tag nomeia outra versão que a do
commit (todos os 117, pela auditoria), (b) o commit de onde o artefato publicado foi feito, (c) o artefato
de fato disponível no registro. O desfecho primário (c) não muda.

Acrescenta, para cada episódio `chegou`, o campo `commit_publicado`, só de fonte que o registre:
- npm: `gitHead` da versão V no documento do pacote.
- crates.io: `.cargo_vcs_info.json` dentro do `.crate` de V (`git.sha1`).
- F-Droid: o `commit:` do bloco de build de V em `fdroiddata` (`metadata/<appid>.yml`, gitlab.com/fdroid/fdroiddata).
- PyPI, RubyGems, pub.dev: o registro não guarda commit → `nao_registrado`. No PyPI vale o conferido
  secundário do pré-registro (conteúdo do artefato × árvore da tag), relatado como conteúdo, não como commit.

Valores: o sha (ou nome de tag) registrado, e a classe `igual_ao_da_tag` / `outro_commit` / `nao_registrado` /
`inconclusivo`. Um nome de tag no `commit:` do F-Droid conta como "o commit da tag", porque é isso que o
F-Droid resolve. Nada é inferido de datas ou de versões vizinhas: ausência fica ausência.

O arquivo histórico do F-Droid é baixado inteiro; se falhar, os episódios F-Droid ficam `inconclusivo`
para o índice que faltou, sem extrapolar do índice principal.
