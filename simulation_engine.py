import numpy as np
from physics import Physics
from geometry import Geometry
from data import Data
from visuals import Visuals

class SimulationEngine:
    def __init__(self, n_film, d, m, diopter=0.0, resolution=0.0, rot_x=0.0, rot_y=0.0):
        self.physics_model = Physics(n_film, d, m)
        self.geometry_model = Geometry(rot_x, rot_y, diopter, resolution)
        self.database = Data(physics=self.physics_model)
        self.visuals_models = Visuals()


    def simulation_figure_1D(self):
        # Conjunto de Ângulos e Comprimentos de Onda
        angles, wavelengths = self.database.data_generate()

        # Exibição do gráfico de Comprimento de Onda em função dos Ângulos de Incidência
        figure = self.visuals_models.wavelength_function_angle_graph(angles, wavelengths)
        
        return figure, angles, wavelengths


    def simulation_grid_2D(self, lens_diameter_mm, glass_index):
        '''
        Constrói o grid de coordenadas e administra as demais dependências para exibir simulação 2D
        '''

        # 1. Criar um grid de coordenadas (x, y)
        x = np.linspace(-1, 1, self.geometry_model.resolution)
        y = np.linspace(-1, 1, self.geometry_model.resolution)
        X, Y = np.meshgrid(x, y)

        # 2. Calcular a distância do centro (0 <= raio R <= 1)
        R = np.sqrt(X**2 + Y**2)

        # 3. Máscara para deixar redondo (recortar o quadrado)
        mask = R <= 1.0

        # 4. Mapear o raio a partir do ângulo de incidência
        # Quanto mais longe do centro, maior o ângulo (devido à curvatura)
        # Multiplica-se por 90 para simular até 90° na borda extrema se a curvatura for 
        theta_max_degree = self.geometry_model.calculate_theta_max_2D(lens_diameter_mm, glass_index)
        theta_grid = R * theta_max_degree

        # 5. Calcular comprimento de onda para cada pixel para cada pixel
        # Aplica-se a função matemática em toda a matriz de uma vez (vetorização)
        lambda_grid = self.physics_model.calculate_wavelength(theta_grid)

        # 6. Criação da imagem no formato RGB
        image_RGB = self.visuals_models.image_grid_construction_2D(mask, lambda_grid, self.geometry_model.resolution)
        return image_RGB, theta_max_degree
    

    def simulation_grid_3D(self, glass_index, light_distance_mm=None):
        '''
        Constrói o grid de coordenadas e administra as demais dependências para exibir simulação 3D
        '''
        
        # 1. Configuração do grid
        limit = 25 # Raio de 25 mm
        x = np.linspace(-limit, limit, self.geometry_model.resolution)
        y = np.linspace(-limit, limit, self.geometry_model.resolution)
        X, Y = np.meshgrid(x, y)

        # 2. Gerar a superfície da lente
        # Equação pro raio de curvatura: R = (n-1)/D * 1000
        # Se D = 0, R é infinito (plano)
        radius_curvature_mm = self.geometry_model.calculate_radius_curvature(glass_index)

        if self.geometry_model.diopter < 0.1:
            Z = np.zeros_like(X)
            mask_circle = None

        else:
            # Equação da esfera: Z = sqrt(R^2 - X^2 - Y^2) - R (para centrar no zero)
            term = np.clip(radius_curvature_mm**2 - X**2 - Y**2, 0, None)
            Z = np.sqrt(term) - radius_curvature_mm

            # Máscara circular
            mask_circle = (X**2 + Y**2) > (limit**2)

            # Aplicar invisibilidade fora do círculo
            Z[mask_circle] = np.nan

        # 3. Empilhar em formato (N, 3) para rotação
        points_flat = np.vstack([X.ravel(), Y.ravel(), Z.ravel()])

        # 4. Rotacionar o vetor
        X_rot, Y_rot, Z_rot = self.geometry_model.grid_rotation_3D(points_flat)

        # 5. Vetorização
        normals, theta_incident_degree = self.geometry_model.vectorize_3D(
            X_rot, Y_rot, Z_rot, 
            radius_curvature_mm, light_distance_mm
        )
        
        # 6. Construção da figura
        wavelength_grid = self.physics_model.calculate_wavelength(theta_incident_degree)
        figure_3D = self.visuals_models.figure_grid_construction_3D(wavelength_grid, X_rot, Y_rot, Z_rot)
        return figure_3D