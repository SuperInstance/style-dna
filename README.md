# style-dna — Musical DNA Extraction, Comparison & Morphing

Extract a composer's irreducible musical fingerprint from MIDI corpora, compare styles mathematically, and morph music toward target styles. Every composer has a DNA signature — topological, dynamical, and statistical invariants that survive across their entire corpus.

## Install

```bash
pip install style-dna
```

Requires Python 3.10+, `mido`, `numpy`.

## Quick Start

```python
from style_dna import StyleExtractor, StyleMorpher, PERSONALITIES

# Extract Bach's DNA from a corpus
ext = StyleExtractor()
bach = ext.extract(
    ["bach_invention_1.mid", "bach_invention_8.mid"],
    composer="Bach",
    era="baroque",
)

# Compare to pre-built profiles
sim = bach.similarity(PERSONALITIES["Chopin"])
print(f"Bach ↔ Chopin similarity: {sim:.3f}")

# Morph a piece toward Coltrane's style
morpher = StyleMorpher()
output = morpher.morph("input.mid", PERSONALITIES["Coltrane"], blend=0.7)
print(f"Morphed output: {output}")
```

## The Key Idea

Two composers can share the same key, tempo, and instrumentation — and still sound completely different. The difference lives in **deep invariants**: topological structure (Betti numbers), dynamical regime (Lyapunov exponent), information density (entropy ratio), and tonal journey breadth (holonomy range). These are the irreducible dimensions of musical style.

Style-dna extracts these invariants as a `StyleTile` — a frozen dataclass with 25+ fields. Similarity is cosine distance over this high-dimensional vector. Morphing applies per-layer structural transformations (register, rhythm, harmony, contour) controlled by a single blend parameter.

## Deep Invariants

| Invariant | Field | What It Measures | Typical Range |
|-----------|-------|-----------------|---------------|
| Betti numbers | `betti_numbers` | Topological complexity: β₀ (melodic strands), β₁ (recurring contour loops) | Bach: (2, 15), Coltrane: (5, 4) |
| Euler characteristic | `euler_characteristic` | β₀ − β₁ per 100 notes. Negative = composed (recurring patterns) | Bach ≈ −10, Coltrane ≈ −1 |
| Lyapunov exponent | `lyapunov_exponent` | Predictability vs chaos in interval sequences | Bach ≈ 0.01, Coltrane ≈ 0.30 |
| Entropy ratio | `entropy_ratio` | H∞ / H₁ — deep structure vs surface variety | Bach ≈ 0.29, Debussy ≈ 0.55 |
| Mutual information | `mutual_information` | Between-voice dependency (contrapuntal coordination) | Higher = more coordinated |
| Holonomy range | `holonomy_range` | Tonal journey breadth (drift from key center) | Wider = more modulation |
| 留白 Liubái rate | `chinese_liubai_rate` | Silence / negative-space fraction | Debussy: 0.30, Bach: 0.15 |

## Pre-Built Personalities

| Composer | Era | Consonance | Syncopation | Lyapunov | Character |
|----------|-----|-----------|-------------|----------|-----------|
| **Bach** | Baroque | 0.93 | 0.05 | 0.01 | Quasi-periodic, deep structure, high step ratio |
| **Chopin** | Romantic | 0.78 | 0.15 | 0.10 | Bifurcation dynamics, wide rubato, expressive leaps |
| **Joplin** | Ragtime | 0.85 | 0.35 | 0.05 | Syncopated, swung rhythm, recognizable patterns |
| **Debussy** | Impressionist | 0.65 | 0.20 | 0.15 | Floating rhythm, chromatic, high entropy ratio |
| **Coltrane** | Jazz | 0.55 | 0.40 | 0.30 | Chaotic "sheets of sound", extreme syncopation |

```python
from style_dna import PERSONALITIES
bach = PERSONALITIES["Bach"]
coltrane = PERSONALITIES["Coltrane"]
print(bach.similarity(coltrane))  # cosine similarity
```

