# Helper functions and stuff
import numpy as np

class vector_uvw:
    @staticmethod
    def degrees_to_vector(rotation: np.ndarray) -> np.ndarray:
        """
        Convert angles in degrees (pan, tilt, 0) to a direction base vector.
        """
        u, v, _ = rotation # (pan, tilt, roll), roll not used right now.

        # Convert degrees to radians
        u = np.radians(u)
        v = np.radians(v)

        x = np.cos(u) * np.cos(v)
        y = np.sin(v)
        z = np.sin(u) * np.cos(v)

        return np.array([x, y, z])

    @staticmethod
    def vector_to_degrees(v: np.ndarray) -> tuple:
        """
        Convert a direction vector into angles in degrees (pan, tilt, 0).
        """
        # Normalize vector to avoid scale issues
        norm_v = v / np.linalg.norm(v)
        x, y, z = norm_v

        # Calculate tilt (assuming rotation around z-axis affects x and y)
        u = np.arctan2(z, x)  # Project on xy-plane and calculate angle
        u = np.degrees(u)  # Convert radians to degrees

        # Calculate pan (assuming rotation around y-axis affects x and z)
        v = np.arctan2(y, np.sqrt(x**2 + z**2))  # Rotate back from z to align with x-axis
        v = np.degrees(v)  # Convert radians to degrees

        # Convert radians to degrees
        return np.array([u, v, 0])

    @staticmethod
    def get_rotation_matrix(rotation: np.ndarray) -> np.ndarray:
        pan, tilt, roll = rotation

        # Convert degrees to radians
        tilt_rad = np.radians(tilt)
        roll_rad = np.radians(roll)
        pan_rad = np.radians(pan)

        # Rotation matrix around the y-axis (pan) 
        R_y = np.array([
            [np.cos(pan_rad), 0, -np.sin(pan_rad)],
            [0, 1, 0],
            [np.sin(pan_rad), 0, np.cos(pan_rad)]
        ])

        # Rotation matrix around the z-axis (tilt) pitch 
        R_z = np.array([
            [np.cos(tilt_rad), -np.sin(tilt_rad), 0],
            [np.sin(tilt_rad), np.cos(tilt_rad), 0],
            [0, 0, 1]
        ])

        # Rotation matrix around the x-axis (roll) 
        R_x = np.array([
            [1, 0, 0],
            [0, np.cos(roll_rad), -np.sin(roll_rad)],
            [0, np.sin(roll_rad), np.cos(roll_rad)]
        ])

        # Combined rotation matrix
        return np.dot(np.dot(R_x, R_z), R_y)
