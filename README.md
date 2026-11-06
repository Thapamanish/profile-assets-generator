# Profile assets generator

Private source for the animated SVG assets published in `Thapamanish/Thapamanish`.

## Generate locally

```bash
python3 scripts/generate_assets.py
```

Generated files are written to `assets/` and intentionally ignored by Git.

## Publish to the public profile repository

```bash
./publish.sh /absolute/path/to/local/Thapamanish-clone
```

The publisher regenerates the SVGs, copies only `header.svg`, `typing.svg`, and
`journey.svg` to the public repository's existing `assets/` directory, commits,
and pushes `master`. It does not change public asset paths or names.
