# To je file za typehinte, ki jih uporabljamo v ostalih fileih.
# Ideja je da interpreterju poveš "js prčakujem da tukej pride tuple, ki je oblike (float, float, float) npr"
# (kokr to počneš v Javi apa c-ju) da sproti odkriješ buge itd.

from typing import Tuple

# Vektorji pozicije in smeri
position = Tuple[float, float, float] # (x, y, z) 0-inf
direction = Tuple[float, float, float] # (x, y, z) 0-inf
rotation = Tuple[float, float, float] # (u, v, w) 0-360 (deg)

# Barva
rgb = Tuple[int, int, int] # (r, g, b) 0-255

# Resolucija
resolution = Tuple[int, int] # (width, height) 0-inf

# Tipi objektov k jih v scene dam v en dict
class _ObjectTypes:
    """Types of objects that can be in the scene."""
    object = "object"
    light = "light"
    camera = "camera"
    space = "space"
