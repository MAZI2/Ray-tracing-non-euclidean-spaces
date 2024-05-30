import numpy as np

from objects import _IntersectableObject
from utilities import Ray

# THIS IS JUST SO TYPE HINTING WORKS
class _Space:
    def xyz_equation(self, ray: Ray, t: float) -> np.ndarray:
        pass

# ---------------------------- Methods ----------------------------

def adaptive_step(ray: Ray, object: _IntersectableObject, space:  _Space,
                 t0: float = 0.0001, # Učas je mel z 0 težave
                 max_t: float = float("inf"), 
                 tollerance: float = 0.0001, 
                 max_iter: int = 1000, 
                 step_size: float = 0.1) -> float:
    """Na vsako potenco števila 2 kličemo broydenovo metodo, če ne koncergira delam korake velikosti step_size."""
    t = np.array([t0] * 2, dtype=np.float64)
    y = np.array([object.equation(space.xyz_equation(ray, t0))] * 2)
    stop_increase = False
    going_towards = False # Pr 2sphere sinusno narašča najprej, rabš it čez prvo grbo.

    for _ in range(max_iter):
        # What would be the new valies?
        new_t = t[1] + step_size
        new_y = object.equation(space.xyz_equation(ray, t[1] + step_size))


        if new_y > y[1]: 
            # If we start going away from the object, reduce step size
            if going_towards: # če še nikol nism šu proti objektu, mam pred sabo grbo, čez katero morm preplezat
                stop_increase = True
                if step_size < tollerance: return None # We missed the object
                # Go one step back (could happen that we went to the other side of the object)
                t[1] = t[0]
                y[1] = y[0]
                step_size /= 2
                continue
        elif new_y < 0: 
            # If we crossed the object, reduce step size, 
            stop_increase = True
            if step_size < tollerance: return t[1] # We hit the object
            step_size /= 2
            continue
        elif new_t > max_t: 
            # If we are out of bounds, return None
            return None 
        else:
            # Increase step size:
            if not stop_increase: step_size *= 2
            going_towards = True 
        # Update t and y
        t[0] = t[1]
        t[1] = new_t
        y[0] = y[1]
        y[1] = new_y

def broyden(ray: Ray, t0: float, delta_t: float, object: _IntersectableObject, space:  _Space, 
            tollerance: float, max_iter: int) -> float:
    """Broydens method da najdem ničlo funkcije iz objekta in enačbe premikanjaa skozi prostor."""
    t = np.array([t0, t0+delta_t], dtype=np.float64)
    y = np.array([object.equation(space.xyz_equation(ray, t0)), 
                  object.equation(space.xyz_equation(ray, t0+delta_t))], dtype=np.float64)

    for i in range(max_iter):
        # Calculate the next t
        new_t = (t[1] - y[1] * (t[1] - t[0]) / (y[1] - y[0]))
        
        # Shift t
        t[0] = t[1]
        t[1] = new_t

        # Shift y
        y[0] = y[1]
        y[1] = object.equation(space.xyz_equation(ray, new_t))

        # Check tollerance
        if (t[1] - t[0])**2 < tollerance**2:
            if new_t > 0: # Samo če smo najdl intersection pred kamero.
                return new_t
            else:
                return None
        
        # Al je šla u tri krasne
        if y[1] > y[0] or new_t > 10000 or i == max_iter: # Če kej nrdiš t[1] > y[0] spremen tud v blaz_broyden da sezmer dela za funkcije k se hitrejš približujejo kokr t raste (črna lukna)
            return None # Failed to converge / dont have intersection

def adaptive_step_broyden(ray: Ray, object: _IntersectableObject, space:  _Space,
                 t0: float = 0.001, # Učas je mel z 0 težave
                 delta_t: float = 0.01, # Za računat naklon
                 max_t: float = float("inf"), 
                 tollerance: float = 0.0001, 
                 max_iter: int = 1000, 
                 step_size: float = 0.1) -> float:
    """Na vsako potenco števila 2 kličemo broydenovo metodo, če ne koncergira delam korake velikosti step_size."""
    t = np.array([t0] * 2, dtype=np.float64)
    y = np.array([object.equation(space.xyz_equation(ray, t0))] * 2)
    stop_increase = False

    for _ in range(max_iter):
        # What would be the new valies?
        new_t = t[1] + step_size
        new_y = object.equation(space.xyz_equation(ray, t[1] + step_size))


        if new_y > y[1]: 
            # If we start going away from the object, reduce step size
            stop_increase = True
            if step_size < tollerance: return None # We missed the object
            # Go one step back (could happen that we went to the other side of the object)
            t[1] = t[0]
            y[1] = y[0]
            step_size /= 2
            continue
        elif new_y < 0: 
            # If we crossed the object, reduce step size, 
            stop_increase = True
            if step_size < tollerance: return t[1] # We hit the object
            step_size /= 2
            continue
        elif new_t > max_t: 
            # If we are out of bounds, return None
            return None 
        else:
            # Increase step size:
            if not stop_increase: step_size *= 2
        
        # Run broyden, as we are going towards the object
        possible_t = broyden(ray, t0, delta_t, object, space, tollerance, max_iter)
        if possible_t is not None:
            return possible_t
        
        # Update t and y
        t[0] = t[1]
        t[1] = new_t
        y[0] = y[1]
        y[1] = new_y
