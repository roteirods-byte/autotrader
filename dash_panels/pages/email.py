# BLOCO A2 - INICIO (dash_panels/pages/email.py)
from dash import html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from planilhas_streamlit_v2.services import get_email_cfg, save_email_cfg
from planilhas_streamlit_v2.schemas import EmailCfg
from pydantic import ValidationError

def layout_email():
    cfg = get_email_cfg()
    principal_val = cfg.principal if cfg else ""
    envio_val = cfg.envio if cfg else ""

    return html.Div(
        [
            html.Div("CORREIO ELETRÔNICO", className="section"),
            html.Div(
                [
                    html.Div([dbc.Label("Principal:"), dbc.Input(id="inp-principal", type="email", value=principal_val)], className="col"),
                    html.Div([dbc.Label("Senha:"),     dbc.Input(id="inp-senha", type="password")], className="col"),
                    html.Div([dbc.Label("Envio:"),     dbc.Input(id="inp-envio", type="email", value=envio_val)], className="col"),
                    html.Div([dbc.Button("TESTAR/SALVAR", id="btn-save", className="btn-260")], className="col"),
                ],
                className="email-row",
            ),
            html.Div(id="save-msg")
        ],
        className="email-card"
    )

def register_callbacks(app):
    @app.callback(
        Output("save-msg", "children"),
        Input("btn-save", "n_clicks"),
        State("inp-principal", "value"),
        State("inp-envio", "value"),
        prevent_initial_call=True
    )
    def _save(_, principal, envio):
        try:
            data = EmailCfg(principal=principal, envio=envio)
            save_email_cfg(data)
            return dbc.Alert(f"Configurações salvas. Teste simulado enviado para {envio}.", color="success", dismissable=True, duration=4000)
        except ValidationError:
            return dbc.Alert("Dados inválidos. Verifique os e-mails.", color="danger", dismissable=True)
# BLOCO A2 - FIM
