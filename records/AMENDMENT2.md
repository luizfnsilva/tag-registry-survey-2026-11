# Emenda 2 (14/11, DEPOIS de ver os desfechos primários; post hoc, declarada como tal)

Visto: os 44 episódios F-Droid deram `nao_chegou`, contra a previsão. Controle positivo: o leitor do índice
funciona (lê `versionName` de todos os apps), mas os índices do F-Droid (principal 74 MB + arquivo 121 MB,
baixados inteiros) só retêm as versões recentes de cada app — p.ex. `com.abhinavxt.debforge` tem 1.7.1–1.9.2,
e o episódio é 1.0.1. Ausência do índice não é "nunca publicado".

Mudança: para F-Droid, ausência do índice passa a `inconclusivo_indice` (não `nao_chegou`). A fonte do
desfecho passa a ser o histórico de builds do próprio F-Droid, `fdroiddata` `metadata/<appid>.yml`
(gitlab.com/fdroid/fdroiddata, ramo master, sha anotado no resultado):
- bloco `Builds` com `versionName` = V e sem `disable:` → `chegou` (o F-Droid construiu e publicou V);
  o `commit:` desse bloco é o commit de publicação (emenda 1);
- bloco com V e `disable:` → `nao_chegou` (anotado o motivo);
- app no fdroiddata sem bloco para V → `nao_chegou`;
- app ausente do fdroiddata → `sem_registro`.
Se o índice tiver V (presença), conta `chegou` independentemente.

Os desfechos dos outros registros (PyPI, npm, RubyGems, pub.dev, crates) não mudam: esses registros mantêm
todas as versões publicadas. Os números F-Droid serão relatados como post hoc.
