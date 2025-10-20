# panels/entrada_panel.py — Visual no modelo (duas seções: 4H e 1H)
# Streamlit puro, sem CSS pesado. Lê dados de:
# st.session_state["signals_4h"] e st.session_state["signals_1h"]
# (listas de dicts com chaves: simbolo, sinal, preco, alvo, ganho, assert, data, hora)

import streamlit as st
import pandas as pd

def _fmt_num(x, nd=3):
    try:
        return f"{float(x):.{nd}f}"
    except Exception:
        return str(x or "")

def _badge_sinal(sinal: str) -> str:
    s = (sinal or "").upper()
    if s == "SHORT":
        return '<span style="background:#EF4444;color:#fff;padding:2px 8px;border-radius:999px;font-weight:700;">SHORT</span>'
    if s == "LONG":
        return '<span style="background:#22C55E;color:#0B0B0B;padding:2px 8px;border-radius:999px;font-weight:700;">LONG</span>'
    return '<span style="opacity:.8">NÃO ENTRAR</span>'

def _render_section(titulo: str, key_list: str):
    st.markdown(f"### {titulo}")

    sinais = st.session_state.get(key_list, [])  # lista de dicts
    # Cabeçalho
    c = st.columns([1.1, 1, 1, 1, 1, 1, 1.2, 1])
    for col, h in zip(c, ["PAR", "SINAL", "PREÇO", "ALVO", "GANHO%", "ASSERT%", "DATA", "HORA"]):
        col.markdown(f"**{h}**")

    if not sinais:
        st.info("Sem dados para esta seção.")
        return

    linhas_csv = []
    for s in sinais:
        par = s.get("simbolo") or s.get("par") or "-"
        sinal = (s.get("sinal") or "").upper()
        preco = s.get("preco")
        alvo = s.get("alvo")
        ganho = s.get("ganho")
        assertv = s.get("assert")
        data = s.get("data")
        hora = s.get("hora")

        c1, c2, c3, c4, c5, c6, c7, c8 = st.columns([1.1, 1, 1, 1, 1, 1, 1.2, 1])
        c1.write(par)
        c2.markdown(_badge_sinal(sinal), unsafe_allow_html=True)
        c3.write(_fmt_num(preco, 3))
        c4.write(_fmt_num(alvo, 3))
        ganho_txt = _fmt_num(ganho, 2)
        if isinstance(ganho, (int, float)) and float(ganho) > 0:
            c5.markdown(f"<span style='color:#22C55E;font-weight:600'>{ganho_txt}</span>", unsafe_allow_html=True)
        else:
            c5.write(ganho_txt)
        c6.write(_fmt_num(assertv, 2))
        c7.write(str(data or ""))
        c8.write(str(hora or ""))

        linhas_csv.append({
            "PAR": par, "SINAL": sinal or "NAO_ENTRAR",
            "PRECO": preco, "ALVO": alvo, "GANHO%": ganho, "ASSERT%": assertv,
            "DATA": data, "HORA": hora
        })

    # Download CSV da seção
    df = pd.DataFrame(linhas_csv)
    st.download_button(
        f"Baixar CSV — {titulo}",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name=f"sinais_{key_list}.csv",
        mime="text/csv",
    )

def render_entrada_panel():
    st.subheader("ENTRADA")

    # Seções no padrão do seu modelo
    _render_section("ENTRADA 4H — SWING", "signals_4h")
    st.divider()
    _render_section("ENTRADA 1H — POSICIONAL", "signals_1h")
