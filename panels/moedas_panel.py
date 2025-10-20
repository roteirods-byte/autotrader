# panels/moedas_panel.py — Adicionar / Excluir / Editar (Streamlit puro)
import streamlit as st
import pandas as pd
import re

# Lista padrão (39)
DEFAULT_COINS = [
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
            sym: {"Símbolo": sym, "Nome": name, "Ativo?": True, "Observação": "", "Excluir?": False}
            for sym, name in DEFAULT_COINS
        }

def _df_from_state():
    data = list(st.session_state.moedas_db.values())
    data.sort(key=lambda x: x["Símbolo"])
    return pd.DataFrame(data, columns=["Símbolo","Nome","Ativo?","Observação","Excluir?"])

def _persist_edit(df: pd.DataFrame):
    # Atualiza edição de linhas existentes (Ativo/Obs/Excluir)
    seen = set()
    for _, row in df.iterrows():
        sym = str(row["Símbolo"]).strip().upper()
        if not sym:
            continue
        seen.add(sym)
        if sym not in st.session_state.moedas_db:
            # Novo símbolo digitado direto na tabela (não recomendado, mas aceito)
            st.session_state.moedas_db[sym] = {
                "Símbolo": sym, "Nome": str(row["Nome"] or "").strip() or sym,
                "Ativo?": bool(row["Ativo?"]), "Observação": str(row["Observação"] or ""),
                "Excluir?": bool(row.get("Excluir?", False))
            }
        else:
            st.session_state.moedas_db[sym]["Nome"] = str(row["Nome"] or "").strip() or sym
            st.session_state.moedas_db[sym]["Ativo?"] = bool(row["Ativo?"])
            st.session_state.moedas_db[sym]["Observação"] = str(row["Observação"] or "")
            st.session_state.moedas_db[sym]["Excluir?"] = bool(row.get("Excluir?", False))
    # Remove símbolos que foram apagados manualmente da tabela (caso aconteça)
    to_del = [s for s in list(st.session_state.moedas_db) if s not in seen]
    for s in to_del:
        st.session_state.moedas_db.pop(s, None)

def _add_symbol(sym: str, name: str) -> str | None:
    sym = (sym or "").strip().upper()
    name = (name or "").strip()
    if not sym or not re.fullmatch(r"[A-Z0-9]{2,8}", sym):
        return "Símbolo inválido (use 2–8 letras/números, sem espaços)."
    if sym in st.session_state.moedas_db:
        return "Símbolo já existe."
    if not name:
        name = sym
    st.session_state.moedas_db[sym] = {
        "Símbolo": sym, "Nome": name, "Ativo?": True, "Observação": "", "Excluir?": False
    }
    return None

def _apply_deletions():
    to_delete = [s for s, v in st.session_state.moedas_db.items() if v.get("Excluir?")]
    for s in to_delete:
        st.session_state.moedas_db.pop(s, None)

def render_moedas_panel():
    _init_state()
    st.subheader("MOEDAS")

    # --- Adicionar moeda ---
    c1, c2, c3 = st.columns([2, 3, 1.2])
    with c1:
        novo_sym = st.text_input("Novo símbolo", placeholder="ex.: ABC")
    with c2:
        novo_nome = st.text_input("Nome da moeda", placeholder="Nome (opcional)")
    with c3:
        if st.button("Adicionar"):
            msg = _add_symbol(novo_sym, novo_nome)
            if msg:
                st.error(msg, icon="⚠️")
            else:
                st.success(f"Moeda {novo_sym.strip().upper()} adicionada.", icon="✅")
                st.rerun()

    # --- Filtro de busca ---
    termo = st.text_input("Buscar (símbolo ou nome)", "")

    base = _df_from_state()
    if termo:
        t = termo.strip().lower()
        base = base[
            base["Símbolo"].str.lower().str.contains(t)
            | base["Nome"].str.lower().str.contains(t)
        ]

    # --- Editor: permite marcar 'Excluir?' e ajustar campos ---
    edit = st.data_editor(
        base,
        hide_index=True,
        use_container_width=True,
        num_rows="dynamic",  # permite inserir linha nova (opcional)
        column_config={
            "Ativo?": st.column_config.CheckboxColumn("Ativo?", default=True),
            "Observação": st.column_config.TextColumn("Observação"),
            "Excluir?": st.column_config.CheckboxColumn("Excluir?", default=False),
        },
    )

    # Persistir alterações da edição
    _persist_edit(edit)

    # Botões de ação
    c4, c5 = st.columns([1.2, 1])
    with c4:
        if st.button("Aplicar alterações"):
            _apply_deletions()
            st.success("Alterações aplicadas.", icon="✅")
            st.rerun()
    with c5:
        csv = edit.to_csv(index=False).encode("utf-8")
        st.download_button("Baixar CSV", data=csv, file_name="moedas.csv", mime="text/csv")

    # Reset para o padrão
    if st.button("Resetar lista (padrão)"):
        st.session_state.pop("moedas_db", None)
        st.rerun()
