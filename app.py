"""
Dashboard de Mortalidad en Colombia 2019
Desarrollado con Python, Plotly y Dash
Despliegue: Azure App Service
"""

import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import dash
from dash import dcc, html, dash_table

# ─────────────────────────────────────────────
# 1. CARGA Y PREPROCESAMIENTO DE DATOS
# ─────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Datos de mortalidad
df = pd.read_excel(os.path.join(BASE_DIR, "data/Anexo1.NoFetal2019_CE_15-03-23.xlsx"))

# DIVIPOLA – División política
div = pd.read_excel(os.path.join(BASE_DIR, "data/Divipola_CE_.xlsx"))

# Códigos de causas de muerte
df_codes = pd.read_excel(
    os.path.join(BASE_DIR, "data/Anexo2.CodigosDeMuerte_CE_15-03-23.xlsx"),
    sheet_name="Final",
    skiprows=8,
    header=0,
)
df_codes.columns = [
    "CAPITULO", "NOMBRE_CAPITULO",
    "COD_3", "DESC_3",
    "COD_4", "DESC_4",
]
df_codes = df_codes.dropna(subset=["COD_3"]).drop_duplicates("COD_3")

# Merge principal: mortalidad + DIVIPOLA
datos = df.merge(div, on="COD_DANE", how="left")

# Mapeo de sexo
SEXO_MAP = {1: "Masculino", 2: "Femenino", 3: "Indeterminado"}
datos["SEXO_NOMBRE"] = datos["SEXO"].map(SEXO_MAP)

# Mapeo de mes
MESES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre",
}
datos["MES_NOMBRE"] = datos["MES"].map(MESES)

# Mapeo GRUPO_EDAD1
GRUPO_EDAD = {
    (0, 4):   "Mort. neonatal (<1 mes)",
    (5, 6):   "Mort. infantil (1-11 meses)",
    (7, 8):   "Primera infancia (1-4 años)",
    (9, 10):  "Niñez (5-14 años)",
    (11, 11): "Adolescencia (15-19 años)",
    (12, 13): "Juventud (20-29 años)",
    (14, 16): "Adultez temprana (30-44 años)",
    (17, 19): "Adultez intermedia (45-59 años)",
    (20, 24): "Vejez (60-84 años)",
    (25, 28): "Longevidad (85-100+ años)",
    (29, 29): "Edad desconocida",
}

ORDEN_EDAD = [
    "Mort. neonatal (<1 mes)",
    "Mort. infantil (1-11 meses)",
    "Primera infancia (1-4 años)",
    "Niñez (5-14 años)",
    "Adolescencia (15-19 años)",
    "Juventud (20-29 años)",
    "Adultez temprana (30-44 años)",
    "Adultez intermedia (45-59 años)",
    "Vejez (60-84 años)",
    "Longevidad (85-100+ años)",
    "Edad desconocida",
]


def categorizar_edad(codigo):
    for (low, high), label in GRUPO_EDAD.items():
        if low <= codigo <= high:
            return label
    return "Desconocido"


datos["ETAPA_VIDA"] = datos["GRUPO_EDAD1"].apply(categorizar_edad)

# ─────────────────────────────────────────────
# 2. FIGURAS
# ─────────────────────────────────────────────

# ── Paleta de colores institucional ──────────
COLOR_PRIMARIO   = "#003087"   # azul DANE
COLOR_SECUNDARIO = "#C8102E"   # rojo Colombia
COLOR_ACENTO     = "#F4C300"   # amarillo Colombia
COLOR_FONDO      = "#F7F9FC"
PLANTILLA        = "plotly_white"

# ────────────────────────────────────────────
# GRÁFICO 1 · MAPA – Muertes totales por departamento
# ────────────────────────────────────────────
muertes_dpto = (
    datos.groupby(["COD_DEPARTAMENTO_x", "DEPARTAMENTO"])
    .size()
    .reset_index(name="TOTAL")
    .rename(columns={"COD_DEPARTAMENTO_x": "COD_DPTO"})
)

