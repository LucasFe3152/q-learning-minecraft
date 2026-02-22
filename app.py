import streamlit as st
import random

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Q-Learning Miner", page_icon="🤖", layout="wide")
st.title("🤖 Q-Learning: Mineração Autônoma")
st.markdown("Ajuste o tamanho do mapa e veja o agente descobrir a melhor rota!")

# --- DEFINIÇÕES GERAIS ---
acoes_possiveis = ['cima', 'baixo', 'esquerda', 'direita']

EMOJIS = {
    -1: '🤠', # Nosso agente
    0: '⚫', # Pedra
    1: '⚪', # Ferro
    2: '🔴', # Redstone
    3: '🟡', # Ouro
    4: '💎'  # Diamante
}

RECOMPENSAS = {0: -1, 1: 10, 2: 20, 3: 30, 4: 60}

# --- FUNÇÃO GERADORA DE MAPAS ---
def gerar_mapa_aleatorio(tamanho):
    opcoes = [0, 1, 2, 3, 4]
    pesos = [0.60, 0.20, 0.10, 0.07, 0.03]
    
    novo_grid = []
    for y in range(tamanho):
        linha = []
        for x in range(tamanho):
            if x == 0 and y == 0:
                linha.append(0) # A posição (0,0) onde o agente nasce sempre é pedra
            else:
                linha.append(random.choices(opcoes, weights=pesos, k=1)[0])
        novo_grid.append(linha)
    return novo_grid

# --- FUNÇÕES DO Q-LEARNING ---
def inicializar_estado(tabela_q, estado):
    if estado not in tabela_q:
        tabela_q[estado] = {acao: 0.0 for acao in acoes_possiveis}

def escolher_acao(tabela_q, estado, epsilon):
    inicializar_estado(tabela_q, estado)
    if random.random() < epsilon:
        return random.choice(acoes_possiveis)
    else:
        return max(tabela_q[estado], key=tabela_q[estado].get)

def interagir_com_ambiente(estado, acao, grid_atual):
    x, y = estado[0], estado[1]
    
    if acao == 'cima': y -= 1
    elif acao == 'baixo': y += 1
    elif acao == 'esquerda': x -= 1
    elif acao == 'direita': x += 1
        
    if x < 0 or x >= len(grid_atual[0]) or y < 0 or y >= len(grid_atual):
        x, y = estado[0], estado[1]  
        recompensa = -5
        minerou = False
    else:
        id_minerio = grid_atual[y][x]
        recompensa = RECOMPENSAS[id_minerio]
        minerou = (id_minerio != 0)
        if minerou:
            grid_atual[y][x] = 0
            
    mapa_estado = tuple(tuple(linha) for linha in grid_atual)
    return (x, y, mapa_estado), recompensa, minerou

# Cache depende do mapa_inicial e dos episódios
@st.cache_data(show_spinner=False)
def treinar_agente(grid_inicial, episodios, total_minerios):
    tabela_q = {}
    alfa, gama, epsilon, decaimento = 0.1, 0.9, 1.0, 0.9999

    tamanho_grid = len(grid_inicial)
    
    for _ in range(episodios):
        grid_atual = [linha[:] for linha in grid_inicial]
        mapa_estado = tuple(tuple(linha) for linha in grid_atual)
        x_inicial = random.randint(0, tamanho_grid - 1)
        y_inicial = random.randint(0, tamanho_grid - 1)
        estado_atual = (x_inicial, y_inicial, mapa_estado)
        terminou = False
        minerios_coletados = 0
        
        while not terminou:
            acao = escolher_acao(tabela_q, estado_atual, epsilon)
            proximo_estado, recompensa, minerou = interagir_com_ambiente(estado_atual, acao, grid_atual)
            
            if minerou:
                minerios_coletados += 1
            if total_minerios > 0 and minerios_coletados == total_minerios:
                terminou = True
                
            inicializar_estado(tabela_q, estado_atual)
            inicializar_estado(tabela_q, proximo_estado)
            
            q_atual = tabela_q[estado_atual][acao]
            max_q_futuro = max(tabela_q[proximo_estado].values())
            tabela_q[estado_atual][acao] = q_atual + alfa * (recompensa + gama * max_q_futuro - q_atual)
            
            estado_atual = proximo_estado
            
        epsilon *= decaimento
    return tabela_q

def renderizar_grid_emoji(grid, pos_agente):
    texto = ""
    for y, linha in enumerate(grid):
        for x, celula in enumerate(linha):
            if (x, y) == pos_agente:
                texto += EMOJIS[-1]
            else:
                texto += EMOJIS[celula]
        texto += "  \n"
    return texto

# --- BARRA LATERAL (CONTROLES) ---
st.sidebar.header("⚙️ Configurações do Ambiente")

# Inputs para o tamanho da grid e episódios
tamanho_grid = st.sidebar.number_input("Tamanho da Grid (N x N)", min_value=3, max_value=10, value=5, step=1)
episodios_input = st.sidebar.number_input("Número de Episódios", min_value=1000, max_value=200000, value=50000, step=5000)

# Inicializa um mapa na memória se não existir
if 'grid_base' not in st.session_state:
    st.session_state['grid_base'] = gerar_mapa_aleatorio(tamanho_grid)

# Botão para sortear um novo mapa
if st.sidebar.button("🎲 Gerar Novo Mapa Aleatório"):
    st.session_state['grid_base'] = gerar_mapa_aleatorio(tamanho_grid)
    # Limpa a tabela Q salva da sessão anterior, pois o mapa mudou
    if 'tabela_q' in st.session_state:
        del st.session_state['tabela_q']
    st.rerun()

