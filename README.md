# Estimación de la tasa de producción de petróleo a partir de parámetros operativos — Campo Volve

**Proyecto integrador · Cursos preparatorios · Maestría en Inteligencia Artificial Aplicada (UIDE)
Autor:** *Alan Israel López Males*  
**Fecha:** 15 de octubre de 2026


## Descripción

En ingeniería de producción es clave conocer la tasa de petróleo de cada pozo, pero medirla de forma continua es costoso y los sensores pueden fallar. Este proyecto estima la **tasa diaria de petróleo (BPPD, barriles por día)** de los pozos productores del campo **Volve** (Mar del Norte) a partir de variables operativas (presión en cabeza en psi, temperatura en °F, apertura y diferencial de presión del choke, horas en línea).

> \*\*Unidades:\*\* el dataset original está en unidades SI (Sm³, bar, °C). Todo el análisis, los resultados y la app usan \*\*unidades de campo\*\*: BPPD/BFPD/BAPD (1 Sm³ = 6,28981 bbl), psi (1 bar = 14,5038 psi) y °F.

Un primer intento de predecir el petróleo directamente fracasó, porque el corte de agua de Volve crece con el tiempo (hasta cerca de 95 % en algunos pozos). Por eso se usa un **enfoque en dos etapas**:

1. Un modelo de *machine learning* (Random Forest) estima la **tasa de líquido total** (petróleo + agua).
2. El petróleo se obtiene como `líquido × (1 − corte de agua de referencia)`, usando la mediana de los 14 registros previos del pozo.

Se evalúa con una **partición temporal** (entrenamiento: feb-2008 a jun-2015; prueba: jul-2015 a sep-2016). Se incluye además un detector de desviaciones con reglas de ingeniería que sugieren hipótesis (no diagnósticos) y una interfaz en Streamlit.

## Resultados principales (período de prueba)

|Enfoque|Modelo|Variables|R² petróleo|RMSE (BPPD)|
|-|-|-|-|-|
|Petróleo directo|Random Forest|Superficie|−0,06|2.181|
|Dos etapas|**Random Forest (modelo final)**|**Superficie**|**0,77**|**1.021**|
|Dos etapas|Red neuronal (MLP, semilla 42)|Superficie|0,83|865|
|Dos etapas|Regresión lineal|Superficie|−0,25|2.364|

La red neuronal obtuvo el menor error con la semilla 42, pero su desempeño varía mucho con la semilla (R² entre 0,45 y 0,89 en cinco repeticiones), por lo que se eligió el Random Forest como modelo final por su estabilidad. Con un estimador de líquido perfecto, el método alcanzaría R² = 0,98. El desempeño varía entre pozos y el modelo tiende a sobreestimar el petróleo; los detalles y limitaciones están en el informe y en el notebook.

## Estructura del repositorio

```
├── proyecto\_integrador\_volve.ipynb   # Notebook principal (limpieza, EDA, modelos, evaluación, ética)
├── app.py                            # Interfaz en Streamlit
├── requirements.txt                  # Dependencias
├── data/
│   ├── Volve\_production\_data.xlsx    # Dataset (Equinor, campo Volve)
│   └── README\_datos.md               # Fuente y licencia de los datos
├── models/
│   ├── modelo\_produccion.joblib      # Modelo de líquido entrenado
│   └── rangos\_variables.json         # Rangos de las variables (usados por la app)
├── figures/                          # Gráficos del análisis
└── docs/
    └── Informe\_tecnico\_Volve.docx    # Informe técnico final
```

## Cómo ejecutarlo

**Opción 1 — Google Colab:** sube el notebook y el archivo `data/Volve\_production\_data.xlsx` (el notebook ofrece subir el archivo si no lo encuentra) y ejecuta todas las celdas.

**Opción 2 — Local:**

```bash
git clone <URL-del-repositorio>
cd <carpeta-del-repositorio>
python -m venv .venv \&\& source .venv/bin/activate      # en Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
jupyter notebook proyecto\_integrador\_volve.ipynb       # ejecutar todas las celdas
streamlit run app.py                                   # interfaz gráfica
```

> El modelo guardado se entrenó con scikit-learn 1.8.0. Si usas otra versión y aparece una advertencia al cargarlo, vuelve a ejecutar el notebook para regenerarlo.

## Limitaciones

* Datos de un solo campo y pocos pozos: el modelo no debe aplicarse a otros campos sin revalidar.
* La estimación de petróleo depende de un corte de agua de referencia conocido.
* El detector de desviaciones usa umbrales calibrados con los datos de prueba y reglas fijadas por criterio; sus hipótesis son orientativas.
* Herramienta educativa: no debe usarse para decisiones operativas, económicas o de seguridad.

## Atribución y licencia de los datos

Datos del campo **Volve**, publicados por **Equinor** y los antiguos socios de la licencia (ExxonMobil y Bayerngas) bajo la **Equinor Open Data Licence**: no pueden revenderse y deben atribuirse a sus propietarios. Equinor no ofrece garantías sobre su contenido. Más información: https://www.equinor.com/energy/volve-data-sharing

Declaración de uso de herramientas: *(indica aquí, con tus palabras, si usaste herramientas de IA como apoyo y para qué)*.

