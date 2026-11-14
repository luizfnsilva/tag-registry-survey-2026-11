# Tag/version mismatches and package registries (2026-11-14)

Of release tags that name a version their commit does not declare, how many had that version
published on a package registry? The question and the rules were written before any registry was
queried (`records/PREREGISTRATION.md`, in Portuguese). Two amendments follow it; the second came after
the results were seen and is marked post hoc.

**Units.** 117 tags from 2026, each confirmed by a double-coded manual audit (κ 0.81) as naming a
version its commit does not declare (`data/units.tsv`). Up to 40 repositories per sample arm, one tag
each: these are counts in a sample, not population rates.

| Registry | Version published | Not counted |
|---|---|---|
| PyPI | 8 of 34 | |
| npm | 8 of 20 | 1 not on npm |
| pub.dev | 4 of 5 | |
| RubyGems | 1 of 5 | |
| crates.io | 1 of 2 | |
| F-Droid (post hoc) | 1 of 16 | 28 apps not yet on F-Droid at the tag date |
| none | | 6 with no registry |
| **Total** | **23 of 82 (28%, 95% CI 20–39%)** | 35 |

Where the registry gives a date, the version was published the same day as the tag (median 0 days,
range −1 to 6). One of the 23 was later yanked.

**Where the published artifact came from**, only where the registry records it, never inferred:
npm `gitHead` 3 from the tag's commit, 2 from another commit, 3 not recorded; crates.io
`.cargo_vcs_info.json` 1 from another commit; F-Droid build `commit:` 1. For PyPI the artifact's `.py`
files were compared with the tag's tree: 4 identical, 4 differ. pub.dev and RubyGems record no commit.

**F-Droid.** The F-Droid indexes keep only recent versions, so absence from the index was not evidence
(found by a positive control). Amendment 2 moved the source to the build history in `fdroiddata`,
pinned at `a64de301`. Read the F-Droid row as post hoc.

**Not measured.** "Before anyone noticed": there is no date for noticing.

## Reproduce

```bash
python3 scripts/measure.py data/units.tsv CACHE_DIR data/results.jsonl
python3 scripts/fdroid_builds.py        # amendment 2, from the folder holding results.jsonl
python3 scripts/publish_commit.py       # amendment 1
```

Registries change: deleted versions and re-cut files will differ from these results, which are as
served on 2026-11-14. The sealed pre-registration's original sha256 is
`64db72452a04231009a745bc2d373b5e11e96dc806f1aeb5636d5cdd4046cf4d`; this copy differs from it only in one line,
where a path in a private repository was removed. The audit that produced the 117 units is not public.

Data and text: CC BY 4.0. Scripts: Apache-2.0.
