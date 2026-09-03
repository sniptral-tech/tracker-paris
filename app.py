import streamlit as st
import pandas as pd
from datetime import datetime

# Configuration optimisée pour mobile
st.set_page_config(page_title="Bankroll Bot", page_icon="📈", layout="centered")

# Initialisation de la mémoire
if 'bankroll' not in st.session_state:
    st.session_state.bankroll = 20000.0
if 'history' not in st.session_state:
    st.session_state.history = []

st.title("📈 Bankroll Tracker")

# Paramètres cachés par défaut pour économiser l'espace écran
with st.expander("⚙️ Modifier le capital ou la mise"):
    new_cap = st.number_input("Capital actuel (FCFA)", value=float(st.session_state.bankroll), step=500.0)
    pct = st.number_input("Pourcentage de mise (%)", value=2.0, step=0.5)
    if st.button("Mettre à jour"):
        st.session_state.bankroll = new_cap
        st.rerun()
else:
    pct = 2.0

# Calcul automatique de la mise
mise = st.session_state.bankroll * (pct / 100)

# Affichage central et bien visible
st.info(f"**Capital actuel :** {st.session_state.bankroll:,.0f} FCFA\n\n**Mise à jouer ({pct}%) :** {mise:,.0f} FCFA")

st.write("### 📝 Nouveau Pari")
match_name = st.text_input("Match (ex: Newcastle vs Bournemouth)")
cote = st.number_input("Cote du pari", min_value=1.01, value=1.85, step=0.01)

# Boutons de validation tactiles et larges
col1, col2 = st.columns(2)
with col1:
    if st.button("✅ GAGNÉ", type="primary", use_container_width=True):
        gain_net = (mise * cote) - mise
        st.session_state.bankroll += gain_net
        st.session_state.history.append({
            "Date": datetime.now().strftime("%d/%m %H:%M"), 
            "Match": match_name if match_name else "Pari", 
            "Cote": cote, 
            "Mise": round(mise), 
            "Résultat": "Gagné", 
            "Bénéfice": round(gain_net), 
            "Capital": round(st.session_state.bankroll)
        })
        st.rerun()
with col2:
    if st.button("❌ PERDU", use_container_width=True):
        st.session_state.bankroll -= mise
        st.session_state.history.append({
            "Date": datetime.now().strftime("%d/%m %H:%M"), 
            "Match": match_name if match_name else "Pari", 
            "Cote": cote, 
            "Mise": round(mise), 
            "Résultat": "Perdu", 
            "Bénéfice": round(-mise), 
            "Capital": round(st.session_state.bankroll)
        })
        st.rerun()

# Affichage de l'historique
if st.session_state.history:
    st.write("### 📊 Historique")
    df = pd.DataFrame(st.session_state.history)
    st.dataframe(df, use_container_width=True)
    
    # Système de sauvegarde pour éviter de perdre les données sur mobile
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="💾 Sauvegarder (Fichier CSV)", 
        data=csv, 
        file_name='historique_bankroll.csv', 
        mime='text/csv',
        use_container_width=True
    )
