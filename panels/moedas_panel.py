# panels/moedas_panel.py  — Streamlit puro (tabela do operador)
import streamlit as st
import pandas as pd

# Lista fixa das 39 moedas
COINS = [
    ("AAVE","Aave"), ("ADA","Cardano"), ("APT","Aptos"), ("ARB","Arbitrum"),
    ("ATOM","Cosmos"), ("AVAX","Avalanche"), ("AXS","Axie"), ("BCH","Bitcoin Cash"),
    ("BNB","BNB"), ("BTC","Bitcoin"), ("DOGE","Dogecoin"), ("DOT","Polkadot"),
    ("ETH","Ethereum"), ("FET","FET"), ("FIL","Filecoin"), ("FLUX","Flux"),
    ("ICP","ICP"), ("INJ","Injective"), ("LDO","Lido"), ("LINK","Chainlink"),
    ("LTC","Litecoin"), ("NEAR","NEAR"), ("OP","Optimism"), ("PEPE","PEPE"),
    ("POL","POL"), ("RATS","RATS"), ("RENDER","Render"), ("RUNE","Rune"),
    ("SEI","SEI"), ("SHIB","Shiba"), ("SOL","Solana"), ("SUI","Sui"),
    ("TIA","TIA"), ("TNSR","TNSR"), ("TON","TON"), ("TRX","TRX"),
    ("UNI","Uniswap"), ("WIF","WIF"), ("XRP","XRP")
]

def _init_state():
    if "moedas_db" not in st.session_state:
        st.session_state.moedas_db = {
            sym: {"Símbolo": sym, "Nome": name, "Ativo?": True, "Observação": ""}
            for sym, name in COINS
        }

def _df_from_state():
    rows = [st.session_state.moedas_db[s] for s, _ in COINS]
    return pd.DataFrame(rows, columns=["Símbolo","Nome","Ativo?","Observação"])

def _persist_back(df: pd.DataFrame):
    for _, row in df.iterrows():
        sym = row["Símbolo"]
        st.session_state.moedas_db[sym]["Ativo?"] = bool(row["Ativo?"])
        st.session_state.moedas_db[sym]["Observação"] = str(row["Observação"] or "")

def render_moedas_panel():
    _init_state()

    st.subheader("MOEDAS")
    termo = st.text_input("Buscar (símbolo ou nome)", "")

    df = _df_from_state()
    if termo:
        t = termo.strip().lower()
        df = df[df["Símbolo"].str.lower().str.contains(t) | df["Nome"].str.lower().str.contains(t)]

    edit = st.data_editor(
        df,
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
    )

    _persist_back(edit)

    csv = edit.to_csv(index=False).encode("utf-8")
    st.download_button("Baixar CSV", data=csv, file_name="moedas.csv", mime="text/csv")
