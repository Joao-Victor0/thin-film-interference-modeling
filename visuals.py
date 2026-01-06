import numpy as np
import plotly.graph_objects as go

class Visuals:
    def __init__(self):
        pass

    
    def wavelength_function_angle_graph(self, angles, wavelengths):
        '''
        Constrói o gráfico que relaciona os comprimentos de onda aos
        ângulos de incidência em filmes finos
        '''
        fig = go.Figure()

        #Adicionar a curva calculada
        fig.add_trace(go.Scatter(
            x=angles,
            y=wavelengths,
            mode='lines',
            name='Comprimento de Onda',
            line=dict(color='white', width=4)
        ))

        #Adicionar faixas de cor para referência do Espectro Visível
        # Violeta/Azul: 380-495nm | Verde: 495-570nm | Amarelo/Vermelho: 570-750nm
        colors = [
            (380, 450, "violet", "Violeta"), (450, 495, "blue", "Azul"),
            (495, 570, "green", "Verde"), (570, 590, "yellow", "Amarelo"),
            (590, 750, "red", "Vermelho")
        ]

        for start, end, color, name in colors:
            fig.add_hrect(
                y0=start, y1=end, 
                fillcolor=color, opacity=0.2, 
                layer="below", annotation_text=name)
        

        fig.update_layout(
            title = "Exibição de Cor vs. Ângulo de Incidência",
            xaxis_title="Ângulo de Incidência (°)",
            yaxis_title="Comprimento de Onda (nm)",
            template="plotly_dark",
            yaxis=dict(range=[350, 750]) #Focar no espectro visível + UV próximo
        )

        return fig
    

    #Conversor de comrpimento de onda em RGB
    def wavelength_to_rgb(self, wavelength, gamma=0.8):
        '''
        Converte comprimento de onda (nm) para cor RGB aproximada
        '''

        wavelength = float(wavelength)

        # Implementação de um transdutor digital a partir do método de Dan Bruton para renderizar o espectro visível em computadores (Ray Tracing)

        # Equação da Reta (Interpolação Linear) da atenuação -> (((wavelength - start) / (440 - end)) * attenuation) ** gamma, que simula a curva de sensibilidade do olho humano
        # Com - em ((-(wavelength - 440) / (440 - 380)) * attenuation) ** gamma cria uma diminuição suave do comprimento de onda
        # Correção Gamma ajusta os valores para que a variação do brilho pareça natural ao olho humano, compensando a não linearidade
        # Sáida 255 formata o RGB para o protocolo digital de 8 bits
        if wavelength >= 380 and wavelength <= 440:
            attenuation = 0.3 + 0.7 * (wavelength - 380) / (440 - 380)
            R = ((-(wavelength - 440) / (440 - 380)) * attenuation) ** gamma
            G = 0.0
            B = (1.0 * attenuation) ** gamma

        elif wavelength >= 440 and wavelength <= 490:
            R = 0.0
            G = ((wavelength - 440) / (490 - 440)) ** gamma
            B = 1.0

        elif wavelength >= 490 and wavelength <= 510:
            R = 0.0
            G = 1.0
            B = (-(wavelength - 510) / (510 - 490)) ** gamma

        elif wavelength >= 510 and wavelength <= 580:
            R = ((wavelength - 510) / (580 - 510)) ** gamma
            G = 1.0
            B = 0.0

        elif wavelength >= 580 and wavelength <= 645:
            R = 1.0
            G = (-(wavelength - 645) / (645 - 580)) ** gamma
            B = 0.0

        elif wavelength >= 645 and wavelength <= 750:
            attenuation = 0.3 + 0.7 * (750 - wavelength) / (750 - 645)
            R = (1.0 * attenuation) ** gamma
            B = 0.0
            G = 0.0

        else:
            R = 0.0
            G = 0.0
            B = 0.0

        return (int(R * 255), int (G * 255), int (B * 255))
    

    def image_grid_construction_2D(self, mask, lambda_grid, resolution):
        '''
        Converter comprimento de onda em RGB
        Cria-se uma imagem vazia (altura, largura, 3 canais de cor)
        '''

        img_RGB = np.zeros((resolution, resolution, 3), dtype=np.uint8)

        # Loop pixel a pixel
        for i in range(resolution):
            for j in range(resolution):

                if mask[i, j]: # se estiver dentro do círculo
                    wavelength = lambda_grid[i, j]
                    RGB = self.wavelength_to_rgb(wavelength)
                    img_RGB[i, j] = RGB

                else:
                    img_RGB[i, j] = [20, 20, 20] # fundo cinza escuro

        return img_RGB
    

    def generate_custom_colorscale(self):
        '''
        Gera uma escala de cores para o Plotly que corresponde ao espectro visível
        '''

        colorscale = []
        min_wavelength, max_wavelength = 350, 750
        steps = 100
        
        for i in range(steps + 1):
            val_norm = i / steps #valor normalizado
            wavelength = min_wavelength + val_norm * (max_wavelength - min_wavelength) #comprimento de onda
            
            # Converter para RGB usando sua função existente
            R, G, B = self.wavelength_to_rgb(wavelength)
            
            # Formatar para string CSS que o Plotly entende na definição da escala
            color_css = f"rgb({R},{G},{B})"
            colorscale.append([val_norm, color_css])
            
        return colorscale
    
    def figure_grid_construction_3D(self, wavelength_grid, X_rot, Y_rot, Z_rot):
        '''
        Constrói uma representação visual em 3D da lente 
        '''
        custom_scale = self.generate_custom_colorscale()
        fig_3D = go.Figure(data=[go.Surface(
                x=X_rot, y=Y_rot, z=Z_rot,
                surfacecolor=wavelength_grid,
                colorscale=custom_scale,     
                cmin=350, cmax=750,          
                showscale=False,
                lighting=dict(ambient=1.0, diffuse=0.0, specular=0.0, roughness=1.0)
            )])

        fig_3D.update_layout(
            scene=dict(
                xaxis=dict(visible=False, range=[-30, 30], backgroundcolor='rgb(20,20,20)'),
                yaxis=dict(visible=False, range=[-30, 30], backgroundcolor='rgb(20,20,20)'),
                zaxis=dict(visible=False, range=[-30, 30], backgroundcolor='rgb(20,20,20)'),
                aspectmode='manual',
                aspectratio=dict(x=1, y=1, z=0.6)
            ),
            margin=dict(l=0, r=0, b=0, t=0),
            height=600,
            paper_bgcolor='rgba(0,0,0,0)'
        )
        return fig_3D