#!/usr/bin/env python3
"""Consulta o registro de cada episódio de units.tsv e grava results.jsonl. Regras em PREREGISTRATION.md."""
import csv, json, re, sys, time, urllib.request, urllib.parse, gzip, os
from pathlib import Path
UA = {"User-Agent": "closure-drift-measurement/1.0"}
CACHE = Path(sys.argv[2]); CACHE.mkdir(parents=True, exist_ok=True)

def get(url, binary=False):
    last = None
    for i in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
                b = r.read()
                return b if binary else json.loads(b)
        except urllib.error.HTTPError as e:
            if e.code == 404: return None
            last = e
        except Exception as e:
            last = e
        time.sleep(5 * (i + 1))
    raise RuntimeError(f"{url}: {last}")

def norm_pep440(v):
    try:
        from packaging.version import Version
        return str(Version(v))
    except Exception:
        return v.lower()

def tagver(tag):
    t = tag.rsplit("@", 1)[-1] if tag.startswith("@") else tag
    t = re.sub(r"^.*?[-_/](?=v?\d)", "", t) if not re.match(r"^v?\d", t) else t
    return t[1:] if t[:1] in "vV" else t

FD = {}
def fdroid():
    if not FD:
        for name, url in [("main", "https://f-droid.org/repo/index-v2.json"), ("archive", "https://f-droid.org/archive/index-v2.json")]:
            f = CACHE / f"fdroid-{name}.json"
            if not f.exists(): f.write_bytes(get(url, binary=True))
            FD[name] = json.loads(f.read_text())["packages"]
    return FD

def q(reg, pkg, V):
    """-> (outcome, published_iso|None, note)"""
    if reg == "pypi":
        d = get(f"https://pypi.org/pypi/{urllib.parse.quote(pkg)}/json")
        if d is None: return "sem_registro", None, "pypi 404"
        rel = {norm_pep440(k): (k, fs) for k, fs in d["releases"].items()}
        hit = rel.get(norm_pep440(V))
        if not hit: return "nao_chegou", None, f"{len(rel)} versions"
        k, fs = hit
        if not fs: return "chegou", None, "release without files"
        up = min(f["upload_time_iso_8601"] for f in fs)
        return "chegou", up, "yanked" if all(f.get("yanked") for f in fs) else ""
    if reg == "npm":
        d = get(f"https://registry.npmjs.org/{pkg.replace('/', '%2F')}")
        if d is None: return "sem_registro", None, "npm 404"
        if V in d.get("versions", {}):
            return "chegou", d.get("time", {}).get(V), "deprecated" if d["versions"][V].get("deprecated") else ""
        return "nao_chegou", None, f"{len(d.get('versions', {}))} versions"
    if reg == "rubygems":
        d = get(f"https://rubygems.org/api/v1/versions/{urllib.parse.quote(pkg)}.json")
        if d is None: return "sem_registro", None, "rubygems 404"
        for x in d:
            if x["number"] == V: return "chegou", x.get("created_at"), "yanked" if x.get("yanked") else ""
        return "nao_chegou", None, f"{len(d)} versions"
    if reg == "pubdev":
        d = get(f"https://pub.dev/api/packages/{urllib.parse.quote(pkg)}")
        if d is None: return "sem_registro", None, "pub 404"
        for x in d["versions"]:
            if x["version"] == V: return "chegou", x.get("published"), ""
        return "nao_chegou", None, f"{len(d['versions'])} versions"
    if reg == "crates":
        d = get(f"https://crates.io/api/v1/crates/{urllib.parse.quote(pkg)}/versions?per_page=100")
        if d is None: return "sem_registro", None, "crates 404"
        for x in d["versions"]:
            if x["num"] == V: return "chegou", x.get("created_at"), "yanked" if x.get("yanked") else ""
        return "nao_chegou", None, f"{len(d['versions'])}+ versions"
    if reg == "fdroid":
        fd = fdroid(); found = False; seen = 0
        for idx in ("main", "archive"):
            p = fd[idx].get(pkg)
            if not p: continue
            found = True
            for ver in p.get("versions", {}).values():
                seen += 1
                vn = ver.get("manifest", {}).get("versionName", "")
                if vn.lstrip("vV") == V:
                    add = ver.get("added")
                    return "chegou", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(add / 1000)) if add else None, idx
        return ("nao_chegou", None, f"{seen} versions") if found else ("sem_registro", None, "not in f-droid index")
    raise ValueError(reg)

def raw(repo, tag, path):
    try:
        with urllib.request.urlopen(urllib.request.Request(
            f"https://raw.githubusercontent.com/{repo}/{urllib.parse.quote(tag, safe='@')}/{path}", headers=UA), timeout=60) as r:
            return r.read().decode("utf-8", "replace")
    except Exception:
        return None

def from_manifest(repo, tag):
    if tag.startswith("@"):
        return "npm", tag.rsplit("@", 1)[0], "tag prefix"
    t = raw(repo, tag, "package.json")
    if t:
        try:
            j = json.loads(t)
            if j.get("name") and not j.get("private"): return "npm", j["name"], "package.json"
        except Exception: pass
    t = raw(repo, tag, "pyproject.toml")
    if t:
        m = re.search(r'(?ms)^\[project\].*?^name\s*=\s*"([^"]+)"', t)
        if m: return "pypi", m.group(1), "pyproject"
    t = raw(repo, tag, "Cargo.toml")
    if t:
        m = re.search(r'(?ms)^\[package\].*?^name\s*=\s*"([^"]+)"', t)
        if m and not re.search(r"(?m)^publish\s*=\s*false", t): return "crates", m.group(1), "Cargo.toml"
    t = raw(repo, tag, "pubspec.yaml")
    if t:
        m = re.search(r"(?m)^name:\s*(\S+)", t)
        if m and not re.search(r"(?m)^publish_to:\s*['\"]?none", t): return "pubdev", m.group(1), "pubspec"
    return None, None, "no publishable manifest"

def main():
    units = list(csv.DictReader(open(sys.argv[1]), delimiter="\t"))
    with open(sys.argv[3], "w") as out:
        for u in units:
            V = tagver(u["tag"]); reg, pkg, how = u["registry"], u["package"], "list"
            try:
                if reg == "manifest":
                    reg, pkg, how = from_manifest(u["repo"], u["tag"])
                if reg is None:
                    res = ("sem_registro", None, how)
                else:
                    res = q(reg, pkg, V)
                    if res[0] == "sem_registro" and how != "list": res = ("sem_registro", None, res[2] + f" ({how})")
            except Exception as e:
                res = ("inconclusivo", None, str(e)[:200])
            row = dict(u, registry_used=reg, package_used=pkg, resolved_by=how, version=V,
                       outcome=res[0], published=res[1], note=res[2])
            out.write(json.dumps(row, ensure_ascii=False) + "\n"); out.flush()
            print(u["case"], reg, pkg, V, res[0], res[2], file=sys.stderr)

if __name__ == "__main__":
    main()