# Calcula o total de minérios do mapa atual
MINERIOS_TOTAIS = sum(1 for linha in st.session_state['grid_base'] for item in linha if item != 0)

# --- VISUALIZAÇÃO PRÉ-TREINAMENTO ---
st.subheader("Pré-visualização do Mapa")
st.markdown(f"**Total de Minérios a coletar:** {MINERIOS_TOTAIS}")

# Divide a tela em duas colunas (proporção de tamanho 1 para 1)
col_mapa, col_legenda = st.columns(2)

# Coluna 1: O Mapa
with col_mapa:
    # Colocamos o mapa dentro de uma caixa para ficar bem alinhado
    st.text(renderizar_grid_emoji(st.session_state['grid_base'], (-1,-1)))

# Coluna 2: O Glossário em formato de Tabela Markdown
with col_legenda:
    st.markdown("""
    ### 📖 Glossário de Recompensas
    
    | Símbolo | Elemento | Recompensa (Q-Value) |
    | :---: | :--- | :---: |
    | 🤠 | **Agente** | *(Posição Inicial)* |
    | ⚫ | **Pedra** | **-1** |
    | ⚪ | **Ferro** | **+10** |
    | 🔴 | **Redstone** | **+20** |
    | 🟡 | **Ouro** | **+30** |
    | 💎 | **Diamante** | **+60** |
    
    *Nota: Passos em blocos de pedra geram punição (-1) para ensinar o agente a encontrar a rota mais rápida.*
    """)


st.markdown("---")

# --- TREINAMENTO E SIMULAÇÃO ---
if st.button("🚀 Treinar Agente neste Mapa"):
    with st.spinner(f"Treinando por {episodios_input} episódios... Isso pode levar de alguns segundos a um minuto."):
        # Passa o grid dinâmico para a função de treino
        tabela_q = treinar_agente(st.session_state['grid_base'], episodios_input, MINERIOS_TOTAIS)
        
        st.session_state['tabela_q'] = tabela_q
        st.session_state['grid_teste'] = [linha[:] for linha in st.session_state['grid_base']]
        
        mapa_estado = tuple(tuple(linha) for linha in st.session_state['grid_teste'])
        st.session_state['estado_atual'] = (0, 0, mapa_estado)
        
        st.session_state['minerios_coletados'] = 0
        st.session_state['passos'] = 0
        st.session_state['recompensa_acumulada'] = 0
        st.session_state['terminou'] = False
        
        st.success("Treinamento Concluído! O agente está pronto.")

# Se já houver uma tabela Q pronta na memória, exibe os controles de passo a passo
if 'tabela_q' in st.session_state:
    st.subheader("⛏️ Execução da Rota Ótima")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Passos", st.session_state['passos'])
    col2.metric("Minérios Coletados", f"{st.session_state['minerios_coletados']} / {MINERIOS_TOTAIS}")
    col3.metric("Recompensa Total", st.session_state['recompensa_acumulada'])
    st.markdown("---")
    
    x_agente = st.session_state['estado_atual'][0]
    y_agente = st.session_state['estado_atual'][1]
    st.text(renderizar_grid_emoji(st.session_state['grid_teste'], (x_agente, y_agente)))
    
    col_btn_passo, col_btn_reset = st.columns(2)
    
    with col_btn_passo:
        if not st.session_state['terminou']:
            if st.button("▶️ Dar Próximo Passo"):
                estado_atual = st.session_state['estado_atual']
                tabela_q = st.session_state['tabela_q']
                grid_teste = st.session_state['grid_teste']
                
                valores = tabela_q.get(estado_atual, {a: 0 for a in acoes_possiveis})
                melhor_acao = max(valores, key=valores.get)
                
                novo_estado, recompensa_do_passo, minerou = interagir_com_ambiente(estado_atual, melhor_acao, grid_teste)
                
                st.session_state['estado_atual'] = novo_estado
                st.session_state['passos'] += 1
                st.session_state['recompensa_acumulada'] += recompensa_do_passo
                
                if minerou:
                    st.session_state['minerios_coletados'] += 1
                    
                if MINERIOS_TOTAIS > 0 and st.session_state['minerios_coletados'] == MINERIOS_TOTAIS:
                    st.session_state['terminou'] = True
                    
                st.rerun()
                
    with col_btn_reset:
        if st.button("🎲 Mudar Posição Inicial"):
            tamanho = len(st.session_state['grid_base'])
            
            # Sorteia uma nova posição
            novo_x = random.randint(0, tamanho - 1)
            novo_y = random.randint(0, tamanho - 1)
            
            # Restaura o mapa e zera os contadores da sessão
            st.session_state['grid_teste'] = [linha[:] for linha in st.session_state['grid_base']]
            mapa_estado = tuple(tuple(linha) for linha in st.session_state['grid_teste'])
            
            st.session_state['estado_atual'] = (novo_x, novo_y, mapa_estado)
            st.session_state['minerios_coletados'] = 0
            st.session_state['passos'] = 0
            st.session_state['recompensa_acumulada'] = 0
            st.session_state['terminou'] = False
            
            # Recarrega a tela com o agente no novo local
            st.rerun()
            
    # Mensagem de vitória
    if st.session_state['terminou']:
        st.success("🎉 Objetivo alcançado! A caverna foi limpa.")