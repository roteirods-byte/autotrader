# BLOCO A1 - INICIO (dash_panels/app.py)
from dash import Dash, html
import dash_bootstrap_components as dbc
from dash_panels.pages.email import layout_email, register_callbacks

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.SLATE],
    suppress_callback_exceptions=True
)
server = app.server  # exigido pelo gunicorn

app.layout = html.Div(
    [
        html.H1("PAINÉIS DA AUTOMAÇÃO", className="title"),
        layout_email()  # por enquanto só a página EMAIL
    ],
    className="root"
)

register_callbacks(app)

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8050, debug=False)
# BLOCO A1 - FIM
