# User Guide — style-dna

Musical DNA extraction, analysis, and style morphing. Extract a composer's irreducible fingerprint from MIDI files, compare styles mathematically, and morph music toward target styles.

## Installation

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
    midi_paths=["bach_invention_1.mid", "bach_invention_8.mid"],
    composer="Bach",
    era="baroque",
)

# Extract Mozart's DNA
mozart = ext.extract(
    midi_paths=["mozart_sonata_k545.mid"],
    composer="Mozart",
    era="classical",
)

# Compare: cosine similarity over high-dimensional DNA vectors
sim = bach.similarity_to(mozart)
print(f"Bach ↔ Mozart similarity: {sim:.3f}")
```

## StyleTile

A `StyleTile` is a frozen dataclass — the irreducible fingerprint of a composer's style:

```python
from style_dna import StyleTile

print(bach.melodic_interval_profile)    # Distribution of melodic intervals
print(bach.rhythmic_profile)            # Duration distribution
print(bach.harmonic_profile)            # Chord quality distribution
print(bach.register_center)             # Average pitch register
print(bach.register_range)              # Pitch range

# Deep mathematical invariants
print(bach.betti_numbers)               # Topological complexity
print(bach.lyapunov_exponent)           # Chaos/predictability
print(bach.entropy_ratio)               # Information density
print(bach.mutual_information)          # Voice dependency structure
print(bach.holonomy_range)              # Tonal journey breadth
```

## Built-in Personalities

Pre-extracted style profiles for famous composers:

```python
from style_dna import PERSONALITIES

for name, tile in PERSONALITIES.items():
    print(f"{name}: entropy={tile.entropy_ratio:.3f}, register={tile.register_center:.1f}")
```

## Style Morphing

Transform a MIDI file toward a target style:

```python
from style_dna import StyleMorpher

morpher = StyleMorpher(seed=42)

# Morph a Bach piece toward Coltrane's style
output = morpher.morph(
    midi_path="bach_fugue.mid",
    target=PERSONALITIES["coltrane"],
    blend=0.7,           # 70% Coltrane, 30% original
    output_path="bach_to_coltrane.mid",
)
print(f"Morphed output: {output}")
```

The `blend` parameter controls morphing intensity:
- `0.0` — no change (original)
- `0.5` — equal blend
- `1.0` — full morph to target style

Morphing applies per-layer adjustments: register, rhythm, timing, harmony, and melodic contour.

## API Reference

### StyleExtractor

| Method | Returns | Description |
|--------|---------|-------------|
| `.extract(midi_paths, composer, era)` | `StyleTile` | Extract DNA from MIDI corpus |

### StyleTile

| Method | Returns | Description |
|--------|---------|-------------|
| `.similarity_to(other)` | `float` | Cosine similarity (0-1) |
| `.melodic_interval_profile` | `dict` | Interval → frequency |
| `.rhythmic_profile` | `dict` | Duration → frequency |
| `.harmonic_profile` | `dict` | Quality → frequency |
| `.register_center` | `float` | Mean pitch |
| `.register_range` | `float` | Pitch span |
| `.betti_numbers` | `list` | Topological invariants |
| `.lyapunov_exponent` | `float` | Chaos measure |
| `.entropy_ratio` | `float` | Information density |

### StyleMorpher

| Method | Returns | Description |
|--------|---------|-------------|
| `.morph(midi_path, target, blend=1.0, output_path=None)` | `str` | Morphed MIDI path |
