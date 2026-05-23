"""Enhanced StyleExtractor — extract musical DNA from MIDI corpora."""

from __future__ import annotations

import math
from collections import Counter
from typing import Dict, List, Tuple

import mido

from .tile import StyleTile


class StyleExtractor:
    """
    Extract a StyleTile from a corpus of MIDI files.

    Usage::

        ext = StyleExtractor()
        tile = ext.extract(["bach_fugue_1.mid", ...], composer="Bach", era="baroque")
    """

    def extract(
        self,
        midi_paths: List[str],
        composer: str,
        era: str,
    ) -> StyleTile:
        """Analyze a corpus and return a StyleTile."""
        all_intervals: list[int] = []
        all_durations: list[float] = []
        all_pitches: list[int] = []
        all_onsets: list[float] = []
        all_velocities: list[int] = []
        track_notes: dict[int, list[tuple[float, int]]] = {}  # track -> [(onset, pitch)]

        valid = 0
        for path in midi_paths:
            try:
                mid = mido.MidiFile(path)
            except Exception:
                continue
            intervals, durations, pitches, onsets, velocities, tnotes = self._parse_midi(mid)
            if not pitches:
                continue
            all_intervals.extend(intervals)
            all_durations.extend(durations)
            all_pitches.extend(pitches)
            all_onsets.extend(onsets)
            all_velocities.extend(velocities)
            for trk, notes in tnotes.items():
                track_notes.setdefault(trk, []).extend(notes)
            valid += 1

        if not all_pitches:
            raise ValueError(f"No notes found in {len(midi_paths)} MIDI files")

        total_beats = max(all_onsets) if all_onsets else 1.0
        total_bars = max(1, int(total_beats / 4))

        # ── Melodic DNA (per-voice intervals only) ──
        voice_intervals: list[int] = []
        for tid, tnotes in track_notes.items():
            tnotes.sort(key=lambda x: x[0])  # sort by onset
            for i in range(len(tnotes) - 1):
                voice_intervals.append(tnotes[i + 1][1] - tnotes[i][1])
        # Fall back to all_intervals if no per-track intervals
        melodic_intervals = voice_intervals if voice_intervals else all_intervals

        interval_dist = self._distribution(melodic_intervals)
        mean_int = sum(abs(i) for i in melodic_intervals) / len(melodic_intervals) if melodic_intervals else 0
        steps = sum(1 for i in melodic_intervals if abs(i) <= 2)
        step_leap = steps / len(melodic_intervals) if melodic_intervals else 0

        CONSONANT = {0, 3, 4, 7, 8, 9, 12}
        consonant = sum(1 for i in all_intervals if abs(i) % 12 in CONSONANT)
        cons_rate = consonant / len(all_intervals) if all_intervals else 0

        # ── Rhythmic DNA ──
        dur_dist = self._duration_names(all_durations)
        sync = self._syncopation_rate(all_onsets)
        density = len(all_pitches) / total_beats if total_beats > 0 else 1
        entropy = self._entropy(dur_dist.values())

        # ── Register ──
        center = sum(all_pitches) / len(all_pitches)
        lo, hi = min(all_pitches), max(all_pitches)

        # ── Timing ──
        timing_ms = self._timing_precision(all_onsets)
        swing = self._detect_swing(all_onsets)

        # ── Deep invariants ──
        betti = self._compute_betti_numbers(all_pitches, all_onsets)
        lyap = self._compute_lyapunov(all_intervals)
        ent_ratio = self._compute_entropy_ratio(all_pitches)
        mi = self._compute_mutual_information(track_notes)
        holo = self._compute_holonomy_range(all_pitches)
        liubai = self._compute_liubai_rate(all_durations, total_beats)
        euler = (betti[0] - betti[1]) * 100.0 / max(len(all_pitches), 1)
        swing_freq = self._compute_swing_frequency(all_onsets, swing)

        return StyleTile(
            composer=composer,
            era=era,
            interval_distribution={str(k): v for k, v in interval_dist.items()},
            melodic_range_semitones=hi - lo,
            mean_interval=round(mean_int, 2),
            step_vs_leap_ratio=round(step_leap, 3),
            consonance_rate=round(cons_rate, 3),
            dissonance_rate=round(1 - cons_rate, 3),
            duration_distribution=dur_dist,
            syncopation_rate=round(sync, 3),
            mean_note_density=round(density, 2),
            rhythmic_entropy=round(entropy, 3),
            timing_precision_ms=round(timing_ms, 1),
            swing_factor=round(swing, 3),
            pitch_center=round(center, 1),
            pitch_range=(lo, hi),
            notes_per_bar=round(density * 4, 1),
            betti_numbers=betti,
            euler_characteristic=round(euler, 2),
            lyapunov_exponent=round(lyap, 4),
            entropy_ratio=round(ent_ratio, 4),
            mutual_information=round(mi, 4),
            swing_frequency=round(swing_freq, 4),
            holonomy_range=holo,
            chinese_liubai_rate=round(liubai, 4),
            corpus_size=valid,
            total_bars=total_bars,
        )

    # ── MIDI Parsing ──

    def _parse_midi(self, mid: mido.MidiFile):
        """Extract intervals, durations, pitches, onsets, velocities, per-track notes."""
        tpb = mid.ticks_per_beat
        pitches, onsets, durations, velocities = [], [], [], []
        track_notes: dict[int, list[tuple[float, int]]] = {}

        for track_idx, track in enumerate(mid.tracks):
            abs_time = 0
            note_ons: dict[int, tuple[int, int]] = {}  # pitch -> (start_tick, velocity)
            for msg in track:
                abs_time += msg.time
                if msg.type == 'note_on' and msg.velocity > 0:
                    note_ons[msg.note] = (abs_time, msg.velocity)
                elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                    if msg.note in note_ons:
                        start_tick, vel = note_ons.pop(msg.note)
                        dur = abs_time - start_tick
                        if dur > 0:
                            on = start_tick / tpb
                            pitches.append(msg.note)
                            onsets.append(on)
                            durations.append(dur / tpb)
                            velocities.append(vel)
                            track_notes.setdefault(track_idx, []).append((on, msg.note))

        # Sort by onset for interval computation
        paired = sorted(zip(onsets, pitches))
        intervals = [paired[i + 1][1] - paired[i][1] for i in range(len(paired) - 1)]

        # Filter out rests (note=0) from pitch collections to avoid corrupting
        # pitch_center and melodic_range metrics
        pitches_no_rests = [p for p in pitches if p > 0]
        if pitches_no_rests:
            # Replace all_pitches references downstream with filtered list
            pitches[:] = pitches_no_rests
            onsets_filtered = []
            # Rebuild paired without rests
            paired = sorted(zip(onsets, [p for p in pitches]))
            intervals = [paired[i + 1][1] - paired[i][1] for i in range(len(paired) - 1)]

        return intervals, durations, pitches, onsets, velocities, track_notes

    # ── Basic helpers ──

    def _distribution(self, values: list) -> dict:
        c = Counter(values)
        total = sum(c.values())
        return {k: round(v / total, 4) for k, v in c.items()}

    def _duration_names(self, durations: list[float]) -> dict[str, float]:
        names: list[str] = []
        for d in durations:
            if d >= 3.5:
                names.append("whole")
            elif d >= 1.5:
                names.append("half")
            elif d >= 0.75:
                names.append("quarter")
            elif d >= 0.35:
                names.append("eighth")
            else:
                names.append("sixteenth")
        c = Counter(names)
        total = len(names)
        return {k: round(v / total, 4) for k, v in c.items()}

    def _syncopation_rate(self, onsets: list[float]) -> float:
        if not onsets:
            return 0.0
        on_beat = sum(1 for o in onsets if abs(o - round(o)) < 0.05)
        return 1.0 - on_beat / len(onsets)

    def _entropy(self, probs) -> float:
        ps = [p for p in probs if p > 0]
        return -sum(p * math.log2(p) for p in ps) if ps else 0.0

    def _detect_swing(self, onsets: list[float]) -> float:
        if not onsets:
            return 0.0
        offsets = []
        for o in onsets:
            nearest_half = round(o * 2) / 2
            diff = o - nearest_half
            if abs(nearest_half - round(nearest_half) - 0.5) < 0.01:
                offsets.append(diff)
        if not offsets:
            return 0.0
        avg = sum(offsets) / len(offsets)
        return max(0.0, min(1.0, avg / 0.083))

    def _timing_precision(self, onsets: list[float]) -> float:
        """Estimate timing precision from deviation from grid."""
        if not onsets:
            return 10.0
        # Assume ~120 BPM → 1 beat = 500ms
        ms_per_beat = 500.0
        devs = [abs(o - round(o)) * ms_per_beat for o in onsets]
        return sum(devs) / len(devs) if devs else 10.0

    # ── Deep invariant computations ──

    def _compute_betti_numbers(self, pitches: list[int], onsets: list[float]) -> tuple[int, int]:
        """
        Simplified topological analysis of melodic contour using persistent homology.

        β₀ (connected components): Group notes into clusters by pitch proximity
        and temporal adjacency. Count distinct melodic "strands."

        β₁ (loops): Count recurring pitch contour patterns (sequences of up/down/same
        that repeat), which create topological loops in the contour space.
        """
        if len(pitches) < 3:
            return (1, 0)

        paired = sorted(zip(onsets, pitches))
        sorted_pitches = [p for _, p in paired]

        # β₀: count connected components in melodic contour
        # A component breaks when pitch jumps more than an octave
        components = 1
        for i in range(1, len(sorted_pitches)):
            if abs(sorted_pitches[i] - sorted_pitches[i - 1]) > 12:
                components += 1

        # β₁: detect recurring contour patterns (loops)
        # Encode contour as sequence of directions: +1 up, -1 down, 0 same
        contour = []
        for i in range(1, len(sorted_pitches)):
            diff = sorted_pitches[i] - sorted_pitches[i - 1]
            if diff > 0:
                contour.append(1)
            elif diff < 0:
                contour.append(-1)
            else:
                contour.append(0)

        # Count repeated substrings of length 3-8 as "loops"
        loops = 0
        for length in range(3, min(9, len(contour) // 2 + 1)):
            seen: set[tuple[int, ...]] = set()
            for start in range(len(contour) - length + 1):
                pattern = tuple(contour[start:start + length])
                if pattern in seen:
                    loops += 1
                else:
                    seen.add(pattern)

        # Normalize loops to reasonable range
        beta_1 = min(loops, len(sorted_pitches) // 10)
        return (components, beta_1)

    def _compute_lyapunov(self, intervals: list[int]) -> float:
        """
        Estimate largest Lyapunov exponent from interval sequence.

        Uses a simplified Rosenstein method: track divergence of nearby
        trajectories in the interval phase space.
        """
        if len(intervals) < 10:
            return 0.0

        # Build 2D phase space: (interval_n, interval_{n+1})
        abs_ints = [abs(i) for i in intervals]
        n = len(abs_ints) - 1
        if n < 5:
            return 0.0

        # Find nearest neighbors and track divergence
        divergences = []
        for i in range(n - 5):
            # Current point in phase space
            x1, y1 = abs_ints[i], abs_ints[i + 1]
            min_dist = float('inf')
            nn_idx = -1
            for j in range(n - 5):
                if abs(j - i) < 3:  # temporal separation requirement
                    continue
                d = math.sqrt((x1 - abs_ints[j]) ** 2 + (y1 - abs_ints[j + 1]) ** 2)
                if d < min_dist:
                    min_dist = d
                    nn_idx = j

            if nn_idx >= 0 and min_dist > 0:
                # Track divergence over next 5 steps
                for step in range(1, min(6, n - max(i, nn_idx))):
                    d_i = abs_ints[i + step]
                    d_j = abs_ints[nn_idx + step]
                    if d_j != 0:
                        divergences.append(math.log(abs(d_i - d_j) + 1) - math.log(min_dist + 1))

        if not divergences:
            return 0.0

        # Lyapunov ≈ average logarithmic divergence rate
        avg = sum(divergences) / len(divergences)
        # Clamp to reasonable range
        return max(-0.5, min(0.5, avg * 0.1))

    def _compute_entropy_ratio(self, pitches: list[int]) -> float:
        """
        Compute H∞ / H₁ — ratio of limiting entropy to first-order entropy.

        Low ratio → deep structure (predictable patterns).
        High ratio → surface variety.
        """
        if len(pitches) < 10:
            return 0.5

        # First-order entropy H₁: from individual pitch frequencies
        pitch_counts = Counter(pitches)
        total = len(pitches)
        h1 = -sum(
            (c / total) * math.log2(c / total)
            for c in pitch_counts.values()
        )

        # Approximate H∞ using bigram entropy (second order)
        bigrams = Counter(
            (pitches[i], pitches[i + 1]) for i in range(len(pitches) - 1)
        )
        bigram_total = len(pitches) - 1
        h2 = -sum(
            (c / bigram_total) * math.log2(c / bigram_total)
            for c in bigrams.values()
        )

        # H∞ is bounded by H₂ ≤ H∞ ≤ H₁
        # Use h2/h1 as approximation of the ratio
        if h1 == 0:
            return 0.5
        return max(0.0, min(1.0, h2 / h1))

    def _compute_mutual_information(self, track_notes: dict[int, list[tuple[float, int]]]) -> float:
        """
        Compute mutual information between voices (tracks) in multi-track MIDI.

        Higher values indicate more information sharing / contrapuntal interaction.
        """
        if len(track_notes) < 2:
            return 0.0

        tracks = list(track_notes.values())
        mi_values = []

        for i in range(len(tracks)):
            for j in range(i + 1, len(tracks)):
                # Quantize onsets to beats
                beats_i = Counter(int(on) for on, _ in tracks[i])
                beats_j = Counter(int(on) for on, _ in tracks[j])

                all_beats = set(beats_i.keys()) | set(beats_j.keys())
                n_beats = len(all_beats)
                if n_beats == 0:
                    continue

                # Joint and marginal probabilities
                joint = sum(
                    min(beats_i.get(b, 0), beats_j.get(b, 0))
                    for b in all_beats
                )
                total_i = sum(beats_i.values())
                total_j = sum(beats_j.values())

                if total_i == 0 or total_j == 0:
                    continue

                p_joint = joint / max(total_i, total_j)
                p_i = total_i / (n_beats * max(total_i, 1))
                p_j = total_j / (n_beats * max(total_j, 1))

                if p_joint > 0 and p_i > 0 and p_j > 0:
                    mi = p_joint * math.log2(p_joint / (p_i * p_j) + 1e-10)
                    mi_values.append(max(0, mi))

        return sum(mi_values) / len(mi_values) if mi_values else 0.0

    def _compute_holonomy_range(self, pitches: list[int]) -> tuple[float, float]:
        """
        Estimate holonomy drift from key center.

        Simplified: estimate key from most common pitch class, then measure
        how far pitches drift from it.
        """
        if not pitches:
            return (0.0, 0.0)

        # Estimate key center from most frequent pitch class
        pitch_classes = Counter(p % 12 for p in pitches)
        tonic = pitch_classes.most_common(1)[0][0]

        # Compute drift for each pitch
        drifts = []
        for p in pitches:
            pc = p % 12
            # Distance on circle of fifths (simplified: raw semitone distance)
            dist = min((pc - tonic) % 12, (tonic - pc) % 12)
            drifts.append(float(dist))

        return (round(min(drifts), 2), round(max(drifts), 2))

    def _compute_liubai_rate(self, durations: list[float], total_beats: float) -> float:
        """
        Compute silence / negative-space fraction (留白 liúbái).

        Estimated as 1 - (sum of durations / total span). More silence = higher rate.
        """
        if not durations or total_beats <= 0:
            return 0.0
        occupied = sum(durations)
        return max(0.0, 1.0 - occupied / total_beats)

    def _compute_swing_frequency(self, onsets: list[float], swing_factor: float) -> float:
        """Estimate dominant swing cycle frequency if swing is present."""
        if swing_factor < 0.05 or not onsets:
            return 0.0
        # Swing typically cycles every 2 beats (triplet feel)
        # Count how many 2-beat windows show alternating strong/weak patterns
        windows = 0
        swing_windows = 0
        max_onset = max(onsets)
        for beat_start in range(0, int(max_onset), 2):
            window_notes = [o for o in onsets if beat_start <= o < beat_start + 2]
            if len(window_notes) >= 2:
                windows += 1
                # Check for swing pattern: notes clustered near 0.0 and 0.67 of each beat
                for b in range(2):
                    beat_notes = [o - (beat_start + b) for o in window_notes
                                  if beat_start + b <= o < beat_start + b + 1]
                    if len(beat_notes) >= 2:
                        near_downbeat = sum(1 for o in beat_notes if o < 0.15)
                        near_offbeat = sum(1 for o in beat_notes if 0.5 < o < 0.85)
                        if near_downbeat > 0 and near_offbeat > 0:
                            swing_windows += 1

        if windows == 0:
            return 0.0
        ratio = swing_windows / windows
        return ratio  # Roughly: 1.0 = every window swings, 0.0 = no swing
