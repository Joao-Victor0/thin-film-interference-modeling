import numpy as np

class Physics:
    def __init__(self, n_film, d, m):
        self.n_film = n_film
        self.d = d
        self.m = m 

    
    # Cálculo do comprimento de onda
    def calculate_wavelength(self, theta_incident_degree):
        """
        Calcula o comprimento de onda (lambda) para interferência construtiva.
        Equação: lambda = (2 * n * d * cos(theta_r)) / m
        """

        # 1. Converter o ângulo incidente de graus para radianos
        theta_i = np.radians(theta_incident_degree)

        # 2. Aplicação da Lei de Snell para achar o ângulo theta_r dentro do filme 
        # Equação: n1 * sin(theta_i) = n2 * sin(theta_r) -> para n_ar = 1.0
        sin_theta_r = (1.0 / self.n_film) * np.sin(theta_i)

        # 3. Evitar ruído por Reflexão Total Interna (dada a sua raridade no fenômeno)
        if np.any(sin_theta_r > 1):
            return np.nan
        
        # 4. Cálculo do cosseno do theta_r
        cos_theta_r = np.sqrt(1 - sin_theta_r**2)

        # 5. Equação de Interferência Construtiva
        wavelength = (2 * self.n_film * self.d* cos_theta_r) / self.m
        return wavelength