## API Reference

### StyleExtractor

```python
ext = StyleExtractor()
tile = ext.extract(
    midi_paths=["piece1.mid", "piece2.mid"],
    composer="Bach",
    era="baroque",
)
# → StyleTile (frozen dataclass, 25+ fields)
```

Extracts from each MIDI file:
- **Melodic DNA**: interval distribution, step-vs-leap ratio, consonance/dissonance rates, mean interval
- **Rhythmic DNA**: duration distribution, syncopation rate, note density, rhythmic entropy
- **Timing DNA**: timing precision (ms), swing factor
- **Register DNA**: pitch center, pitch range, notes per bar
- **Deep invariants**: Betti numbers, Euler characteristic, Lyapunov exponent, entropy ratio, mutual information, holonomy range, 留白 rate

### StyleTile

```python
tile.composer                    # "Bach"
tile.era                         # "baroque"
tile.interval_distribution       # {"0": 0.12, "1": 0.15, "2": 0.25, ...}
tile.consonance_rate             # 0.93
tile.lyapunov_exponent           # 0.01
tile.betti_numbers               # (2, 15)

tile.similarity(other)           # cosine similarity (0-1)
tile.diff(other)                 # field-by-field difference dict

tile.to_json("bach.json")        # serialize
StyleTile.from_json("bach.json") # deserialize
```

### StyleMorpher

Structural MIDI transformations — not cosmetic register shifts but deep morphing:

```python
morpher = StyleMorpher(seed=42)
output = morpher.morph(
    midi_path="input.mid",
    target=PERSONALITIES["Coltrane"],
    blend=0.7,               # 0=no change, 1=full morph
    output_path="out.mid",   # auto-generated if None
)
```

Transformations applied in order:
1. **Interval distribution** — rescale intervals toward target mean
2. **Consonance** — shift simultaneous intervals toward/away from consonance
3. **Step vs leap** — insert passing tones (more steps) or create leaps
4. **Durations** — reshape note lengths toward target distribution
5. **Syncopation** — move notes on/off beat
6. **Density** — add/remove notes per bar
7. **Register** — shift pitch center
8. **Velocity curve** — reshape dynamics (even → expressive or vice versa)

```python
# Morph toward multiple targets at once
outputs = morpher.batch_morph("input.mid", [BACH, JOPLIN, COLTRANE], blend=1.0)
```

## Architecture

```
style_dna/
├── __init__.py          # Exports: StyleTile, StyleExtractor, StyleMorpher, PERSONALITIES
├── tile.py              # StyleTile frozen dataclass (25+ fields, JSON serialization, similarity)
├── extract.py           # StyleExtractor (MIDI parsing, invariant computation)
├── morph.py             # StyleMorpher (8-layer structural transformation pipeline)
└── personalities.py     # Pre-built tiles: Bach, Chopin, Joplin, Debussy, Coltrane
```

## Documentation

- [User Guide](docs/USER-GUIDE.md) — Complete usage documentation
- [Developer Guide](docs/DEVELOPER-GUIDE.md) — Contributing and internals
- [Demo](examples/demo_morph.py) — Style morphing + similarity matrix example

## Related Repos

- [constraint-theory-core](https://github.com/SuperInstance/constraint-theory-core) — Mathematical primitives underneath
- [holonomy-harmony](https://github.com/SuperInstance/holonomy-harmony) — Chord progression analysis via holonomy
- [flux-tensor-midi](https://github.com/SuperInstance/flux-tensor-midi) — 4D tensor representation of MIDI events
- [snapkit-v2](https://github.com/SuperInstance/snapkit-v2) — Eisenstein lattice snap + spectral analysis
- [spline-midi-smooth](https://github.com/SuperInstance/spline-midi-smooth) — Spline interpolation for MIDI automation

## License

MIT
