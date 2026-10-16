"""
Estimador de producción de petróleo – Campo Volve (Equinor)
Proyecto integrador · Maestría en Inteligencia Artificial Aplicada (UIDE)

Ejecutar:  streamlit run app.py
"""
import json
import os

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Estimador de producción – Volve", page_icon="🛢️", layout="wide")

BASE = os.path.dirname(os.path.abspath(__file__))
RUTA_MODELO = os.path.join(BASE, "models", "modelo_produccion.joblib")
RUTA_RANGOS = os.path.join(BASE, "models", "rangos_variables.json")
RUTA_DATOS = os.path.join(BASE, "data", "Volve_production_data.xlsx")

BBL_POR_SM3 = 6.28981  # 1 Sm3 = 6,28981 bbl (el dataset original está en unidades SI)

ETIQUETAS = {
    "ON_STREAM_HRS": ("Horas en línea", "h", 0.25),
    "AVG_CHOKE_SIZE_P": ("Apertura del choke", "%", 0.5),
    "AVG_WHP_P": ("Presión en cabeza (WHP)", "psi", 5.0),
    "AVG_WHT_P": ("Temperatura en cabeza (WHT)", "°F", 1.0),
    "DP_CHOKE_SIZE": ("Diferencial de presión en el choke", "psi", 5.0),
}


@st.cache_resource
def cargar_modelo():
    return joblib.load(RUTA_MODELO)


@st.cache_data
def cargar_rangos():
    with open(RUTA_RANGOS, encoding="utf-8") as f:
        return json.load(f)


@st.cache_data
def cargar_datos():
    df = pd.read_excel(RUTA_DATOS, sheet_name="Daily Production Data")
    df = df[(df["WELL_TYPE"] == "OP") & (df["ON_STREAM_HRS"] > 0) & (df["BORE_OIL_VOL"] > 0)].copy()
    df["BORE_WAT_VOL"] = df["BORE_WAT_VOL"].clip(lower=0)
    df["BORE_OIL_VOL"] = df["BORE_OIL_VOL"] * BBL_POR_SM3   # BPPD
    df["BORE_WAT_VOL"] = df["BORE_WAT_VOL"] * BBL_POR_SM3   # BAPD
    df["LIQUIDO"] = df["BORE_OIL_VOL"] + df["BORE_WAT_VOL"]
    df["CORTE_AGUA"] = df["BORE_WAT_VOL"] / df["LIQUIDO"]
    return df.rename(columns={"NPD_WELL_BORE_NAME": "POZO"})


st.title("🛢️ Estimador de producción de petróleo – Campo Volve")
st.caption(
    "Proyecto integrador · Maestría en IA Aplicada (UIDE). Unidades de campo (bbl, psi, °F). Datos: Equinor, campo Volve "
    "(Equinor Open Data Licence). Herramienta educativa, no apta para decisiones operativas."
)

try:
    paquete = cargar_modelo()
    rangos = cargar_rangos()
except FileNotFoundError:
    st.error("No se encontró el modelo en la carpeta models/. Ejecuta primero el notebook para generarlo.")
    st.stop()

modelo = paquete["modelo_liquido"]
variables = paquete["variables"]
umbral = paquete["umbral_desviacion"]

tab1, tab2, tab3 = st.tabs(["Estimación puntual", "Explorar datos de Volve", "Acerca del modelo"])

