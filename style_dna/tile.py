"""Enhanced StyleTile — a composer's complete musical DNA fingerprint."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple
import json
import math


@dataclass(frozen=True)
class StyleTile:
    """
    A composer's musical DNA, extracted from a corpus of MIDI files.

    This frozen, serializable snapshot captures every musical parameter
    the style-dna ecosystem cares about: melodic, rhythmic, harmonic,
    register, timing, and deep mathematical invariants.
    """

    # ── Identity ──
    composer: str
    era: str

    # ── Melodic DNA ──
    interval_distribution: Dict[str, float]   # semitone → probability
    melodic_range_semitones: int
    mean_interval: float
    step_vs_leap_ratio: float                 # steps (≤2 semitones) vs leaps
    consonance_rate: float                    # 0-1
    dissonance_rate: float

    # ── Rhythmic DNA ──
    duration_distribution: Dict[str, float]   # "whole","half",... → prob
    syncopation_rate: float                   # 0-1
    mean_note_density: float                  # notes per beat
    rhythmic_entropy: float                   # complexity measure

    # ── Timing DNA ──
    timing_precision_ms: float                # timing tightness
    swing_factor: float                       # 0 straight, 1 full swing

    # ── Register DNA ──
    pitch_center: float                       # weighted average MIDI pitch
    pitch_range: Tuple[int, int]              # (low, high)

    # ── Density ──
    notes_per_bar: float

    # ── Topological / Dynamical Invariants ──
    betti_numbers: Tuple[int, int] = (0, 0)
    # β₀ = connected components in melodic contour graph
    # β₁ = independent loops (recurring melodic patterns)

    euler_characteristic: float = 0.0
    # Per-100-notes: β₀ − β₁. Negative = "composed" (lots of recurring
    # patterns creating loops). Bach ≈ −10, Coltrane ≈ −1.

    lyapunov_exponent: float = 0.0
    # Largest Lyapunov exponent from interval sequence.
    # <0 = convergent, ≈0 = quasi-periodic, >0 = chaotic.
    # Bach ≈ 0.01, Coltrane ≈ 0.30

    entropy_ratio: float = 0.0
    # H∞ / H₁ — ratio of limiting entropy to first-order entropy.
    # Low = deep structure (Bach ≈ 0.29), high = surface variety.

    mutual_information: float = 0.0
    # Between-voice information sharing for multi-track MIDI.
    # Higher = more contrapuntal independence / information exchange.

    swing_frequency: float = 0.0
    # If swing is present, estimated dominant frequency of swing cycle.

    holonomy_range: Tuple[float, float] = (0.0, 0.0)
    # (min, max) holonomy drift from key center across corpus.

    chinese_liubai_rate: float = 0.0
    # Silence / negative-space fraction. "留白" (liúbái).
    # Higher = more breathing room.

    # ── Metadata ──
    corpus_size: int = 0
    total_bars: int = 0

    def to_json(self, path: str | None = None) -> str:
        """Serialize to JSON string, optionally writing to path."""
        data = {k: v for k, v in self.__dict__.items()}
        text = json.dumps(data, indent=2, default=str)
        if path:
            with open(path, 'w') as f:
                f.write(text)
        return text

    @classmethod
    def from_json(cls, source: str) -> 'StyleTile':
        """Deserialize from JSON file path or JSON string."""
        try:
            with open(source) as f:
                data = json.load(f)
        except (FileNotFoundError, OSError):
            data = json.loads(source)
        # Convert lists back to tuples
        for key in ('pitch_range', 'betti_numbers', 'holonomy_range'):
            if key in data and isinstance(data[key], list):
                data[key] = tuple(data[key])
        return cls(**data)

    def _numeric_vector(self) -> list[float]:
        """All numeric fields as a flat vector for similarity comparison."""
        return [
            self.melodic_range_semitones,
            self.mean_interval,
            self.step_vs_leap_ratio,
            self.syncopation_rate,
            self.mean_note_density,
            self.rhythmic_entropy,
            self.consonance_rate,
            self.dissonance_rate,
            self.timing_precision_ms,
            self.swing_factor,
            self.pitch_center,
            self.notes_per_bar,
            self.pitch_range[0],
            self.pitch_range[1],
            self.betti_numbers[0],
            self.betti_numbers[1],
            self.euler_characteristic,
            self.lyapunov_exponent,
            self.entropy_ratio,
            self.mutual_information,
            self.swing_frequency,
            self.holonomy_range[0],
            self.holonomy_range[1],
            self.chinese_liubai_rate,
        ]

    def similarity(self, other: 'StyleTile') -> float:
        """Cosine similarity over numeric fields. 1.0 = identical direction."""
        v1 = self._numeric_vector()
        v2 = other._numeric_vector()
        dot = sum(a * b for a, b in zip(v1, v2))
        mag1 = math.sqrt(sum(a * a for a in v1))
        mag2 = math.sqrt(sum(b * b for b in v2))
        if mag1 == 0 or mag2 == 0:
            return 0.0
        return round(dot / (mag1 * mag2), 4)

    def diff(self, other: 'StyleTile') -> Dict[str, float]:
        """Return field-by-field difference (other - self)."""
        v1 = self._numeric_vector()
        names = [
            'melodic_range', 'mean_interval', 'step_leap', 'syncopation',
            'density', 'rhythmic_entropy', 'consonance', 'dissonance',
            'timing_ms', 'swing', 'pitch_center', 'notes_per_bar',
            'pitch_lo', 'pitch_hi', 'betti0', 'betti1', 'euler',
            'lyapunov', 'entropy_ratio', 'mutual_info', 'swing_freq',
            'holonomy_min', 'holonomy_max', 'liubai',
        ]
        v2 = other._numeric_vector()
        return {n: round(b - a, 4) for n, a, b in zip(names, v1, v2)}
