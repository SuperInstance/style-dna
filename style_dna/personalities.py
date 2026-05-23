"""Pre-built composer personality tiles based on musicological research."""

from .tile import StyleTile

PERSONALITIES: dict[str, StyleTile] = {}


def _register(tile: StyleTile) -> StyleTile:
    """Register a personality tile and return it."""
    PERSONALITIES[tile.composer] = tile
    return tile


# ─── Johann Sebastian Bach ───────────────────────────────────────────────────
# Baroque master of counterpoint. Quasi-periodic dynamics (Lyapunov ≈ 0.01).
# Deep structure with low entropy ratio. High consonance, strict voice-leading.

BACH = _register(StyleTile(
    composer="Bach",
    era="baroque",
    interval_distribution={
        "0": 0.12, "1": 0.15, "2": 0.25, "3": 0.10, "4": 0.12,
        "5": 0.08, "7": 0.08, "12": 0.05, "-1": 0.05,
    },
    melodic_range_semitones=24,
    mean_interval=2.8,
    step_vs_leap_ratio=0.85,
    consonance_rate=0.93,
    dissonance_rate=0.07,
    duration_distribution={
        "whole": 0.05, "half": 0.30, "quarter": 0.40,
        "eighth": 0.20, "sixteenth": 0.05,
    },
    syncopation_rate=0.05,
    mean_note_density=3.5,
    rhythmic_entropy=1.2,
    timing_precision_ms=5.0,
    swing_factor=0.0,
    pitch_center=60.0,
    pitch_range=(48, 72),
    notes_per_bar=8.0,
    betti_numbers=(2, 15),
    euler_characteristic=-10.0,
    lyapunov_exponent=0.01,
    entropy_ratio=0.29,
    mutual_information=0.18,
    swing_frequency=0.0,
    holonomy_range=(0.0, 3.0),
    chinese_liubai_rate=0.15,
))


# ─── Frédéric Chopin ─────────────────────────────────────────────────────────
# Romantic piano poet. Bifurcation dynamics (Lyapunov ≈ 0.10).
# Wide rubato (timing_precision ≈ 25ms), moderate consonance, expressive leaps.

CHOPIN = _register(StyleTile(
    composer="Chopin",
    era="romantic",
    interval_distribution={
        "0": 0.08, "1": 0.12, "2": 0.18, "3": 0.12, "4": 0.10,
        "5": 0.08, "7": 0.10, "12": 0.08, "-2": 0.06, "-3": 0.08,
    },
    melodic_range_semitones=30,
    mean_interval=3.5,
    step_vs_leap_ratio=0.55,
    consonance_rate=0.78,
    dissonance_rate=0.22,
    duration_distribution={
        "whole": 0.08, "half": 0.25, "quarter": 0.30,
        "eighth": 0.25, "sixteenth": 0.12,
    },
    syncopation_rate=0.15,
    mean_note_density=4.0,
    rhythmic_entropy=1.8,
    timing_precision_ms=25.0,
    swing_factor=0.0,
    pitch_center=62.0,
    pitch_range=(40, 84),
    notes_per_bar=10.0,
    betti_numbers=(3, 8),
    euler_characteristic=-3.0,
    lyapunov_exponent=0.10,
    entropy_ratio=0.42,
    mutual_information=0.10,
    swing_frequency=0.0,
    holonomy_range=(0.0, 5.0),
    chinese_liubai_rate=0.25,
))


# ─── Scott Joplin ─────────────────────────────────────────────────────────────
# King of Ragtime. Syncopated (0.35), swung rhythm, moderate structure.
# Playful Lyapunov ≈ 0.05, recognizable ragtime patterns.