# GeoJSON de Colombia por departamentos – archivo local.
GEOJSON_PATH = os.path.join(BASE_DIR, "data/Colombia.geo.json")
try:
    with open(GEOJSON_PATH, "r", encoding="utf-8") as _f:
        colombia_geo = json.load(_f)
    # Normalizar id para hacer match con COD_DPTO
    for feat in colombia_geo["features"]:
        feat["id"] = str(feat["properties"].get("DPTO", ""))
    muertes_dpto["COD_STR"] = muertes_dpto["COD_DPTO"].astype(str).str.zfill(2)

    fig_mapa = px.choropleth(
        muertes_dpto,
        geojson=colombia_geo,
        locations="COD_STR",
        color="TOTAL",
        hover_name="DEPARTAMENTO",
        hover_data={"TOTAL": True, "COD_STR": False},
        color_continuous_scale="Blues",
        labels={"TOTAL": "Muertes"},
        title="Mapa – Distribución Total de Muertes por Departamento · Colombia 2019",
    )
    fig_mapa.update_geos(
        fitbounds="locations",
        visible=False,
        bgcolor=COLOR_FONDO,
    )
except Exception:
    # Fallback: mapa de barras si el GeoJSON no está disponible
    fig_mapa = px.bar(
        muertes_dpto.sort_values("TOTAL", ascending=True).tail(20),
        x="TOTAL",
        y="DEPARTAMENTO",
        orientation="h",
        color="TOTAL",
        color_continuous_scale="Blues",
        labels={"TOTAL": "Total de Muertes", "DEPARTAMENTO": "Departamento"},
        title="Mapa – Total de Muertes por Departamento · Colombia 2019",
        template=PLANTILLA,
    )

fig_mapa.update_layout(
    plot_bgcolor=COLOR_FONDO,
    paper_bgcolor=COLOR_FONDO,
    font_family="Arial",
    title_font_size=16,
    title_font_color=COLOR_PRIMARIO,
    coloraxis_colorbar_title_text="Muertes",
)

# ────────────────────────────────────────────
# GRÁFICO 2 · LÍNEAS – Muertes totales por mes
# ────────────────────────────────────────────
muertes_mes = (
    datos.groupby("MES").size()
    .reset_index(name="TOTAL")
    .sort_values("MES")
)
muertes_mes["MES_NOMBRE"] = muertes_mes["MES"].map(MESES)

fig_lineas = px.line(
    muertes_mes,
    x="MES_NOMBRE",
    y="TOTAL",
    markers=True,
    labels={"MES_NOMBRE": "Mes", "TOTAL": "Total de Muertes"},
    title="Gráfico de Líneas – Total de Muertes por Mes · Colombia 2019",
    template=PLANTILLA,
    color_discrete_sequence=[COLOR_PRIMARIO],
    category_orders={"MES_NOMBRE": list(MESES.values())},
)
fig_lineas.update_traces(
    line_width=2.5,
    marker_size=8,
    marker_color=COLOR_SECUNDARIO,
)
fig_lineas.update_layout(
    plot_bgcolor=COLOR_FONDO,
    paper_bgcolor=COLOR_FONDO,
    font_family="Arial",
    title_font_size=16,
    title_font_color=COLOR_PRIMARIO,
    xaxis_title="Mes",
    yaxis_title="Total de Muertes",
    hovermode="x unified",
)

# ────────────────────────────────────────────
# GRÁFICO 3 · BARRAS – Top 5 ciudades más violentas (X95)
# ────────────────────────────────────────────
homicidios_x95 = datos[datos["COD_MUERTE"].str.startswith("X95", na=False)]
top5_violencia = (
    homicidios_x95.groupby("MUNICIPIO").size()
    .reset_index(name="HOMICIDIOS")
    .sort_values("HOMICIDIOS", ascending=False)
    .head(5)
)

fig_violencia = px.bar(
    top5_violencia.sort_values("HOMICIDIOS"),
    x="HOMICIDIOS",
    y="MUNICIPIO",
    orientation="h",
    color="HOMICIDIOS",
    color_continuous_scale=["#FFCCCC", COLOR_SECUNDARIO],
    labels={"HOMICIDIOS": "Homicidios (X95)", "MUNICIPIO": "Ciudad"},
    title="Gráfico de Barras – 5 Ciudades más Violentas · Homicidios Código X95 · Colombia 2019",
    template=PLANTILLA,
    text="HOMICIDIOS",
)
fig_violencia.update_traces(textposition="outside", textfont_size=12)
fig_violencia.update_layout(
    plot_bgcolor=COLOR_FONDO,
    paper_bgcolor=COLOR_FONDO,
    font_family="Arial",
    title_font_size=15,
    title_font_color=COLOR_PRIMARIO,
    showlegend=False,
    coloraxis_showscale=False,
    xaxis_title="Homicidios (X95)",
    yaxis_title="Ciudad",
)

