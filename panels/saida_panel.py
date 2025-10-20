# panels/saida_panel.py — sincroniza com MOEDAS (Streamlit puro)
import streamlit as st
import pandas as pd

def _moedas():
    return st.session_state.get("moedas_db", {})

def _ensure_sync():
    moedas = _moedas()
    db = st.session_state.get("saida_db", {})
    for sym, v in moedas.items():
        if sym not in db:
            db[sym] = {
                "Símbolo": sym,
                "Habilitar?": bool(v.get("Ativo?", True)),
                "TP %": 3.0,
                "SL %": 2.0,
                "Trailing %": 0.0,
                "Observação": "",
            }
    for sym in list(db):
        if sym not in moedas:
            db.pop(sym, None)
    st.session_state.saida_db = db

def _df(so_ativas: bool):
    moedas = _moedas()
    rows = []
    for sym, v in st.session_state.saida_db.items():
        if so_ativas and not moedas.get(sym, {}).get("Ativo?", True):
            continue
        rows.append(v)
    rows.sort(key=lambda x: x["Símbolo"])
    return pd.DataFrame(rows, columns=["Símbolo","Habilitar?","TP %","SL %","Trailing %","Observação"])

def _save(df: pd.DataFrame):
    for _, row in df.iterrows():
        sym = str(row["Símbolo"])
        if sym in st.session_state.saida_db:
            st.session_state.saida_db[sym]["Habilitar?"] = bool(row["Habilitar?"])
            st.session_state.saida_db[sym]["TP %"] = float(row["TP %"] or 0)
            st.session_state.saida_db[sym]["SL %"] = float(row["SL %"] or 0)
            st.session_state.saida_db[sym]["Trailing %"] = float(row["Trailing %"] or 0)
            st.session_state.saida_db[sym]["Observação"] = str(row["Observação"] or "")

def render_saida_panel():
    _ensure_sync()
    st.subheader("SAÍDA")

    so_ativas = st.checkbox("Mostrar apenas moedas ativas", value=True, key="saida_show_active")
    base = _df(so_ativas)

    edit = st.data_editor(
        base, hide_index=True, num_rows="fixed", use_container_width=True,
        column_config={
            "Habilitar?": st.column_config.CheckboxColumn("Habilitar?", default=True),
            "TP %": st.column_config.NumberColumn("TP %", step=0.1, format="%.2f"),
            "SL %": st.column_config.NumberColumn("SL %", step=0.1, format="%.2f"),
            "Trailing %": st.column_config.NumberColumn("Trailing %", step=0.1, format="%.2f"),
        },
    )
    _save(edit)

    csv = edit.to_csv(index=False).encode("utf-8")
    st.download_button("Baixar CSV (Saída)", data=csv, file_name="saida.csv", mime="text/csv")