JOPLIN = _register(StyleTile(
    composer="Joplin",
    era="ragtime",
    interval_distribution={
        "0": 0.10, "1": 0.12, "2": 0.20, "3": 0.12, "4": 0.10,
        "5": 0.08, "7": 0.10, "12": 0.06, "-2": 0.06, "-3": 0.06,
    },
    melodic_range_semitones=22,
    mean_interval=3.2,
    step_vs_leap_ratio=0.60,
    consonance_rate=0.85,
    dissonance_rate=0.15,
    duration_distribution={
        "whole": 0.02, "half": 0.15, "quarter": 0.25,
        "eighth": 0.40, "sixteenth": 0.18,
    },
    syncopation_rate=0.35,
    mean_note_density=5.0,
    rhythmic_entropy=2.0,
    timing_precision_ms=10.0,
    swing_factor=0.25,
    pitch_center=58.0,
    pitch_range=(36, 79),
    notes_per_bar=12.0,
    betti_numbers=(2, 10),
    euler_characteristic=-5.0,
    lyapunov_exponent=0.05,
    entropy_ratio=0.38,
    mutual_information=0.12,
    swing_frequency=0.25,
    holonomy_range=(0.0, 4.0),
    chinese_liubai_rate=0.18,
))


# ─── Claude Debussy ──────────────────────────────────────────────────────────
# Impressionist innovator. Floating rhythm (timing_precision ≈ 40ms), high
# entropy ratio (0.55), chromatic harmony, low consonance (0.65).

DEBUSSY = _register(StyleTile(
    composer="Debussy",
    era="impressionist",
    interval_distribution={
        "0": 0.06, "1": 0.10, "2": 0.15, "3": 0.12, "4": 0.10,
        "5": 0.08, "6": 0.06, "7": 0.08, "11": 0.05, "12": 0.06,
        "-1": 0.05, "-2": 0.05, "-3": 0.04,
    },
    melodic_range_semitones=28,
    mean_interval=4.0,
    step_vs_leap_ratio=0.50,
    consonance_rate=0.65,
    dissonance_rate=0.35,
    duration_distribution={
        "whole": 0.12, "half": 0.28, "quarter": 0.30,
        "eighth": 0.20, "sixteenth": 0.10,
    },
    syncopation_rate=0.20,
    mean_note_density=3.8,
    rhythmic_entropy=2.2,
    timing_precision_ms=40.0,
    swing_factor=0.0,
    pitch_center=61.0,
    pitch_range=(36, 84),
    notes_per_bar=9.0,
    betti_numbers=(4, 6),
    euler_characteristic=-2.0,
    lyapunov_exponent=0.15,
    entropy_ratio=0.55,
    mutual_information=0.08,
    swing_frequency=0.0,
    holonomy_range=(0.0, 6.0),
    chinese_liubai_rate=0.30,
))


# ─── John Coltrane ────────────────────────────────────────────────────────────
# Jazz titan. "Sheets of sound" — high Lyapunov (0.30), extreme syncopation (0.40),
# low consonance (0.55), high mutual information (0.14) from interactive group playing.

COLTRANE = _register(StyleTile(
    composer="Coltrane",
    era="jazz",
    interval_distribution={
        "0": 0.05, "1": 0.08, "2": 0.12, "3": 0.10, "4": 0.08,
        "5": 0.07, "6": 0.05, "7": 0.08, "8": 0.05, "9": 0.04,
        "10": 0.04, "11": 0.05, "12": 0.05, "-1": 0.04, "-2": 0.05,
        "-3": 0.05,
    },
    melodic_range_semitones=32,
    mean_interval=4.5,
    step_vs_leap_ratio=0.35,
    consonance_rate=0.55,
    dissonance_rate=0.45,
    duration_distribution={
        "whole": 0.03, "half": 0.12, "quarter": 0.25,
        "eighth": 0.35, "sixteenth": 0.25,
    },
    syncopation_rate=0.40,
    mean_note_density=5.5,
    rhythmic_entropy=2.5,
    timing_precision_ms=15.0,
    swing_factor=0.35,
    pitch_center=63.0,
    pitch_range=(42, 84),
    notes_per_bar=14.0,
    betti_numbers=(5, 4),
    euler_characteristic=-1.0,
    lyapunov_exponent=0.30,
    entropy_ratio=0.58,
    mutual_information=0.14,
    swing_frequency=0.35,
    holonomy_range=(0.0, 6.0),
    chinese_liubai_rate=0.12,
))
