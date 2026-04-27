import streamlit as st
import networkx as nx
import plotly.graph_objects as go
import random

# Налаштування сторінки
st.set_page_config(
    page_title="Network Resilience Pro", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- ОНОВЛЕНИЙ ДИЗАЙН ТА КОЛЬОРИ ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&family=Inter:wght@400;700&display=swap');
    
    /* Головний фон додатка */
    .stApp {
        background-color: #0F172A; /* Дуже темний синій (Slate 900) */
        color: #F8FAFC;
    }
    
    /* Шрифт для всього тексту */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Стилізація бічної панелі (Sidebar) */
    section[data-testid="stSidebar"] {
        background-color: #1E293B; /* Темно-сірий синій (Slate 800) */
        border-right: 1px solid #334155;
    }
    
    /* Заголовки */
    h1 {
        color: #38BDF8; /* Світло-блакитний (Sky 400) */
        font-family: 'Roboto Mono', monospace;
        text-transform: uppercase;
        letter-spacing: 2px;
        text-shadow: 0px 0px 10px rgba(56, 189, 248, 0.3);
    }

    /* Метрики */
    div[data-testid="stMetricValue"] {
        color: #38BDF8 !important;
        font-family: 'Roboto Mono', monospace;
    }
    
    div[data-testid="stMetricLabel"] {
        color: #94A3B8 !important;
    }

    /* Кнопки */
    .stButton>button {
        background-color: #0EA5E9;
        color: white;
        border-radius: 4px;
        border: none;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #38BDF8;
        box-shadow: 0px 0px 15px rgba(56, 189, 248, 0.5);
        color: white;
    }

    /* Стилізація карток висновків */
    .stAlert {
        background-color: #1E293B;
        border: 1px solid #334155;
        color: #F8FAFC;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    st.markdown("<h1>Network Resilience Analysis</h1>", unsafe_allow_html=True)
    
    # --- Бічна панель (Sidebar) ---
    st.sidebar.markdown("### 🛠 CONTROL PANEL")
    
    node_count = st.sidebar.slider("Nodes count", 5, 60, 25)
    edge_prob = st.sidebar.slider("Link density", 0.05, 0.5, 0.12)
    
    if 'G' not in st.session_state or st.sidebar.button("REGENERATE TOPOLOGY"):
        st.session_state.G = nx.erdos_renyi_graph(n=node_count, p=edge_prob, seed=random.randint(1, 9999))
        st.session_state.pos = nx.spring_layout(st.session_state.G)

    G = st.session_state.G.copy()
    pos = st.session_state.pos

    # Алгоритм пошуку критичних вузлів
    articulation_points = set(nx.articulation_points(G))
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚠️ SCENARIO SIMULATION")
    attack_mode = st.sidebar.radio("Mode:", ["Monitoring", "Random Failure", "Targeted Attack"])
    
    nodes_to_remove = []
    if attack_mode == "Random Failure":
        fail_rate = st.sidebar.slider("Degradation %", 0, 50, 20)
        num_to_del = int(node_count * (fail_rate / 100))
        nodes_to_remove = random.sample(list(G.nodes()), min(num_to_del, len(G.nodes())))
    
    elif attack_mode == "Targeted Attack":
        nodes_to_remove = list(articulation_points)

    G.remove_nodes_from(nodes_to_remove)

    # --- Метрики ---
    m_col1, m_col2, m_col3 = st.columns(3)
    with m_col1:
        st.metric("Alive Nodes", G.number_of_nodes())
    with m_col2:
        components = nx.number_connected_components(G) if G.number_of_nodes() > 0 else 0
        st.metric("Sub-networks", components)
    with m_col3:
        is_ok = G.number_of_nodes() > 0 and nx.is_connected(G)
        st.metric("System Integrity", "STABLE" if is_ok else "BREACHED")

    # --- Візуалізація Plotly ---
    edge_trace = go.Scatter(
        x=[], y=[], line=dict(width=0.8, color='#475569'), hoverinfo='none', mode='lines'
    )

    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_trace['x'] += (x0, x1, None)
        edge_trace['y'] += (y0, y1, None)

    node_trace = go.Scatter(
        x=[], y=[], text=[], mode='markers', hoverinfo='text',
        marker=dict(size=16, line_width=2, line_color='#0F172A')
    )

    colors = []
    texts = []
    for node in G.nodes():
        node_x, node_y = pos[node]
        node_trace['x'] += (node_x,)
        node_trace['y'] += (node_y,)
        
        if node in articulation_points:
            colors.append('#F43F5E') # Яскравий рожево-червоний для вразливостей
            texts.append(f"CRITICAL NODE {node}")
        else:
            colors.append('#38BDF8') # Світло-блакитний для стабільних вузлів
            texts.append(f"Node {node}")

    node_trace.marker.color = colors
    node_trace.text = texts

    fig = go.Figure(data=[edge_trace, node_trace],
                 layout=go.Layout(
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=0, l=0, r=0, t=0),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
                 ))
    
    st.plotly_chart(fig, use_container_width=True)

    # --- Аналітика ---
    st.markdown("### 📊 SECURITY LOG")
    if nodes_to_remove:
        st.error(f"ATTACK DETECTED: {len(nodes_to_remove)} nodes offline.")
        if components > 1:
            st.warning(f"CRITICAL: Network fragmented into {components} segments.")
    else:
        st.success("STATUS: All systems nominal. No active threats.")

if __name__ == "__main__":
    main()
