# panels/moedas_panel.py  — SUBSTITUA/CRIE INTEIRO
import streamlit as st
import pandas as pd

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

def _df():
    return pd.DataFrame(
        [st.session_state.moedas_db[s] for s, _ in COINS],
        columns=["Símbolo","Nome","Ativo?","Observação"]
    )

def _save(df: pd.DataFrame):
    for _, row in df.iterrows():
        sym = row["Símbolo"]
        st.session_state.moedas_db[sym]["Ativo?"] = bool(row["Ativo?"])
        st.session_state.moedas_db[sym]["Observação"] = str(row["Observação"] or "")

def render_moedas_panel():
    _init_state()
    st.subheader("MOEDAS")

    termo = st.text_input("Buscar (símbolo ou nome)", "")
    base = _df()
    if termo:
        t = termo.strip().lower()
        base = base[ base["Símbolo"].str.lower().str.contains(t) | base["Nome"].str.lower().str.contains(t) ]

    edit = st.data_editor(
        base, hide_index=True, num_rows="fixed", use_container_width=True,
        column_config={
            "Ativo?": st.column_config.CheckboxColumn("Ativo?", default=True, help="Habilita/Desabilita"),
            "Observação": st.column_config.TextColumn("Observação"),
        },
    )
    _save(edit)

    st.download_button(
        "Baixar CSV",
        data=edit.to_csv(index=False).encode("utf-8"),
        file_name="moedas.csv",
        mime="text/csv"
    )

    if st.button("Resetar lista (padrão)"):
        st.session_state.pop("moedas_db", None)
        st.rerun()
