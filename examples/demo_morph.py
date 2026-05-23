#!/usr/bin/env python3
"""Demo: morph a MIDI file through multiple composer styles and compare tiles."""

import os
import sys
import shutil
import tempfile

# Add parent to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from style_dna.extract import StyleExtractor
from style_dna.morph import StyleMorpher
from style_dna.personalities import BACH, JOPLIN, COLTRANE, CHOPIN, DEBUSSY


def main():
    # Find a MIDI file to morph
    workspace = os.path.join(os.path.dirname(__file__), "..", "..")
    midi_files = []
    for f in os.listdir(workspace):
        if f.endswith('.mid') and 'morphed' not in f:
            midi_files.append(os.path.join(workspace, f))
            if len(midi_files) >= 5:
                break

    if not midi_files:
        print("No MIDI files found in workspace! Place some .mid files in the workspace root.")
        return

    extractor = StyleExtractor()
    morpher = StyleMorpher(extractor=extractor)

    src = midi_files[0]
    print(f"🎵 Source: {os.path.basename(src)}")

    # Extract original style
    print("\n── Original Style ──")
    original = extractor.extract([src], "Original", "unknown")
    print(f"  Consonance:  {original.consonance_rate:.3f}")
    print(f"  Syncopation: {original.syncopation_rate:.3f}")
    print(f"  Swing:       {original.swing_factor:.3f}")
    print(f"  Lyapunov:    {original.lyapunov_exponent:.4f}")
    print(f"  Entropy ratio: {original.entropy_ratio:.4f}")
    print(f"  Euler char:  {original.euler_characteristic:.2f}")
    print(f"  Betti:       {original.betti_numbers}")

    # Morph through each personality
    targets = [
        ("Bach Baroque", BACH),
        ("Joplin Ragtime", JOPLIN),
        ("Coltrane Jazz", COLTRANE),
    ]

    print("\n── Morphing ──")
    for label, tile in targets:
        with tempfile.TemporaryDirectory() as tmpdir:
            src_copy = shutil.copy(src, os.path.join(tmpdir, "input.mid"))
            out = morpher.morph(src_copy, tile, blend=0.8)
            morphed = extractor.extract([out], label, tile.era)

            sim = original.similarity(morphed)
            print(f"\n  ▸ {label}")
            print(f"    Consonance:  {morphed.consonance_rate:.3f}  (target: {tile.consonance_rate:.3f})")
            print(f"    Syncopation: {morphed.syncopation_rate:.3f}  (target: {tile.syncopation_rate:.3f})")
            print(f"    Swing:       {morphed.swing_factor:.3f}  (target: {tile.swing_factor:.3f})")
            print(f"    Similarity to original: {sim:.4f}")

    # Compare all personalities
    print("\n── Personality Similarity Matrix ──")
    names = ["Bach", "Chopin", "Joplin", "Debussy", "Coltrane"]
    tiles = [BACH, CHOPIN, JOPLIN, DEBUSSY, COLTRANE]
    header = "".join(f"{n:>10}" for n in names)
    print(f"{'':>10}{header}")
    for i, (name_i, tile_i) in enumerate(zip(names, tiles)):
        row = f"{name_i:>10}"
        for j, tile_j in enumerate(tiles):
            sim = tile_i.similarity(tile_j)
            row += f"{sim:>10.4f}"
        print(row)

    print("\n✨ Demo complete!")


if __name__ == "__main__":
    main()
