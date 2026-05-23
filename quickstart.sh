#!/bin/bash
# style-dna quickstart — extract style from MIDI files, morph through personalities
set -e
echo "🧬 Style DNA — Quick Start"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKSPACE="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$SCRIPT_DIR"

pip install -e . --quiet 2>/dev/null || true

python3 -c "
from style_dna.extract import StyleExtractor
from style_dna.personalities import BACH, JOPLIN, COLTRANE, CHOPIN, DEBUSSY
from style_dna.tile import StyleTile
import glob

# Find MIDI files in workspace
midis = sorted(glob.glob('$WORKSPACE/*.mid'))[:3]
if not midis:
    print('⚠️  No MIDI files found in workspace root — showing personality matrix instead')
    print()
else:
    extractor = StyleExtractor()
    for m in midis:
        try:
            tile = extractor.extract([m], m.split('/')[-1], 'unknown')
            print(f'📄 {m.split(\"/\")[-1]}:')
            print(f'   consonance={tile.consonance_rate:.3f}  syncopation={tile.syncopation_rate:.3f}')
            print(f'   swing={tile.swing_factor:.3f}  lyapunov={tile.lyapunov_exponent:.4f}')
        except Exception as e:
            print(f'   (skipped: {e})')
    print()

# Personality comparison matrix
print('🎭 Personality Similarity Matrix:')
names = ['Bach', 'Chopin', 'Joplin', 'Debussy', 'Coltrane']
tiles = [BACH, CHOPIN, JOPLIN, DEBUSSY, COLTRANE]
header = ''.join(f'{n:>10}' for n in names)
print(f'{\"\":>10}{header}')
for i, (ni, ti) in enumerate(zip(names, tiles)):
    row = f'{ni:>10}'
    for j, tj in enumerate(tiles):
        sim = ti.similarity(tj)
        row += f'{sim:>10.4f}'
    print(row)

print()
print('✅ style-dna works!')
"
