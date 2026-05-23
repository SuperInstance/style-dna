# style-dna

Musical DNA extraction, analysis, and style morphing system. Extract a composer's irreducible musical fingerprint from MIDI files, compare styles mathematically, and morph music toward target styles.

## What It Does

- **Extract** a `StyleTile` — a frozen dataclass capturing melodic, rhythmic, harmonic, register, and deep mathematical invariants (Betti numbers, Lyapunov exponent, entropy ratio, mutual information, holonomy range, 留白 rate) from any corpus of MIDI files
- **Compare** composers via cosine similarity over high-dimensional DNA vectors
- **Morph** MIDI files toward target styles with controllable blend
- **Pre-built tiles** for Bach, Chopin, Joplin, Debussy, and Coltrane based on musicological research

## Quick Start

```python
from style_dna import StyleExtractor, StyleMorpher, PERSONALITIES

# Extract from your MIDI files
ext = StyleExtractor()
tile = ext.extract(["piece1.mid", "piece2.mid"], composer="MyStyle", era="modern")

# Compare to Bach
similarity = tile.similarity(PERSONALITIES["Bach"])
print(f"Similarity to Bach: {similarity:.3f}")

# Morph toward Joplin
morpher = StyleMorpher()
output = morpher.morph("input.mid", PERSONALITIES["Joplin"], blend=0.8)
```

## Architecture

```
style_dna/
├── tile.py           # StyleTile dataclass (25+ fields)
├── extract.py        # StyleExtractor — full pipeline with deep invariants
├── morph.py          # StyleMorpher — per-layer MIDI transformation
├── personalities.py  # Pre-built tiles: Bach, Chopin, Joplin, Debussy, Coltrane
└── __init__.py

tests/
└── test_style_dna.py # Full test suite

examples/
└── demo_morph.py     # Interactive demo
```

## Deep Invariants

Beyond basic statistics, each StyleTile captures:

| Invariant | What it measures |
|-----------|-----------------|
| `betti_numbers` | Topological fingerprint — connected components and loops in melodic contour |
| `euler_characteristic` | β₀ − β₁ per 100 notes; negative = composed/structured |
| `lyapunov_exponent` | Dynamical regime: quasi-periodic (Bach ≈ 0.01) to chaotic (Coltrane ≈ 0.30) |
| `entropy_ratio` | H∞/H₁ — deep structure (Bach ≈ 0.29) vs surface variety |
| `mutual_information` | Between-voice information sharing in multi-track MIDI |
| `holonomy_range` | How far pitches drift from estimated key center |
| `chinese_liubai_rate` | Silence / negative-space fraction (留白) |

## Install

```bash
pip install -e .
# or just: pip install mido
```

## Run Tests

```bash
cd style-dna
python -m pytest tests/ -v
```

## Run Demo

```bash
python examples/demo_morph.py
```

## License

MIT
