#!/usr/bin/env python3
"""Emenda 1: commit de publicação onde o registro guarda (npm gitHead, crates .cargo_vcs_info.json);
PyPI: conteúdo do wheel/sdist de V × árvore da tag. Nada inferido."""
import json, sys, io, tarfile, zipfile, hashlib, subprocess, urllib.request, urllib.parse, time, tempfile, os
UA = {"User-Agent": "closure-drift-measurement/1.0"}
def get(url, binary=False):
    for i in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
                b = r.read(); return b if binary else json.loads(b)
        except urllib.error.HTTPError as e:
            if e.code == 404: return None
        except Exception: pass
        time.sleep(5 * (i + 1))
    raise RuntimeError(url)
def tag_commit(repo, tag):
    out = subprocess.run(["git", "ls-remote", f"https://github.com/{repo}", f"refs/tags/{tag}", f"refs/tags/{tag}^{{}}"],
                         capture_output=True, text=True, timeout=60).stdout.split("\n")
    d = {l.split("\t")[1]: l.split("\t")[0] for l in out if "\t" in l}
    return d.get(f"refs/tags/{tag}^{{}}") or d.get(f"refs/tags/{tag}")
rows = [json.loads(l) for l in open("results.jsonl")]
with open("results_commit_a1.jsonl", "w") as out:
    for x in rows:
        if x["outcome"] != "chegou" or x["registry_used"] == "fdroid": continue
        reg, pkg, V = x["registry_used"], x["package_used"], x["version"]
        tc = tag_commit(x["repo"], x["tag"]); pc, cls, note = None, "nao_registrado", ""
        try:
            if reg == "npm":
                d = get(f"https://registry.npmjs.org/{pkg.replace('/', '%2F')}/{urllib.parse.quote(V)}")
                pc = (d or {}).get("gitHead")
            elif reg == "crates":
                b = get(f"https://static.crates.io/crates/{pkg}/{pkg}-{V}.crate", binary=True)
                with tarfile.open(fileobj=io.BytesIO(b)) as t:
                    m = [n for n in t.getnames() if n.endswith(".cargo_vcs_info.json")]
                    if m: pc = json.load(t.extractfile(m[0]))["git"]["sha1"]
            elif reg == "pypi":
                d = get(f"https://pypi.org/pypi/{pkg}/{V}/json")
                whl = [u for u in d["urls"] if u["packagetype"] == "bdist_wheel"] or [u for u in d["urls"] if u["packagetype"] == "sdist"]
                if whl and tc:
                    b = get(whl[0]["url"], binary=True)
                    with tempfile.TemporaryDirectory() as td:
                        subprocess.run(["git", "clone", "-q", "--no-checkout", f"https://github.com/{x['repo']}", td], check=True, timeout=600)
                        files = subprocess.run(["git", "-C", td, "ls-tree", "-r", "--name-only", tc], capture_output=True, text=True).stdout.split()
                        def tagblob(path):
                            return subprocess.run(["git", "-C", td, "show", f"{tc}:{path}"], capture_output=True).stdout
                        if whl[0]["packagetype"] == "bdist_wheel":
                            z = zipfile.ZipFile(io.BytesIO(b)); members = {n: z.read(n) for n in z.namelist() if n.endswith(".py")}
                        else:
                            t = tarfile.open(fileobj=io.BytesIO(b)); members = {"/".join(n.split("/")[1:]): t.extractfile(n).read() for n in t.getnames() if n.endswith(".py") and t.getmember(n).isfile()}
                        same = diff = unmatched = 0; diffs = []
                        for n, data in members.items():
                            cands = [f for f in files if f == n or f.endswith("/" + n)]
                            if len(cands) != 1: unmatched += 1; continue
                            if tagblob(cands[0]) == data: same += 1
                            else: diff += 1; diffs.append(cands[0])
                        note = f"py same {same} differ {diff} unmatched {unmatched}; differ: {diffs[:3]}"
                        cls = "conteudo_igual" if diff == 0 and same else ("conteudo_difere" if diff else "nao_conferivel")
        except Exception as e:
            cls, note = "inconclusivo", str(e)[:150]
        if reg in ("npm", "crates") and cls != "inconclusivo":
            cls = "nao_registrado" if not pc else ("igual_ao_da_tag" if tc and pc == tc else "outro_commit")
        y = dict(x, tag_commit=tc, commit_publicado=pc, classe_commit=cls, note_a1=note)
        out.write(json.dumps(y, ensure_ascii=False) + "\n")
        print(x["case"], reg, pkg, V, cls, (pc or "")[:10], (tc or "")[:10], note[:90], file=sys.stderr)