# ------------------------------------------------------------------ Pestaña 1
with tab1:
    st.subheader("Estimar la tasa de producción")
    st.write(
        "Ingresa las condiciones operativas del día. El modelo estima la **tasa de líquido** y, con el "
        "**corte de agua de referencia**, se calcula la tasa de petróleo. Los controles están limitados al "
        "rango de valores vistos en el entrenamiento."
    )
    col_in, col_out = st.columns([1, 1])
    valores = {}
    with col_in:
        for v in variables:
            nombre, unidad, paso = ETIQUETAS[v]
            vmin, vmax, vmed = rangos["min"][v], rangos["max"][v], rangos["50%"][v]
            valores[v] = st.slider(f"{nombre} ({unidad})", float(vmin), float(vmax), float(vmed), float(paso))
        wc_ref = st.slider(
            "Corte de agua de referencia (%)",
            0.0, round(rangos["max"]["CORTE_AGUA_REF"] * 100, 1),
            round(rangos["50%"]["CORTE_AGUA_REF"] * 100, 1), 0.5,
            help="En campo proviene de pruebas de pozo o asignación de producción (p. ej., mediana de los últimos 14 días).",
        ) / 100
        real = st.number_input(
            "Petróleo real medido (BPPD) — opcional, 0 = no comparar", min_value=0.0, value=0.0, step=100.0
        )

    X = pd.DataFrame([valores])[variables]
    liquido = float(max(0.0, modelo.predict(X)[0]))
    petroleo = liquido * (1 - wc_ref)
    agua = liquido - petroleo

    with col_out:
        c1, c2, c3 = st.columns(3)
        c1.metric("Líquido estimado", f"{liquido:,.0f} BFPD")
        c2.metric("Petróleo estimado", f"{petroleo:,.0f} BPPD")
        c3.metric("Agua estimada", f"{agua:,.0f} BAPD")

        fig, ax = plt.subplots(figsize=(5, 2.6))
        ax.barh(["Líquido"], [petroleo], color="#2e7d32", label="Petróleo")
        ax.barh(["Líquido"], [agua], left=[petroleo], color="#1976d2", label="Agua")
        ax.set_xlabel("bbl/día"); ax.legend(loc="lower right")
        st.pyplot(fig)

        if real > 0:
            resid = real - petroleo
            st.write(f"**Residuo (real − estimado):** {resid:,.0f} BPPD  (umbral de desviación: ±{umbral:,.0f} BPPD)")
            if abs(resid) > umbral:
                signo = "mayor" if resid > 0 else "menor"
                st.warning(
                    f"Desviación: la producción real es {signo} que la esperada para estas condiciones. "
                    "Es solo una alerta para que un ingeniero revise el pozo (medición, choke, corte de agua, "
                    "restricciones). No es un diagnóstico de la causa."
                )
            else:
                st.success("La producción real está dentro de lo esperado para estas condiciones.")

# ------------------------------------------------------------------ Pestaña 2
with tab2:
    st.subheader("Historial de producción")
    try:
        datos = cargar_datos()
    except FileNotFoundError:
        st.info("Coloca el archivo Volve_production_data.xlsx en la carpeta data/ para ver esta sección.")
    else:
        pozos = sorted(datos["POZO"].unique())
        pozo = st.selectbox("Pozo", pozos, index=pozos.index("15/9-F-12") if "15/9-F-12" in pozos else 0)
        d = datos[datos["POZO"] == pozo].sort_values("DATEPRD")
        f_ini, f_fin = st.slider(
            "Rango de fechas",
            d["DATEPRD"].min().date(), d["DATEPRD"].max().date(),
            (d["DATEPRD"].min().date(), d["DATEPRD"].max().date()),
        )
        d = d[(d["DATEPRD"].dt.date >= f_ini) & (d["DATEPRD"].dt.date <= f_fin)]
        fig, axes = plt.subplots(2, 1, figsize=(10, 5.5), sharex=True)
        axes[0].plot(d["DATEPRD"], d["BORE_OIL_VOL"], label="Petróleo (BPPD)", color="#2e7d32", lw=1)
        axes[0].plot(d["DATEPRD"], d["LIQUIDO"], label="Líquido total (BFPD)", color="#1976d2", lw=1)
        axes[0].set_ylabel("bbl/día (BPPD / BFPD)"); axes[0].legend()
        axes[1].plot(d["DATEPRD"], d["CORTE_AGUA"] * 100, color="#6d4c41", lw=1)
        axes[1].set_ylabel("Corte de agua (%)")
        plt.tight_layout()
        st.pyplot(fig)
        st.caption(f"{len(d)} días de producción activa del pozo {pozo} en el rango seleccionado.")

# ------------------------------------------------------------------ Pestaña 3
with tab3:
    st.subheader("Cómo funciona")
    st.markdown(
        """
**Enfoque en dos etapas**
1. Un modelo de *machine learning* (Random Forest) estima la **tasa de líquido total** a partir de horas en línea,
   apertura del choke, presión y temperatura en cabeza y diferencial de presión en el choke.
2. El petróleo se calcula como `líquido × (1 − corte de agua de referencia)`.

**Desempeño en el período de prueba (jul-2015 a sep-2016)**: R² ≈ 0,77, RMSE ≈ 1.020 BPPD, MAE ≈ 760 BPPD
(la tasa media de petróleo en ese período fue ≈ 2.440 BPPD).

**Limitaciones**
- Datos de un solo campo (Volve) y de pocos pozos; no se debe aplicar a otros campos sin revalidar.
- El modelo tiende a sobreestimar el petróleo (≈ 395 BPPD en promedio) y su desempeño varía mucho entre pozos;
  en F-5, sin historia en el entrenamiento, el error fue alto.
- Depende de un corte de agua de referencia conocido; si cambia bruscamente, la estimación se sesga.
- Es una estimación a partir de condiciones operativas, no un pronóstico de declinación ni un diagnóstico de causas.
- Herramienta educativa: no debe usarse para decisiones operativas, económicas o de seguridad.
        """
    )
