"""style-dna — Musical DNA extraction, analysis, and morphing system."""

from .tile import StyleTile
from .extract import StyleExtractor
from .morph import StyleMorpher
from .personalities import PERSONALITIES

__all__ = ["StyleTile", "StyleExtractor", "StyleMorpher", "PERSONALITIES"]
__version__ = "0.1.0"
