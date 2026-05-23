"""StyleMorpher — structural MIDI style transformation."""

from __future__ import annotations

import math
import random
from collections import Counter
from typing import Optional

import mido

from .extract import StyleExtractor
from .tile import StyleTile


class StyleMorpher:
    """
    Transform a MIDI file's style toward a target StyleTile.

    Unlike cosmetic morphing (register shifts), this performs structural
    transformations: interval rescaling, consonance shifting, duration
    reshaping, syncopation adjustment, and density changes.
    """

    # Consonant pitch-class intervals (unison, m3, M3, P4, P5, m6, M6, octave)
    CONSONANT_PC = {0, 3, 4, 7, 8, 9, 12}

    def __init__(self, extractor: StyleExtractor | None = None, seed: int | None = 42):
        self.extractor = extractor or StyleExtractor()
        self.rng = random.Random(seed)

    def morph(
        self,
        midi_path: str,
        target: StyleTile,
        blend: float = 0.7,
        output_path: str | None = None,
    ) -> str:
        """
        Transform a MIDI file toward a target style.

        Parameters
        ----------
        midi_path : str
            Path to input MIDI file.
        target : StyleTile
            Target style to morph toward.
        blend : float
            0.0 = no change, 1.0 = full morph.
        output_path : str | None
            Output path. Auto-generated if None.

        Returns
        -------
        str
            Path to morphed MIDI file.
        """
        mid = mido.MidiFile(midi_path)
        current = self.extractor.extract([midi_path], "input", "input")

        # 1. Extract all notes as structured data
        notes, meta_events = self._extract_notes(mid)
        if not notes:
            if output_path is None:
                output_path = midi_path.replace('.mid', f'_morphed_{target.composer.lower()}.mid')
            mid.save(output_path)
            return output_path

        # 2. Apply structural transformations in order
        notes = self._morph_interval_distribution(notes, current, target, blend)
        notes = self._morph_consonance(notes, current, target, blend)
        notes = self._morph_step_leap(notes, current, target, blend)
        notes = self._morph_durations(notes, current, target, blend)
        notes = self._morph_syncopation(notes, current, target, blend)
        notes = self._morph_density(notes, current, target, blend)
        notes = self._morph_register(notes, current, target, blend)
        notes = self._morph_velocity_curve(notes, current, target, blend)

        # 3. Rebuild MIDI
        mid = self._rebuild_midi(mid, notes, meta_events)

        if output_path is None:
            output_path = midi_path.replace(
                '.mid', f'_morphed_{target.composer.lower()}.mid'
            )
        mid.save(output_path)
        return output_path

    # ── Note extraction ──

    def _extract_notes(self, mid: mido.MidiFile):
        """
        Parse MIDI into a list of note events and meta events.

        Returns (notes, meta_events) where:
        - notes: list of dicts with onset_tick, pitch, duration_ticks, velocity, channel, track_idx
        - meta_events: list of (track_idx, tick, meta_msg_copy) for tempo/time_sig/etc
        """
        tpb = mid.ticks_per_beat
        notes = []
        meta_events = []

        for track_idx, track in enumerate(mid.tracks):
            abs_tick = 0
            note_ons: dict[tuple[int, int], tuple[int, int]] = {}  # (pitch, ch) -> (start_tick, vel)

            for msg in track:
                abs_tick += msg.time

                if msg.is_meta:
                    # Keep tempo, time sig, key sig, program change
                    if msg.type in ('set_tempo', 'time_signature', 'key_signature'):
                        meta_events.append((track_idx, abs_tick, msg.copy()))
                    continue

                if msg.type == 'program_change':
                    meta_events.append((track_idx, abs_tick, msg.copy()))
                    continue

                if msg.type == 'note_on' and msg.velocity > 0:
                    note_ons[(msg.note, msg.channel)] = (abs_tick, msg.velocity)

                elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                    key = (msg.note, msg.channel)
                    if key in note_ons:
                        start_tick, vel = note_ons.pop(key)
                        dur = abs_tick - start_tick
                        if dur > 0:
                            notes.append({
                                'onset_tick': start_tick,
                                'pitch': msg.note,
                                'duration_ticks': dur,
                                'velocity': vel,
                                'channel': msg.channel,
                                'track_idx': track_idx,
                            })

        notes.sort(key=lambda n: (n['onset_tick'], n['pitch']))
        return notes, meta_events

    # ── Structural transformations ──

    def _morph_interval_distribution(self, notes, current, target, blend):
        """
        Rescale intervals between consecutive notes (within each track)
        to match the target's mean_interval.

        If target has smaller mean_interval (Bach=2.8 vs jazz=4.5),
        shrink large leaps proportionally.
        """
        delta = (target.mean_interval - current.mean_interval) * blend
        if abs(delta) < 0.1:
            return notes

        # Group notes by track and sort by onset
        track_notes = {}
        for n in notes:
            track_notes.setdefault(n['track_idx'], []).append(n)

        # Sort each track's notes by onset
        for tidx in track_notes:
            track_notes[tidx].sort(key=lambda n: n['onset_tick'])

        # Build pitch map: for each note, compute interval to next note in same track
        pitch_changes = {}  # note_id (index in notes list) -> pitch delta to apply
        for tidx, tnotes in track_notes.items():
            for i in range(len(tnotes) - 1):
                curr_pitch = tnotes[i]['pitch']
                next_pitch = tnotes[i + 1]['pitch']
                interval = next_pitch - curr_pitch

                # Shrink/expand interval toward target mean
                if abs(interval) > 0:
                    # Scale factor: how much to reduce/expand this interval
                    ratio = target.mean_interval / max(current.mean_interval, 0.5)
                    # Blend between original (1.0) and target ratio
                    scaled_ratio = 1.0 + (ratio - 1.0) * blend * 0.5
                    new_interval = round(interval * scaled_ratio)
                    # Don't eliminate direction
                    if interval > 0:
                        new_interval = max(1, new_interval)
                    elif interval < 0:
                        new_interval = min(-1, new_interval)
                    else:
                        new_interval = 0

                    note_idx = notes.index(tnotes[i + 1])
                    pitch_changes[id(tnotes[i + 1])] = new_interval - interval

        # Apply pitch changes cumulatively (each note adjusts relative to previous)
        for tidx, tnotes in track_notes.items():
            cumulative_shift = 0
            for i in range(len(tnotes)):
                nid = id(tnotes[i])
                if nid in pitch_changes:
                    cumulative_shift += pitch_changes[nid]
                tnotes[i]['pitch'] = max(0, min(127, tnotes[i]['pitch'] + cumulative_shift))

        return notes

    def _morph_consonance(self, notes, current, target, blend):
        """
        Shift notes toward consonant intervals if target is more consonant,
        or toward dissonant intervals if target is more dissonant.

        For simultaneous notes (same onset within small window), adjust pitch
        to use consonant intervals from the bass note.
        """
        delta = (target.consonance_rate - current.consonance_rate) * blend
        if abs(delta) < 0.02:
            return notes

        tpb = 480  # approximate
        window = tpb // 8  # 1/8 beat window for simultaneity

        # Group notes by approximate onset (simultaneous notes)
        onset_groups = {}
        for n in notes:
            bucket = (n['onset_tick'] // window) * window
            onset_groups.setdefault((n['track_idx'], bucket), []).append(n)

        for (tidx, bucket), group in onset_groups.items():
            if len(group) < 2:
                continue

            # Sort by pitch (lowest = bass)
            group.sort(key=lambda n: n['pitch'])
            bass_pitch = group[0]['pitch']

            for i in range(1, len(group)):
                note = group[i]
                interval_pc = abs(note['pitch'] - bass_pitch) % 12
                is_consonant = interval_pc in self.CONSONANT_PC

                if delta > 0 and not is_consonant:
                    # Target is more consonant: shift to nearest consonant interval
                    best_shift = 0
                    best_dist = 999
                    for shift in [-2, -1, 1, 2]:
                        new_pitch = note['pitch'] + shift
                        new_interval_pc = abs(new_pitch - bass_pitch) % 12
                        if new_interval_pc in self.CONSONANT_PC and abs(shift) < best_dist:
                            best_shift = shift
                            best_dist = abs(shift)
                    if best_shift != 0 and self.rng.random() < abs(delta):
                        note['pitch'] = max(0, min(127, note['pitch'] + best_shift))

                elif delta < 0 and is_consonant:
                    # Target is more dissonant: occasionally shift to dissonant
                    if self.rng.random() < abs(delta) * 0.3:
                        shift = self.rng.choice([-1, 1])
                        note['pitch'] = max(0, min(127, note['pitch'] + shift))

        return notes

    def _morph_step_leap(self, notes, current, target, blend):
        """
        Convert leaps to steps (or vice versa) to match target step_vs_leap_ratio.

        Bach has 0.85 step ratio — mostly stepwise motion. Jazz has 0.35 — more leaps.
        When targeting Bach, replace large leaps with stepwise passing tones.
        """
        delta = (target.step_vs_leap_ratio - current.step_vs_leap_ratio) * blend
        if abs(delta) < 0.05:
            return notes

        # Group by track
        track_notes = {}
        for n in notes:
            track_notes.setdefault(n['track_idx'], []).append(n)
        for tidx in track_notes:
            track_notes[tidx].sort(key=lambda n: n['onset_tick'])

        new_notes = list(notes)
        extra_notes = []

        for tidx, tnotes in track_notes.items():
            for i in range(len(tnotes) - 1):
                curr = tnotes[i]
                nxt = tnotes[i + 1]
                interval = abs(nxt['pitch'] - curr['pitch'])

                # If it's a leap and we want more steps, insert passing tones
                if delta > 0 and interval > 4:
                    # Probability of inserting passing tone
                    if self.rng.random() < delta * 0.5:
                        # Direction of the leap
                        direction = 1 if nxt['pitch'] > curr['pitch'] else -1
                        # Insert 1-2 passing tones between
                        gap = nxt['pitch'] - curr['pitch']
                        n_steps = min(3, abs(gap) // 2)
                        for s in range(1, n_steps + 1):
                            pass_pitch = round(curr['pitch'] + gap * s / (n_steps + 1))
                            # Place at proportional time
                            time_frac = s / (n_steps + 1)
                            pass_onset = round(curr['onset_tick'] + time_frac * (nxt['onset_tick'] - curr['onset_tick']))
                            pass_duration = round(curr['duration_ticks'] * 0.5)
                            extra_notes.append({
                                'onset_tick': pass_onset,
                                'pitch': max(0, min(127, pass_pitch)),
                                'duration_ticks': max(1, pass_duration),
                                'velocity': round(curr['velocity'] * 0.8),
                                'channel': curr['channel'],
                                'track_idx': tidx,
                            })

                # If we want more leaps and it's a step, occasionally replace with leap
                elif delta < 0 and interval <= 2 and interval > 0:
                    if self.rng.random() < abs(delta) * 0.15:
                        direction = 1 if nxt['pitch'] > curr['pitch'] else -1
                        leap = direction * self.rng.choice([4, 5, 7])
                        nxt['pitch'] = max(0, min(127, curr['pitch'] + leap))

        new_notes.extend(extra_notes)
        new_notes.sort(key=lambda n: (n['onset_tick'], n['pitch']))
        return new_notes

    def _morph_durations(self, notes, current, target, blend):
        """
        Reshape note durations toward target distribution.

        If target uses more half notes and fewer eighth notes, stretch/contract
        durations accordingly.
        """
        # Compute desired duration scale factor
        # Approximate: mean duration in beats from distribution
        def mean_dur_beats(dist):
            mapping = {'whole': 4, 'half': 2, 'quarter': 1, 'eighth': 0.5, 'sixteenth': 0.25}
            total = sum(dist.get(k, 0) for k in mapping)
            if total == 0:
                return 1.0
            return sum(mapping.get(k, 0.5) * dist.get(k, 0) for k in mapping) / total

        cur_mean = mean_dur_beats(current.duration_distribution)
        tgt_mean = mean_dur_beats(target.duration_distribution)

        if cur_mean == 0:
            return notes

        ratio = tgt_mean / cur_mean
        scale = 1.0 + (ratio - 1.0) * blend * 0.5

        if abs(scale - 1.0) < 0.05:
            return notes

        for n in notes:
            n['duration_ticks'] = max(1, round(n['duration_ticks'] * scale))

        return notes

    def _morph_syncopation(self, notes, current, target, blend):
        """
        Move notes on/off beat to match target syncopation rate.

        Low syncopation (Bach 0.05) → quantize to beat grid.
        High syncopation (Coltrane 0.40) → shift some on-beat notes off-beat.
        """
        delta = (target.syncopation_rate - current.syncopation_rate) * blend
        if abs(delta) < 0.02:
            return notes

        # Estimate ticks per beat from note data
        # Use 480 as default (standard MIDI)
        tpb = 480

        for n in notes:
            beat_pos = n['onset_tick'] / tpb
            nearest_beat = round(beat_pos)
            is_on_beat = abs(beat_pos - nearest_beat) < 0.08

            if delta < 0 and not is_on_beat:
                # Target wants less syncopation: quantize to nearest beat or half-beat
                if self.rng.random() < abs(delta) * 0.5:
                    # Snap to nearest quarter beat
                    nearest_q = round(beat_pos * 4) / 4
                    n['onset_tick'] = round(nearest_q * tpb)

            elif delta > 0 and is_on_beat:
                # Target wants more syncopation: shift some notes off beat
                if self.rng.random() < delta * 0.3:
                    # Shift to off-beat (eighth note after beat)
                    offset = round(tpb * 0.5)  # half-beat
                    if self.rng.random() < 0.5:
                        offset = round(tpb * 0.75)  # dotted-eighth feel
                    n['onset_tick'] = max(0, n['onset_tick'] + offset)

        return notes

    def _morph_density(self, notes, current, target, blend):
        """
        Adjust note density (notes per bar) toward target.

        If target is denser, duplicate some notes with small offsets.
        If target is sparser, remove some short/repeated notes.
        """
        delta = (target.notes_per_bar - current.notes_per_bar) * blend
        if abs(delta) < 0.5:
            return notes

        if delta > 0:
            # Add density: duplicate some notes at slight offsets (ornamentation)
            extras = []
            for n in notes:
                if self.rng.random() < delta * 0.05:
                    # Add a neighbor tone or repeated note
                    offset = round(n['duration_ticks'] * 0.25)
                    pitch_shift = self.rng.choice([-2, -1, 1, 2])
                    extras.append({
                        'onset_tick': n['onset_tick'] + offset,
                        'pitch': max(0, min(127, n['pitch'] + pitch_shift)),
                        'duration_ticks': max(1, round(n['duration_ticks'] * 0.3)),
                        'velocity': round(n['velocity'] * 0.7),
                        'channel': n['channel'],
                        'track_idx': n['track_idx'],
                    })
            notes.extend(extras)
            notes.sort(key=lambda n: (n['onset_tick'], n['pitch']))

        elif delta < 0:
            # Reduce density: remove shortest notes probabilistically
            if len(notes) < 5:
                return notes
            durations = sorted(n['duration_ticks'] for n in notes)
            median_dur = durations[len(durations) // 2]
            removal_prob = abs(delta) * 0.03
            notes = [n for n in notes
                     if n['duration_ticks'] >= median_dur or self.rng.random() > removal_prob]

        return notes

    def _morph_register(self, notes, current, target, blend):
        """Shift pitch center toward target."""
        pitch_shift = (target.pitch_center - current.pitch_center) * blend * 0.5
        total_shift = round(pitch_shift)
        if total_shift == 0:
            return notes
        for n in notes:
            n['pitch'] = max(0, min(127, n['pitch'] + total_shift))
        return notes

    def _morph_velocity_curve(self, notes, current, target, blend):
        """
        Reshape velocity dynamics. Bach tends to be more even,
        jazz/romantic has wider dynamic range.
        """
        if not notes:
            return notes

        vels = [n['velocity'] for n in notes]
        cur_mean = sum(vels) / len(vels)
        cur_range = max(vels) - min(vels) if len(vels) > 1 else 0

        # Estimate target velocity characteristics from timing_precision
        # Tighter timing → more even dynamics (Bach)
        # Looser timing → more dynamic variation
        target_range = max(10, 127 * (1.0 - target.timing_precision_ms / 50.0))
        range_delta = (target_range - cur_range) * blend * 0.3

        if abs(range_delta) < 2:
            return notes

        if cur_range == 0:
            # All same velocity — add variation toward target
            for n in notes:
                variation = self.rng.randint(-int(abs(range_delta)/2), int(abs(range_delta)/2))
                n['velocity'] = max(1, min(127, n['velocity'] + variation))
        else:
            # Scale existing variation
            scale = 1.0 + range_delta / cur_range
            for n in notes:
                deviation = n['velocity'] - cur_mean
                n['velocity'] = max(1, min(127, round(cur_mean + deviation * scale)))

        return notes

    # ── MIDI rebuild ──

    def _rebuild_midi(self, orig_mid, notes, meta_events):
        """
        Rebuild a MIDI file from transformed note data.

        Groups notes by original track, then creates note_on/note_off pairs
        with proper delta times.
        """
        mid = mido.MidiFile(ticks_per_beat=orig_mid.ticks_per_beat)

        # Collect all track indices
        track_indices = sorted(set(n['track_idx'] for n in notes))

        # Also include tracks that only had meta events
        meta_tracks = set(me[0] for me in meta_events)
        for tidx in meta_tracks:
            if tidx not in track_indices:
                track_indices.append(tidx)
        track_indices.sort()

        # Get original track count for reference
        orig_track_count = len(orig_mid.tracks)

        for tidx in track_indices:
            track = mido.MidiTrack()
            mid.tracks.append(track)

            # Collect events for this track
            events = []  # (tick, msg)

            # Add meta events for this track
            for me_tidx, me_tick, me_msg in meta_events:
                if me_tidx == tidx:
                    events.append((me_tick, me_msg))

            # Add note events for this track
            track_notes = [n for n in notes if n['track_idx'] == tidx]
            for n in track_notes:
                note_on = mido.Message(
                    'note_on',
                    note=n['pitch'],
                    velocity=n['velocity'],
                    channel=n['channel'],
                )
                note_off = mido.Message(
                    'note_off',
                    note=n['pitch'],
                    velocity=0,
                    channel=n['channel'],
                )
                events.append((n['onset_tick'], note_on))
                events.append((n['onset_tick'] + n['duration_ticks'], note_off))

            # Sort events by tick (note_off at same tick before note_on to prevent overlap)
            def event_sort_key(e):
                tick, msg = e
                is_off = hasattr(msg, 'type') and msg.type == 'note_off'
                return (tick, 0 if is_off else 1)

            events.sort(key=event_sort_key)

            # Convert to delta times
            prev_tick = 0
            for tick, msg in events:
                delta = max(0, tick - prev_tick)
                msg.time = delta
                track.append(msg)
                prev_tick = tick

            # End of track
            track.append(mido.MetaMessage('end_of_track', time=0))

        # If we have no tracks, add at least one
        if not mid.tracks:
            track = mido.MidiTrack()
            track.append(mido.MetaMessage('end_of_track', time=0))
            mid.tracks.append(track)

        return mid

    def batch_morph(
        self,
        midi_path: str,
        targets: list[StyleTile],
        blend: float = 1.0,
    ) -> list[str]:
        """Morph a single file toward multiple targets, returning output paths."""
        results = []
        for target in targets:
            out = self.morph(midi_path, target, blend)
            results.append(out)
        return results
