import numpy as np
from physics import Physics

class Data:
    def __init__(self, physics:Physics):
        self.physics = physics

    def data_generate(self):
        angles = np.linspace(0, 90, 100)
        wavelengths = [self.physics.calculate_wavelength(angle) for angle in angles]

        return angles, wavelengths