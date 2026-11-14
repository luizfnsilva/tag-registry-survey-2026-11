#!/usr/bin/env python3
"""Emenda 2: desfecho F-Droid pelo histórico de builds do fdroiddata (fixado num sha)."""
import json, sys, time, urllib.request, urllib.error, yaml
UA = {"User-Agent": "closure-drift-measurement/1.0"}
def get(url):
    for i in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r: return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404: return None
        except Exception: pass
        time.sleep(5 * (i + 1))
    raise RuntimeError(url)
sha = json.loads(get("https://gitlab.com/api/v4/projects/fdroid%2Ffdroiddata/repository/branches/master"))["commit"]["id"]
print("fdroiddata", sha, file=sys.stderr)
rows = [json.loads(l) for l in open("results.jsonl")]
with open("results_fdroid_a2.jsonl", "w") as out:
    for x in rows:
        if x["registry_used"] != "fdroid": continue
        V = x["version"]; idx_hit = x["outcome"] == "chegou"
        try:
            b = get(f"https://gitlab.com/api/v4/projects/fdroid%2Ffdroiddata/repository/files/metadata%2F{x['package_used']}.yml/raw?ref={sha}")
            if b is None:
                oc, commit, note = ("chegou" if idx_hit else "sem_registro"), None, "not in fdroiddata"
            else:
                m = yaml.safe_load(b) or {}
                hits = [bl for bl in (m.get("Builds") or []) if str(bl.get("versionName", "")).lstrip("vV") == V]
                ok = [bl for bl in hits if not bl.get("disable")]
                if ok:
                    oc, commit, note = "chegou", str(ok[-1].get("commit")), f"{len(ok)} build block(s)"
                elif hits:
                    oc, commit, note = ("chegou" if idx_hit else "nao_chegou"), str(hits[-1].get("commit")), "disabled: " + str(hits[-1].get("disable"))[:80]
                else:
                    oc, commit, note = ("chegou" if idx_hit else "nao_chegou"), None, f"{len(m.get('Builds') or [])} builds, none for V"
        except Exception as e:
            oc, commit, note = "inconclusivo", None, str(e)[:120]
        y = dict(x, outcome_a2=oc, fdroid_commit=commit, note_a2=note, fdroiddata_sha=sha)
        out.write(json.dumps(y, ensure_ascii=False) + "\n")
        print(x["case"], x["package_used"], V, oc, commit, note, file=sys.stderr)