# ────────────────────────────────────────────
# GRÁFICO 4 · CIRCULAR – 10 ciudades con menor mortalidad
# ────────────────────────────────────────────
muertes_ciudad = (
    datos.groupby("MUNICIPIO").size()
    .reset_index(name="TOTAL")
)
bottom10 = (
    muertes_ciudad[muertes_ciudad["TOTAL"] > 0]
    .sort_values("TOTAL")
    .head(10)
)

fig_circular = px.pie(
    bottom10,
    names="MUNICIPIO",
    values="TOTAL",
    title="Gráfico Circular – 10 Ciudades con Menor Índice de Mortalidad · Colombia 2019",
    template=PLANTILLA,
    hole=0.35,
    color_discrete_sequence=px.colors.qualitative.Set3,
)
fig_circular.update_traces(
    textposition="inside",
    textinfo="percent+label",
    hovertemplate="<b>%{label}</b><br>Muertes: %{value}<extra></extra>",
)
fig_circular.update_layout(
    plot_bgcolor=COLOR_FONDO,
    paper_bgcolor=COLOR_FONDO,
    font_family="Arial",
    title_font_size=16,
    title_font_color=COLOR_PRIMARIO,
    legend_title_text="Municipio",
)

# ────────────────────────────────────────────
# GRÁFICO 5 · TABLA – Top 10 causas de muerte
# ────────────────────────────────────────────
datos["COD_3"] = datos["COD_MUERTE"].str[:3]
top10_causas = (
    datos["COD_3"].value_counts()
    .head(10)
    .reset_index()
)
top10_causas.columns = ["CÓDIGO", "TOTAL"]
top10_causas = top10_causas.merge(
    df_codes[["COD_3", "DESC_3"]].rename(columns={"COD_3": "CÓDIGO", "DESC_3": "DESCRIPCIÓN"}),
    on="CÓDIGO",
    how="left",
)
top10_causas = top10_causas[["CÓDIGO", "DESCRIPCIÓN", "TOTAL"]].sort_values(
    "TOTAL", ascending=False
)
top10_causas.index = range(1, len(top10_causas) + 1)

tabla_causas = dash_table.DataTable(
    data=top10_causas.to_dict("records"),
    columns=[
        {"name": "Código CIE-10", "id": "CÓDIGO"},
        {"name": "Causa de Muerte",  "id": "DESCRIPCIÓN"},
        {"name": "Total de Casos",   "id": "TOTAL"},
    ],
    sort_action="native",
    style_table={"overflowX": "auto", "borderRadius": "8px"},
    style_header={
        "backgroundColor": COLOR_PRIMARIO,
        "color": "white",
        "fontWeight": "bold",
        "textAlign": "center",
        "fontSize": "13px",
        "fontFamily": "Arial",
        "padding": "10px",
    },
    style_data={
        "fontFamily": "Arial",
        "fontSize": "13px",
        "color": "#333333",
        "border": "1px solid #e0e0e0",
    },
    style_data_conditional=[
        {
            "if": {"row_index": "odd"},
            "backgroundColor": "#EEF2FB",
        },
        {
            "if": {"column_id": "TOTAL"},
            "textAlign": "center",
            "fontWeight": "bold",
            "color": COLOR_SECUNDARIO,
        },
    ],
    style_cell={
        "padding": "10px 14px",
        "textAlign": "left",
        "whiteSpace": "normal",
        "height": "auto",
    },
)

# ────────────────────────────────────────────
# GRÁFICO 6 · BARRAS APILADAS – Muertes por sexo y departamento
# ────────────────────────────────────────────
muertes_sexo_dpto = (
    datos[datos["SEXO"].isin([1, 2])]
    .groupby(["DEPARTAMENTO", "SEXO_NOMBRE"])
    .size()
    .reset_index(name="TOTAL")
)

