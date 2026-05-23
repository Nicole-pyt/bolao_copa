import streamlit as st
import pandas as pd
from datetime import datetime
import pytz

st.set_page_config(page_title="Bolão da Copa", layout="wide", page_icon="⚽")
st.title("🏆 Bolão da Copa 2026")

# CONFIGURAÇÃO
ARQUIVO_APOSTAS = 'respostas_forms.csv'
ABA_PLANILHA = 'Respostas ao formulário 1'
TZ_BRASILIA = pytz.timezone('America/Sao_Paulo')
HOJE = datetime.now(TZ_BRASILIA).date()

# RESULTADOS - cadastra todos os jogos previstos aqui
RESULTADOS = {
    'México x África do Sul': {'casa': 2, 'fora': 1, 'data': '2026-05-11'},
    'Coréia do Sul x República Tcheca': {'casa': 2, 'fora': 1, 'data': '2026-06-11'},
    'Canadá x Bósnia e Herzegovina': {'casa': 2, 'fora': 1, 'data': '2026-06-12'},
    'EUA x Paraguai': {'casa': 2, 'fora': 1, 'data': '2026-06-12'},
    'Qatar x Suíça': {'casa': 2, 'fora': 1, 'data': '2026-06-13'},
    'Brasil x Marrocos': {'casa': 2, 'fora': 1, 'data': '2026-06-13'},
    'Haiti x Escócia': {'casa': 2, 'fora': 1, 'data': '2026-06-14'},
    'Austrália x Turquia': {'casa': 2, 'fora': 1, 'data': '2026-06-14'},
    'Alemanha x Curaçao': {'casa': 2, 'fora': 1, 'data': '2026-06-14'},
    'Holanda x Japão': {'casa': 2, 'fora': 1, 'data': '2026-06-14'},
    'Costa do Marfim x Equador': {'casa': 2, 'fora': 1, 'data': '2026-06-14'},
    'Suécia x Tunísia': {'casa': 2, 'fora': 1, 'data': '2026-06-14'},
}

def calcular_pontos(p_casa, p_fora, r_casa, r_fora):
    pontos = 0
    if (p_casa > p_fora and r_casa > r_fora) or \
       (p_casa < p_fora and r_casa < r_fora) or \
       (p_casa == p_fora and r_casa == r_fora):
        pontos += 5
    if p_casa == r_casa:
        pontos += 2
    if p_fora == r_fora:
        pontos += 2
    if p_casa == r_casa and p_fora == r_fora:
        pontos += 3
    return pontos

def jogo_ja_aconteceu(data_jogo_str):
    data_jogo = datetime.strptime(data_jogo_str, '%Y-%m-%d').date()
    return HOJE >= data_jogo

@st.cache_data(ttl=600)
def carregar_apostas():
    df = pd.read_csv('respostas_forms.csv')
    df = df.rename(columns={
        'Nome completo': 'Nome',
        'Qual o jogo?': 'Jogo',
        'Gols Time da Casa': 'Palpite_Casa',
        'Gols Time Visitante': 'Palpite_Fora'
    })
    df['Jogo'] = df['Jogo'].str.strip()
    return df

@st.cache_data
def calcula_ranking(_df_apostas, _resultados, _hoje):
    ranking = []
    for nome in _df_apostas['Nome'].unique():
        apostas_user = _df_apostas[_df_apostas['Nome'] == nome]
        total_pontos = 0
        jogos_computados = 0
        for _, row in apostas_user.iterrows():
            jogo = row['Jogo']
            if jogo in _resultados:
                res = _resultados[jogo]
                if _hoje >= datetime.strptime(res['data'], '%Y-%m-%d').date():
                    pts = calcular_pontos(row['Palpite_Casa'], row['Palpite_Fora'], res['casa'], res['fora'])
                    total_pontos += pts
                    jogos_computados += 1
        ranking.append({'Nome': nome, 'Pontos': total_pontos, 'Jogos': jogos_computados})

    df_ranking = pd.DataFrame(ranking).sort_values(['Pontos', 'Jogos'], ascending=[False, False]).reset_index(drop=True)
    df_ranking.index += 1
    df_ranking.index.name = 'Pos'
    return df_ranking

df_apostas = carregar_apostas()

tab1, tab2, tab3 = st.tabs(["📅 Jogos", "🏅 Ranking", "📊 Regras"])

with tab1:
    st.header("Jogos e Palpites")
    jogos_cadastrados = list(RESULTADOS.keys())
    jogos_apostados = df_apostas['Jogo'].unique().tolist()
    todos_jogos = sorted(list(set(jogos_cadastrados + jogos_apostados)))

    jogo_selecionado = st.selectbox("Selecione o jogo:", todos_jogos)

    if jogo_selecionado in RESULTADOS:
        res = RESULTADOS[jogo_selecionado]
        if jogo_ja_aconteceu(res['data']):
            st.success(f"**Resultado Final:** {res['casa']} x {res['fora']} | **Data:** {res['data']}")
            jogo_finalizado = True
        else:
            st.warning(f"**Jogo ainda não aconteceu** | **Data:** {res['data']} | **Placar:** 0 x 0")
            jogo_finalizado = False
    else:
        st.info("Jogo cadastrado sem resultado previsto")
        jogo_finalizado = False

    palpites = df_apostas[df_apostas['Jogo'] == jogo_selecionado][['Nome', 'Palpite_Casa', 'Palpite_Fora']].copy()

    if not palpites.empty:
        palpites['Palpite'] = palpites['Palpite_Casa'].astype(str) + ' x ' + palpites['Palpite_Fora'].astype(str)
        if jogo_selecionado in RESULTADOS and jogo_finalizado:
            res = RESULTADOS[jogo_selecionado]
            palpites['Pontos'] = palpites.apply(
                lambda x: calcular_pontos(x['Palpite_Casa'], x['Palpite_Fora'], res['casa'], res['fora']), axis=1
            )
            palpites = palpites.sort_values('Pontos', ascending=False)
            st.dataframe(palpites[['Nome', 'Palpite', 'Pontos']], hide_index=True, use_container_width=True)
        else:
            st.dataframe(palpites[['Nome', 'Palpite']], hide_index=True, use_container_width=True)
    else:
        st.write("Nenhum palpite registrado para este jogo ainda.")

with tab2:
    st.header("Ranking Geral")
    df_ranking = calcula_ranking(df_apostas, RESULTADOS, HOJE)
    st.dataframe(df_ranking, use_container_width=True)

with tab3:
    st.header("Regras de Pontuação")
    st.write("""
    **5 pontos**: Acertar o vencedor ou empate

    **3 pontos**: Acertar o placar exato

    **2 pontos**: Acertar gols do time da casa

    **2 pontos**: Acertar gols do time visitante

    *Todas as regras somam. Placar exato = 12 pontos*
    """)
    st.caption(f"Data de hoje: {HOJE.strftime('%d/%m/%Y')} - Horário de Brasília | Jogos são contabilizados automaticamente após a data")
