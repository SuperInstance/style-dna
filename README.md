# style-dna — Musical DNA Extraction, Comparison & Morphing

Extract a composer's irreducible musical fingerprint from MIDI files, compare styles mathematically, and morph music toward target styles. Every composer has a DNA signature — topological, dynamical, and statistical invariants that survive across their entire corpus.

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
sim = bach.similarity_to(PERSONALITIES["Chopin"])
print(f"Bach ↔ Chopin similarity: {sim:.3f}")

# Morph a piece toward Coltrane's style
morpher = StyleMorpher()
output = morpher.morph("input.mid", PERSONALITIES["Coltrane"], blend=0.7)
print(f"Morphed output: {output}")
```

## The Key Idea

Two composers can share the same key, tempo, and instrumentation — and still sound completely different. The difference lives in their deep invariants: topological structure (Betti numbers), dynamical regime (Lyapunov exponent), information density (entropy ratio), and tonal journey breadth (holonomy range). These are the irreducible dimensions of musical style.

Style-dna extracts these invariants as a `StyleTile` — a frozen dataclass with 25+ fields. The similarity metric is cosine distance over this high-dimensional vector. Morphing applies per-layer adjustments (register, rhythm, harmony, contour) controlled by a single blend parameter.

## Deep Invariants

| Invariant | What It Measures | Typical Values |
|-----------|-----------------|----------------|
| `betti_numbers` | Topological complexity (components + loops) | Bach: structured, Coltrane: complex |
| `lyapunov_exponent` | Predictability vs chaos | Bach ≈ 0.01, Coltrane ≈ 0.30 |
| `entropy_ratio` | Deep structure vs surface variety | Bach ≈ 0.29 |
| `mutual_information` | Between-voice dependency | Higher = more coordinated voices |
| `holonomy_range` | Tonal journey breadth | Wider = more modulation |
| `chinese_liubai_rate` | Silence / negative-space fraction (留白) | Debussy: high, Bach: low |

## API Reference

### StyleExtractor

```python
ext = StyleExtractor()
tile = ext.extract(midi_paths=["piece1.mid", ...], composer="Name", era="baroque")
# → StyleTile (frozen dataclass)
```

### StyleTile

```python
tile.similarity_to(other)          # → float (cosine similarity, 0-1)
tile.melodic_interval_profile      # → dict[int, float]
tile.rhythmic_profile              # → dict[float, float]
tile.harmonic_profile              # → dict[str, float]
tile.register_center               # → float (mean MIDI pitch)
tile.betti_numbers                 # → list[int]
tile.lyapunov_exponent             # → float
tile.entropy_ratio                 # → float
```

### StyleMorpher

```python
morpher = StyleMorpher(seed=42)
output = morpher.morph(
    midi_path="input.mid",
    target=PERSONALITIES["Coltrane"],
    blend=0.7,              # 0=no change, 1=full morph
    output_path="out.mid",  # auto-generated if None
)
```

### PERSONALITIES

Pre-extracted tiles: Bach, Chopin, Joplin, Debussy, Coltrane.

## Documentation

- [User Guide](docs/USER-GUIDE.md) — Complete usage documentation
- [Developer Guide](docs/DEVELOPER-GUIDE.md) — Contributing and internals
- [Examples](examples/) — Style morphing demo

## Related

- [constraint-theory-core](https://github.com/SuperInstance/constraint-theory-core) — The mathematical primitives underneath
- [holonomy-harmony](https://github.com/SuperInstance/holonomy-harmony) — Chord progression analysis via holonomy
- [flux-tensor-midi](https://github.com/SuperInstance/flux-tensor-midi) — 4D tensor representation of MIDI events

## License

MIT