fig_sexo = px.bar(
    muertes_sexo_dpto,
    x="DEPARTAMENTO",
    y="TOTAL",
    color="SEXO_NOMBRE",
    barmode="stack",
    labels={
        "DEPARTAMENTO": "Departamento",
        "TOTAL": "Total de Muertes",
        "SEXO_NOMBRE": "Sexo",
    },
    title="Gráfico de Barras Apiladas – Muertes por Sexo en cada Departamento · Colombia 2019",
    template=PLANTILLA,
    color_discrete_map={
        "Masculino": COLOR_PRIMARIO,
        "Femenino":  COLOR_SECUNDARIO,
    },
    category_orders={
        "SEXO_NOMBRE": ["Masculino", "Femenino"]
    },
)
fig_sexo.update_layout(
    plot_bgcolor=COLOR_FONDO,
    paper_bgcolor=COLOR_FONDO,
    font_family="Arial",
    title_font_size=16,
    title_font_color=COLOR_PRIMARIO,
    xaxis_tickangle=-45,
    xaxis_title="Departamento",
    yaxis_title="Total de Muertes",
    legend_title_text="Sexo",
    bargap=0.15,
)

# ────────────────────────────────────────────
# GRÁFICO 7 · HISTOGRAMA – Distribución por GRUPO_EDAD1
# ────────────────────────────────────────────
conteo_edad = (
    datos.groupby("ETAPA_VIDA").size()
    .reset_index(name="TOTAL")
)
conteo_edad["ETAPA_VIDA"] = pd.Categorical(
    conteo_edad["ETAPA_VIDA"], categories=ORDEN_EDAD, ordered=True
)
conteo_edad = conteo_edad.sort_values("ETAPA_VIDA")

fig_hist = px.bar(
    conteo_edad,
    x="ETAPA_VIDA",
    y="TOTAL",
    color="TOTAL",
    color_continuous_scale=["#B3CCF5", COLOR_PRIMARIO],
    labels={"ETAPA_VIDA": "Etapa del Ciclo de Vida", "TOTAL": "Total de Muertes"},
    title="Histograma – Distribución de Muertes por GRUPO_EDAD1 (Ciclo de Vida) · Colombia 2019",
    template=PLANTILLA,
    text="TOTAL",
)
fig_hist.update_traces(
    texttemplate="%{text:,}",
    textposition="outside",
    textfont_size=10,
)
fig_hist.update_layout(
    plot_bgcolor=COLOR_FONDO,
    paper_bgcolor=COLOR_FONDO,
    font_family="Arial",
    title_font_size=15,
    title_font_color=COLOR_PRIMARIO,
    xaxis_tickangle=-30,
    xaxis_title="Etapa del Ciclo de Vida",
    yaxis_title="Total de Muertes",
    coloraxis_showscale=False,
    uniformtext_minsize=9,
    uniformtext_mode="hide",
)

# ─────────────────────────────────────────────
# 3. LAYOUT DE LA APLICACIÓN
# ─────────────────────────────────────────────

CARD_STYLE = {
    "backgroundColor": "white",
    "borderRadius": "10px",
    "boxShadow": "0 2px 10px rgba(0,0,0,0.08)",
    "padding": "20px",
    "marginBottom": "24px",
}

HEADER_STYLE = {
    "backgroundColor": COLOR_PRIMARIO,
    "padding": "20px 30px",
    "marginBottom": "30px",
    "borderRadius": "0 0 12px 12px",
}

