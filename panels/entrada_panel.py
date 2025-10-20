# panels/entrada_panel.py — sincroniza com MOEDAS (Streamlit puro)
import streamlit as st
import pandas as pd

def _moedas():  # mapa símbolos -> dados da MOEDAS
    return st.session_state.get("moedas_db", {})

def _ensure_sync():
    moedas = _moedas()
    db = st.session_state.get("entrada_db", {})
    # adiciona novos símbolos
    for sym, v in moedas.items():
        if sym not in db:
            db[sym] = {
                "Símbolo": sym,
                "Habilitar?": bool(v.get("Ativo?", True)),
                "Preço entrada": 0.0,
                "Observação": "",
            }
    # remove símbolos deletados em MOEDAS
    for sym in list(db):
        if sym not in moedas:
            db.pop(sym, None)
    st.session_state.entrada_db = db

def _df(so_ativas: bool):
    moedas = _moedas()
    rows = []
    for sym, v in st.session_state.entrada_db.items():
        if so_ativas and not moedas.get(sym, {}).get("Ativo?", True):
            continue
        rows.append(v)
    rows.sort(key=lambda x: x["Símbolo"])
    return pd.DataFrame(rows, columns=["Símbolo","Habilitar?","Preço entrada","Observação"])

def _save(df: pd.DataFrame):
    for _, row in df.iterrows():
        sym = str(row["Símbolo"])
        if sym in st.session_state.entrada_db:
            st.session_state.entrada_db[sym]["Habilitar?"] = bool(row["Habilitar?"])
            st.session_state.entrada_db[sym]["Preço entrada"] = float(row["Preço entrada"] or 0)
            st.session_state.entrada_db[sym]["Observação"] = str(row["Observação"] or "")

def render_entrada_panel():
    _ensure_sync()
    st.subheader("ENTRADA")

    so_ativas = st.checkbox("Mostrar apenas moedas ativas", value=True)
    base = _df(so_ativas)

    edit = st.data_editor(
        base, hide_index=True, num_rows="fixed", use_container_width=True,
        column_config={
            "Preço entrada": st.column_config.NumberColumn("Preço entrada", step=0.0001, format="%.6f"),
            "Habilitar?": st.column_config.CheckboxColumn("Habilitar?", default=True),
        },
    )
    _save(edit)

    csv = edit.to_csv(index=False).encode("utf-8")
    st.download_button("Baixar CSV (Entrada)", data=csv, file_name="entrada.csv", mime="text/csv")
