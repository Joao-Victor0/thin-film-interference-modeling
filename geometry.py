import numpy as np

class Geometry:
    def __init__(self, rot_x, rot_y, diopter, resolution):
        self.diopter = diopter
        self.resolution = resolution

       # Matrizes de rotação Rx e Ry
        self.Rx = np.array([
                [1, 0, 0],
                [0, np.cos(np.radians(rot_x)), -np.sin(np.radians(rot_x))],
                [0, np.sin(np.radians(rot_x)), np.cos(np.radians(rot_x))]
        ])

        self.Ry = np.array([
                [np.cos(np.radians(rot_y)), 0, np.sin(np.radians(rot_y))],
                [0, 1, 0],
                [-np.sin(np.radians(rot_y)), 0, np.cos(np.radians(rot_y))]
        ])


    
    # Cálculo do raio de curvatura
    def calculate_radius_curvature(self, glass_index):
        '''
        Cálcula o raio de curvatura da lente
        Equação: r = (n - 1) / D
        Para ter em mm, multiplica-se por 1000
        '''

        if self.diopter < 0.1:
            radius_curvature_mm = 999999 # Plano infinito

        else:
            radius_curvature_mm = ((glass_index - 1) * 1000) / self.diopter

        return radius_curvature_mm


    def grid_rotation_3D(self, points_flat):
        '''
        Realiza a rotação matricial do vetor em 3 dimensões
        '''

        # Combinação de Rotação a partir da multiplicação matricial
        rotated_flat = self.Ry @ (self.Rx @ points_flat)

        # Remontar os grid 2D
        X_rot = rotated_flat[0].reshape(self.resolution, self.resolution)
        Y_rot = rotated_flat[1].reshape(self.resolution, self.resolution)
        Z_rot = rotated_flat[2].reshape(self.resolution, self.resolution)

        return X_rot, Y_rot, Z_rot
    

    # Cálculo do ângulo máximo na borda para duas dimensões
    def calculate_theta_max_2D(self, lens_diameter_mm, glass_index):
        '''
        Cálculo do ângulo máximo na borda (por aproximação) em 2D
        Equação: sin(theta) = (metade_do_diametro) / raio_curvatura
        '''

        half_diameter = lens_diameter_mm / 2
        radius_curvature_mm = self.calculate_radius_curvature(glass_index)

        #Contorno para erro de tamanho
        if half_diameter > radius_curvature_mm:
            theta_max_degree = 90.0

        else:
            sin_theta = half_diameter / radius_curvature_mm
            theta_max_radius = np.arcsin(sin_theta)
            theta_max_degree = np.degrees(theta_max_radius)

        return theta_max_degree
    
    
    # Cálculo do ângulo de incidência
    def calculate_theta_3D(self, normals, light_vectors=None):
        '''
        Calcula o ângulo entre a normal e o vetor da luz.
        Se light_vectors for None, assume luz vindo de fonte distante [0,0,1] (Sol).
        Se light_vectors for passado, usa a luz pontual (Lâmpada).
        '''

        if light_vectors is None: # se não tiver parâmetro de vetor de luz definido. usar luz vindo de uma fonte distante
            light_vectors = np.array([0, 0, 1])

        # Produto Escalar
        dot_product = np.sum(normals * light_vectors, axis=2)
        dot_product = np.nan_to_num(dot_product, nan=1.0) # evitar erro no arccos
        dot_product = np.clip(dot_product, -1.0, 1.0)

        theta_incident_degree= np.degrees(np.arccos(np.abs(dot_product)))
        return theta_incident_degree   
    

    # Função genérica de normalização para qualquer array de vetores
    @staticmethod
    def generic_normalize(vectors):
        '''
        Normaliza qualquer array de vetores (N, M, 3) com segurança.
        Serve tanto para Normais da Lente quanto para Vetores de Luz.
        '''

        magnitudes = np.linalg.norm(vectors, axis=2, keepdims=True)
        magnitudes[magnitudes == 0] = 1
        return vectors / magnitudes

    
    # Função de normalização para a normal da superfície
    def superficial_normalize_3D(self, center_rot, P_grid):
        '''
        Realiza a normalização para cada direção de vetor
        Normalização = vetor / magnitude
        '''
        if self.diopter < 0.1:
            normal_flat = self.Ry @ (self.Rx @ np.array([0, 0, 1])) # plano z rotacionado
            normals = np.tile(normal_flat, (self.resolution, self.resolution, 1)) # em todo grid

        else:
            vectors = P_grid - center_rot
            normals = self.generic_normalize(vectors)

        return normals


    # Função de vetorização para pontos normais da superfície
    def vectorize_3D(self, X_rot, Y_rot, Z_rot, radius_curvature_mm, light_distance_mm=None):
        '''
        Realiza o processo de vetorização dos pontos
        '''

        # Criando um array (res, res, 3) -> cada pixel tem coordenadas x,y,z
        P_grid = np.dstack((X_rot, Y_rot, Z_rot))

        # Centro da esfera rotacionado
        center_point = np.array([0, 0, -radius_curvature_mm])
        center_rot = self.Ry @ (self.Rx @ center_point)

        # Cálculo das normais de cada direção
        normals = self.superficial_normalize_3D(center_rot, P_grid)

        # Cálculo do vetor de luz
        if light_distance_mm is not None:
            # Fonte Pontual
            # Vetor dado por posição da luz - posição do pixel
            light_position = np.array([0, 0, light_distance_mm])
            light_vectors = light_position - P_grid

            # Normalizar os vetores
            light_vectors_normals = self.generic_normalize(light_vectors)

        else:
            light_vectors_normals = None


        # Cálculo do ângulo de incidência
        theta_degrees = self.calculate_theta_3D(normals, light_vectors_normals)
        return normals, theta_degrees