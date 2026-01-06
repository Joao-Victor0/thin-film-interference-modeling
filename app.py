import streamlit as st
from simulation_engine import SimulationEngine

# -- ELEMENTOS DA PÁGINA -- 
st.set_page_config(page_title="Simulador de Interferência em Filmes Finos", layout="wide")

st.title("🔬 Modelagem de Interferência em Filmes Finos")
st.markdown("""
Este dashboard modela o fenômeno de interferência construtiva em lentes com tratamento antirreflexo.
O objetivo é observar como o **ângulo de incidência** altera a **cor (comprimento de onda)** percebida.
""")

# Inserção de Parâmetros Físicos
st.sidebar.header("Parâmetros da Lente")

# Refractive Index (n ~= 1.413) para material MgF2 (Fluoreto de Magnésio)
film_index = st.sidebar.slider(
    "Índice de Refração do Filme (n)",
    min_value=1.0,
    max_value=2.0,
    value=1.413,
    step=0.01,
    help="O índice de refração do material antirreflexo."
)

# Thickbess (d) em nanômetros (nm)
# Permite trabalhar em relação a diferentes comprimentos de onda
film_thickness = st.sidebar.slider(
    "Espessura do Filme (d) [mm]",
    min_value=50,
    max_value=800,
    value=200,
    step=10,
    help="Espessura da camada antirreflexo"
)

# Order of interference (m) - adimensional
interference_order = st.sidebar.selectbox(
    "Ordem de Interferência (m)",
    options=[1, 2, 3],
    index=0,
    help="Geralmente usa-se m = 1 para a cor principal é observada."
)

# Abas para separar os níveis
tab1, tab2, tab3 = st.tabs(["📈 Nível 1: Gráfico 1D", "👓 Nível 2: Simulação da Lente 2D", "Nível 3: Simulação da Lente 3D"])

# Para a aba 1 -- Estudo da relação entre o ângulo de inclinação da lente em relação a fonte de luz e o comprimento de onda
with tab1:
    simulation = SimulationEngine(
        n_film=film_index, d=film_thickness, m=interference_order, 
    )

    figure, angles, wavelengths = simulation.simulation_figure_1D()
    st.plotly_chart(figure, width='stretch')

    # -- INTERAÇÕES ADICIONAIS --

    st.write("### Análise do Fenômeno")
    col1, col2 = st.columns(2)

    # Observação em diferentes ângulos
    with col1:
        st.info(f"""
        **Olhando de frente (0°):**
        A cor refletida é aproximadamente **{wavelengths[0]:.0f} nm**.
        """)

    with col2:
        st.info(f"""
        **Olhando de lado (60°):**
        A cor refletida cai para **{wavelengths[66]:.0f} nm** (Blue Shift).
        """)

    st.warning("Nota: Se a linha cair abaixo de 380nm, a luz entra no espectro Ultravioleta (invisível a olho nu).")

# Para a aba 2 -- Estudo da interferência de películas finas para uma fonte distante em geometria 2D
with tab2:
    col_params, col_sim = st.columns([1, 3])

    with col_params:
        st.info("Ângulo baseado na física óptica real")

        diopter = st.number_input("Grau da Lente (Dioptria)", min_value=0.0, max_value=20.0, value=5.0, step=0.25, help="Ex: 5.0 para uma lente de -5.00 graus.", key="diopter_2D")
        lens_diameter_mm = st.number_input("Diâmetro da Lente (mm)", min_value=30, max_value=80, value=50, step=1, help="Tamanho aproximado do aro do óculos.")
        glass_index = 1.50 # Índice comum para vidro/resina padrão
        resolution = st.slider("Resolução da Simulação", 100, 500, 200, 50, help="Mais pixels = mais bonito, mas mais lento.", key="resolution_2D")

        simulation = SimulationEngine(
            n_film=film_index, d=film_thickness, m=interference_order, 
            diopter=diopter, resolution=resolution
        )

        img_RGB, theta_max_degree = simulation.simulation_grid_2D(
            lens_diameter_mm=lens_diameter_mm, glass_index=glass_index) 

        st.write("---")
        st.metric("Ângulo Máximo na Borda", f"{theta_max_degree:.1f}°")
        st.caption(f"Isso significa que na pontinha da armação, a luz bate inclinada a {theta_max_degree:.1f} graus.")

    with col_sim:               
        st.image(img_RGB, caption=f"Simulação Física: Lente de {diopter}D ({lens_diameter_mm}mm)", width='stretch')
       
        if theta_max_degree < 15:
            st.warning("Nota: Para graus baixos (< 4D), a curvatura é pequena. A cor mudará pouco do centro para a borda (efeito sutil), o que é fiel à realidade.")

# Para a aba 3 -- Estudo da interferência de películas finas para uma fonte distante em geometria 3D, variando inclinação da lente
with tab3:
    col_params, col_sim= st.columns([1, 3])

    with col_params:
        st.write("-- Controles em 3D --")
        st.write("**🔦 Fonte de Luz**")

        light_type = st.radio(
            "Tipo de Luz:", 
            ["Sol (Infinito)", "Lâmpada (Pontual)"], 
            horizontal=True,
            label_visibility="collapsed" # Esconde o label repetido
        )

        light_distance = None # Padrão para o "Sol" -- em milímetros

        if light_type == "Lâmpada (Pontual)":
            light_distance = st.slider(
                "Distância (mm)", 
                min_value=50, max_value=1000, value=200, step=10,
                help="Distância da lâmpada até a lente. Quanto mais perto, maior o efeito de gradiente nas bordas."
            )
            st.info("💡 Note o gradiente nas bordas!")

        else:
            st.caption("Raios paralelos (luz colimada). A cor depende apenas da inclinação da lente.")

        st.divider()

        # Sliders de rotação
        rot_x = st.slider("Rotação Vertical (Tilt X)", -45, 45, 0, 1)
        rot_y = st.slider("Rotação Lateral (Pan Y)", -45, 45, 0, 1)

        st.divider()

        # Configuração de Geometria
        st.write("-- Geometria --")
        diopter = st.number_input("Grau da Lente (Dioptria)", min_value=0.0, max_value=20.0, value=5.0, step=0.25, help="Ex: 5.0 para uma lente de -5.00 graus.", key="diopter_3D")
        st.caption("Nota: A cor é calculada dinamicamente baseada na normal da superfície em relação à câmera (Luz).")

        resolution = st.slider("Resolução da Simulação", 100, 500, 200, 50, help="Mais pixels = mais bonito, mas mais lento.", key="resolution_3D")
        
    with col_sim:
        simulation = SimulationEngine(
            n_film=film_index, d=film_thickness, m=interference_order,
            diopter=diopter, resolution=resolution,
            rot_x=rot_x, rot_y=rot_y,
        )

        figure = simulation.simulation_grid_3D(glass_index=1.5, light_distance_mm=light_distance)
        st.plotly_chart(figure, width='stretch')