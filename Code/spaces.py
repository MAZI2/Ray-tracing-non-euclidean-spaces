# Vsebuje Space razrede, ki enkapsulirajo logiko specifično za vsak space.

import typehints as th

# Vsi space morjo bit otroci _Space classa, in povozt vse njen metode.

class _Space:
    def move(self, pos: th.position, dir: th.direction , step_size) -> th.position:
        """Premakne ray ki se začne v točki pos(x, y, z) za step_size v smeri dir(u, v, w)"""
        pass


class Euclidean(_Space):
    def move(self, pos: th.position, dir: th.direction , step_size) -> th.position:
        x = pos[0] + step_size * dir[0]
        y = pos[1] + step_size * dir[1]
        z = pos[2] + step_size * dir[2]
        return (x, y, z)

# Torus

# Spheare