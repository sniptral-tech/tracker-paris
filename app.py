import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Bankroll Tracker", page_icon="📈", layout="centered")

# --- Initialisation de la mémoire de session ---
if 'bankroll' not in st.session_state:
    st.session_state.bankroll = 20000.0
if 'history' not in st.session_state:
    st.session_state.history = []
if 'pct' not in st.session_state:
    st.session_state.pct = 2.0
if 'restored' not in st.session_state:
    st.session_state.restored = False

st.title("📈 Bankroll Tracker")

# --- Reprendre un historique sauvegardé (la mémoire de session se vide à chaque
#     fermeture d'onglet, donc on restaure depuis le CSV téléchargé la dernière fois) ---
if not st.session_state.restored and not st.session_state.history:
    with st.expander("📂 Reprendre un historique existant"):
        uploaded = st.file_uploader("Importer ton dernier fichier CSV sauvegardé", type="csv")
        if uploaded is not None:
            try:
                df_restore = pd.read_csv(uploaded)
                st.session_state.history = df_restore.to_dict('records')
                if len(df_restore) > 0 and 'Capital' in df_restore.columns:
                    st.session_state.bankroll = float(df_restore.iloc[-1]['Capital'])
                st.session_state.restored = True
                st.rerun()
            except Exception as e:
                st.error(f"Fichier illisible : {e}")

# --- Paramètres ---
with st.expander("⚙️ Modifier le capital ou la mise"):
    new_cap = st.number_input("Capital actuel (FCFA)", min_value=0.0, value=float(st.session_state.bankroll), step=500.0)
    new_pct = st.number_input("Pourcentage de mise (%)", min_value=0.5, max_value=10.0, value=float(st.session_state.pct), step=0.5)
    if st.button("Mettre à jour"):
        st.session_state.bankroll = new_cap
        st.session_state.pct = new_pct
        st.rerun()

pct = st.session_state.pct
mise = st.session_state.bankroll * (pct / 100)

st.info(f"**Capital actuel :** {st.session_state.bankroll:,.0f} FCFA\n\n**Mise à jouer ({pct}%) :** {mise:,.0f} FCFA")

# --- Résumé de performance ---
if st.session_state.history:
    df_stats = pd.DataFrame(st.session_state.history)
    df_stats['Bénéfice'] = pd.to_numeric(df_stats['Bénéfice'], errors='coerce').fillna(0)
    total = len(df_stats)
    wins = len(df_stats[df_stats['Résultat'] == 'Gagné'])
    win_rate = (wins / total * 100) if total else 0
    total_pnl = df_stats['Bénéfice'].sum()

    c1, c2, c3 = st.columns(3)
    c1.metric("Paris", total)
    c2.metric("Taux de réussite", f"{win_rate:.0f}%")
    c3.metric("P&L total", f"{total_pnl:+,.0f} FCFA")

st.write("### 📝 Nouveau Pari")
match_name = st.text_input("Match (ex: Newcastle vs Bournemouth)")
cote = st.number_input("Cote du pari", min_value=1.01, value=1.85, step=0.01)

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

# --- Historique, sauvegarde, réinitialisation ---
if st.session_state.history:
    st.write("### 📊 Historique")
    df = pd.DataFrame(st.session_state.history)
    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="💾 Sauvegarder (Fichier CSV)",
        data=csv,
        file_name='historique_bankroll.csv',
        mime='text/csv',
        use_container_width=True
    )
    st.caption("⚠️ Télécharge ce fichier avant de fermer l'app — c'est lui qui te permet de reprendre ton historique la prochaine fois.")

    with st.expander("🗑️ Réinitialiser"):
        st.warning("Efface tout l'historique et remet le capital à 20 000 FCFA.")
        if st.button("Confirmer la réinitialisation"):
            st.session_state.bankroll = 20000.0
            st.session_state.history = []
            st.session_state.restored = False
            st.rerun()