app = dash.Dash(
    __name__,
    title="Mortalidad Colombia 2019",
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
server = app.server  # Necesario para Azure / Gunicorn

app.layout = html.Div(
    style={"backgroundColor": COLOR_FONDO, "minHeight": "100vh", "fontFamily": "Arial"},
    children=[
        # ── Encabezado ───────────────────────────
        html.Div(
            style=HEADER_STYLE,
            children=[
                html.H1(
                    [
                        "Presentado por: Carolina Rodriguez Chacon - universidad de la Salle",
                        html.Br(),
                        "Dashboard de Mortalidad · Colombia 2019",
                    ],
                    style={"color": "white", "margin": 0, "fontSize": "26px"},
                ),
                html.P(
                    "Análisis interactivo de los datos de mortalidad no fetal del DANE.",
                    style={"color": "#C8D8F0", "margin": "6px 0 0 0", "fontSize": "14px"},
                ),
            ],
        ),

        html.Div(
            style={"maxWidth": "1400px", "margin": "0 auto", "padding": "0 24px 40px"},
            children=[

                # ── Mapa ────────────────────────────────
                html.Div(
                    style=CARD_STYLE,
                    children=[
                        html.H3("Mapa – Distribución Total de Muertes por Departamento",
                                style={"color": COLOR_PRIMARIO, "marginTop": 0}),
                        html.P("Visualización de la distribución total de muertes por departamento en Colombia para el año 2019.",
                               style={"color": "#555", "fontSize": "13px"}),
                        dcc.Graph(figure=fig_mapa, config={"displayModeBar": True}),
                    ],
                ),

                # ── Líneas ───────────────────────────────
                html.Div(
                    style=CARD_STYLE,
                    children=[
                        html.H3("Gráfico de Líneas – Total de Muertes por Mes",
                                style={"color": COLOR_PRIMARIO, "marginTop": 0}),
                        html.P("Representación del total de muertes por mes en Colombia, mostrando variaciones a lo largo del año.",
                               style={"color": "#555", "fontSize": "13px"}),
                        dcc.Graph(figure=fig_lineas, config={"displayModeBar": True}),
                    ],
                ),

                # ── Barras violencia + Circular ─────────
                html.Div(
                    style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "24px"},
                    children=[
                        html.Div(
                            style=CARD_STYLE | {"marginBottom": 0},
                            children=[
                                html.H3("Gráfico de Barras – 5 Ciudades más Violentas",
                                        style={"color": COLOR_PRIMARIO, "marginTop": 0}),
                                html.P("Visualización de las 5 ciudades más violentas de Colombia, considerando homicidios con código X95 (agresión con disparo de armas de fuego y casos no especificados).",
                                       style={"color": "#555", "fontSize": "13px"}),
                                dcc.Graph(figure=fig_violencia, config={"displayModeBar": True}),
                            ],
                        ),
                        html.Div(
                            style=CARD_STYLE | {"marginBottom": 0},
                            children=[
                                html.H3("Gráfico Circular – 10 Ciudades con Menor Índice de Mortalidad",
                                        style={"color": COLOR_PRIMARIO, "marginTop": 0}),
                                html.P("Muestra las 10 ciudades con menor índice de mortalidad registrado en Colombia durante 2019.",
                                       style={"color": "#555", "fontSize": "13px"}),
                                dcc.Graph(figure=fig_circular, config={"displayModeBar": True}),
                            ],
                        ),
                    ],
                ),

                html.Div(style={"height": "24px"}),

                # ── Tabla causas ─────────────────────────
                html.Div(
                    style=CARD_STYLE,
                    children=[
                        html.H3("Tabla – 10 Principales Causas de Muerte en Colombia",
                                style={"color": COLOR_PRIMARIO, "marginTop": 0}),
                        html.P("Listado de las 10 principales causas de muerte en Colombia, incluyendo su código CIE-10, nombre y total de casos (ordenadas de mayor a menor).",
                               style={"color": "#555", "fontSize": "13px", "marginBottom": "16px"}),
                        tabla_causas,
                    ],
                ),

                # ── Barras apiladas sexo ──────────────────
                html.Div(
                    style=CARD_STYLE,
                    children=[
                        html.H3("Gráfico de Barras Apiladas – Muertes por Sexo en cada Departamento",
                                style={"color": COLOR_PRIMARIO, "marginTop": 0}),
                        html.P("Comparación del total de muertes por sexo en cada departamento, para analizar diferencias significativas entre géneros.",
                               style={"color": "#555", "fontSize": "13px"}),
                        dcc.Graph(figure=fig_sexo, config={"displayModeBar": True}),
                    ],
                ),

                # ── Histograma edad ──────────────────────
                html.Div(
                    style=CARD_STYLE,
                    children=[
                        html.H3("Histograma – Distribución por GRUPO_EDAD1 (Ciclo de Vida)",
                                style={"color": COLOR_PRIMARIO, "marginTop": 0}),
                        html.P("Distribución de muertes agrupando los valores de la variable GRUPO_EDAD1 según los rangos definidos en la tabla de referencia, para identificar patrones de mortalidad a lo largo del ciclo de vida.",
                               style={"color": "#555", "fontSize": "13px"}),
                        dcc.Graph(figure=fig_hist, config={"displayModeBar": True}),
                    ],
                ),

                # ── Pie de página ────────────────────────
                html.Div(
                    style={"textAlign": "center", "padding": "16px", "color": "#888", "fontSize": "12px"},
                    children=[
                        html.P("Fuente: DANE – Estadísticas Vitales EEVV 2019 · Datos: NoFetal2019 · Elaborado con Python, Plotly y Dash"),
                    ],
                ),
            ],
        ),
    ],
)

# ─────────────────────────────────────────────
# 4. EJECUCIÓN LOCAL
# ─────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
