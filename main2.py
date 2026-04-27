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

# Впровадження кастомного дизайну через CSS
st.markdown("""
    <style>
    /* Головний фон та шрифти */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Стилізація бічної панелі */
    .stSidebar {
        background-color: #f0f2f6;
        border-right: 2px solid #e6e9ef;
    }
    
    /* Стилізація заголовків */
    h1 {
        color: #1E3A8A; /* Темно-синій */
        font-weight: 700;
        text-align: center;
        border-bottom: 2px solid #3B82F6;
        padding-bottom: 10px;
    }
    
    /* Картки метрик */
    div[data-testid="stMetricValue"] {
        color: #2563EB;
        font-size: 28px;
    }
    
    /* Кнопки */
    .stButton>button {
        width: 100%;
        background-color: #3B82F6;
        color: white;
        border-radius: 8px;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #1E40AF;
        color: #ffffff;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    st.markdown("<h1>System Resilience Analyzer v2.0</h1>", unsafe_allow_html=True)
    
    # --- Бічна панель (Sidebar) ---
    st.sidebar.markdown("### ⚙️ Налаштування мережі")
    
    node_count = st.sidebar.slider("Кількість вузлів інфраструктури", 5, 60, 20)
    edge_prob = st.sidebar.slider("Щільність зв'язків", 0.05, 0.5, 0.15)
    
    if 'G' not in st.session_state or st.sidebar.button("🔄 Оновити топологію"):
        # Створення графа (моделювання мережі) [cite: 123]
        st.session_state.G = nx.erdos_renyi_graph(n=node_count, p=edge_prob, seed=random.randint(1, 1000))
        st.session_state.pos = nx.spring_layout(st.session_state.G)

    G = st.session_state.G.copy()
    pos = st.session_state.pos

    # --- Аналітичний блок (Кібербезпека) ---
    # Визначення критичних точок артикуляції [cite: 124, 127]
    articulation_points = set(nx.articulation_points(G))
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🛡️ Симуляція інцидентів")
    attack_mode = st.sidebar.radio("Оберіть сценарій атаки:", 
                                  ["Моніторинг", "Випадковий збій", "Таргетована атака"])
    
    nodes_to_remove = []
    if attack_mode == "Випадковий збій":
        fail_rate = st.sidebar.slider("Рівень деградації (%)", 0, 50, 10)
        num_to_del = int(node_count * (fail_rate / 100))
        nodes_to_remove = random.sample(list(G.nodes()), min(num_to_del, len(G.nodes())))
    
    elif attack_mode == "Таргетована атака":
        st.sidebar.warning("Атака спрямована на точки артикуляції!")
        nodes_to_remove = list(articulation_points)

    # Видалення вузлів та перерахунок метрик [cite: 166, 189]
    G.remove_nodes_from(nodes_to_remove)

    # --- Основна візуалізація ---
    m_col1, m_col2, m_col3 = st.columns(3)
    
    with m_col1:
        st.metric("Активні вузли", G.number_of_nodes())
    with m_col2:
        components = nx.number_connected_components(G) if G.number_of_nodes() > 0 else 0
        st.metric("Сегменти (Islands)", components)
    with m_col3:
        status = "СТІЙКА" if (G.number_of_nodes() > 0 and nx.is_connected(G)) else "КРИТИЧНА"
        st.metric("Статус мережі", status)

    # Побудова графіка Plotly [cite: 149, 162]
    edge_trace = go.Scatter(
        x=[], y=[], line=dict(width=1.5, color='#CBD5E1'), hoverinfo='none', mode='lines'
    )

    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_trace['x'] += (x0, x1, None)
        edge_trace['y'] += (y0, y1, None)

    node_trace = go.Scatter(
        x=[], y=[], text=[], mode='markers', hoverinfo='text',
        marker=dict(showscale=False, size=18, line_width=3, line_color='white')
    )

    colors = []
    texts = []
    for node in G.nodes():
        node_x, node_y = pos[node]
        node_trace['x'] += (node_x,)
        node_trace['y'] += (node_y,)
        
        if node in articulation_points:
            colors.append('#EF4444') # Червоний - критичний
            texts.append(f"Критичний вузол {node} (Точка артикуляції)")
        else:
            colors.append('#3B82F6') # Синій - стабільний
            texts.append(f"Вузол {node} (Статус: OK)")

    node_trace.marker.color = colors
    node_trace.text = texts

    fig = go.Figure(data=[edge_trace, node_trace],
                 layout=go.Layout(
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=0, l=0, r=0, t=40),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
                 ))
    
    st.plotly_chart(fig, use_container_width=True)

    # --- Аналітичний блок ---
    st.markdown("### 📋 Аналітичний висновок щодо безпеки")
    
    a_col1, a_col2 = st.columns(2)
    with a_col1:
        st.info(f"**Виявлені точки артикуляції:** {list(articulation_points) if articulation_points else 'Відсутні'}")
        st.write("Це вузли, вихід з ладу яких призведе до негайної втрати зв'язності мережі[cite: 124].")
    
    with a_col2:
        if nodes_to_remove:
            st.error(f"**Наслідки атаки:** Вилучено {len(nodes_to_remove)} вузлів.")
            if components > 1:
                st.warning(f"Мережа фрагментована на {components} частин. Потрібне негайне відновлення маршрутів[cite: 123, 126].")
        else:
            st.success("Система працює в штатному режимі. Усі вузли доступні.")

if __name__ == "__main__":
    main()