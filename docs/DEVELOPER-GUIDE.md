# Developer Guide — style-dna

## Architecture

```
style_dna/
├── __init__.py        # Public API exports
├── tile.py            # StyleTile frozen dataclass
├── extract.py         # StyleExtractor — MIDI corpus analysis
├── morph.py           # StyleMorpher — style transformation
└── personalities.py   # Pre-extracted composer profiles
```

### StyleTile Design

`StyleTile` is a frozen dataclass — immutable once created. This guarantees that extracted DNA never accidentally mutates. The tile captures:

- **Surface features**: interval distribution, rhythm, harmony, register
- **Deep invariants**: Betti numbers (topology), Lyapunov exponent (chaos), entropy ratio, mutual information, holonomy range

### Extraction Pipeline

1. Parse MIDI files → raw note events
2. Compute surface distributions (intervals, durations, pitches)
3. Build track-level dependency graph
4. Compute topological invariants (Betti numbers)
5. Estimate Lyapunov exponent from pitch sequence
6. Calculate entropy and mutual information
7. Freeze into StyleTile

### Morphing Strategy

Per-layer morphing with blend control:
- **Register**: shift mean pitch toward target
- **Rhythm**: adjust duration distribution
- **Timing**: add microtiming deviations matching target
- **Harmony**: substitute chords toward target's harmonic profile
- **Melodic contour**: reshape interval distribution

## Contributing

```bash
git clone https://github.com/SuperInstance/style-dna.git
cd style-dna
pip install -e ".[dev]"
pytest tests/ -v
```

### Adding a New Invariant

1. Add the field to `StyleTile` dataclass
2. Compute it in `StyleExtractor._compute_deep_invariants()`
3. Include it in the similarity vector in `StyleTile.similarity_to()`
4. Add morphing logic in `StyleMorpher._morph_layer()`
5. Update tests

### Code Style

- Frozen dataclasses for immutable data
- Type hints everywhere
- `mido` for MIDI I/O
- `numpy` for numerical computation
