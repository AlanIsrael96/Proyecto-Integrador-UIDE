# Guion del video de presentación (5 a 7 minutos)

**Requisitos de la guía:** aparecer en cámara, explicar el problema, el dataset, el código, los resultados y las conclusiones. Duración objetivo: **6:30**.
**Consejo:** el guion es una base; léelo en voz alta una vez y luego dilo con tus palabras. Usa el notebook ya ejecutado en pantalla para no esperar tiempos de cómputo.

| Tiempo | Sección | Qué mostrar en pantalla |
|---|---|---|
| 0:00 – 0:30 | Presentación | Cámara completa |
| 0:30 – 1:15 | Problema | Diapositiva o notebook (sección 1) |
| 1:15 – 2:00 | Dataset | Notebook: carga de datos y tabla por pozo |
| 2:00 – 3:30 | Código y metodología | Notebook: limpieza, EDA, partición temporal |
| 3:30 – 5:00 | Resultados | Notebook: intento 1, dos etapas, gráficos |
| 5:00 – 5:45 | Interfaz (Streamlit) | App en ejecución |
| 5:45 – 6:30 | Conclusiones, ética y cierre | Cámara o diapositiva final |

---

## 0:00 – 0:30 · Presentación
> Hola, soy **[tu nombre]**, ingeniero en petróleos, y este es mi proyecto integrador de los cursos preparatorios de la Maestría en Inteligencia Artificial Aplicada de la UIDE. Voy a explicar el problema que abordé, los datos, el código, los resultados y las conclusiones.

## 0:30 – 1:15 · El problema
> En producción de petróleo es fundamental conocer la tasa de cada pozo, pero medirla de forma continua es costoso y los sensores pueden fallar. Una alternativa es **estimarla a partir de variables operativas**, como presiones, temperatura y apertura del choke. Mi pregunta fue: *¿puedo estimar la tasa diaria de petróleo de los pozos del campo Volve con estas variables, y qué tan bien funciona con fechas posteriores a las de entrenamiento?*

## 1:15 – 2:00 · El dataset
> Usé los datos abiertos del campo Volve, en el Mar del Norte, publicados por Equinor. La hoja diaria tiene más de 15.000 registros entre 2007 y 2016. Me quedé con los **pozos productores** y con los días en que el pozo estuvo produciendo, lo que dejó unos **8.000 registros de seis pozos**. La variable a estimar es el petróleo diario. El archivo viene en unidades del Sistema Internacional, pero **convertí todo a unidades de campo**: barriles por día, psi y grados Fahrenheit. Los datos tienen licencia abierta de Equinor y los atribuyo en el repositorio y el informe.

*(Muestra la tabla resumen por pozo y la consulta SQL del notebook.)*

## 2:00 – 3:30 · Código y metodología
> **Limpieza:** excluí los pozos inyectores y los días sin producción. En la presión y temperatura de fondo había más de 1.900 ceros que corresponden a un sensor sin lectura, así que los traté como datos faltantes.
>
> **Análisis exploratorio:** la presión en cabeza y el diferencial de presión en el choke son las variables más correlacionadas con el petróleo. Y hay un hallazgo clave: el **corte de agua crece con el tiempo**, de casi cero en 2008 a más de la mitad en años posteriores. Por eso el petróleo cae aunque el pozo siga produciendo líquido.
>
> **Partición:** como son datos en el tiempo, no usé una partición aleatoria. Entrené con datos hasta junio de 2015 y evalué con los posteriores, evitando además usar como entrada variables que son resultado de la producción, como el agua o el gas del mismo día.

*(Muestra el gráfico del corte de agua y la celda de partición temporal.)*

## 3:30 – 5:00 · Resultados
> Mi **primer intento**, predecir el petróleo directamente, **falló**: el Random Forest tuvo un R² de aproximadamente cero y la red neuronal fue incluso peor. La razón es que las presiones y el choke explican cuánto *líquido* produce el pozo, pero no qué fracción es petróleo.
>
> Entonces planteé un **enfoque en dos etapas**: un Random Forest estima el líquido total, y el petróleo se calcula multiplicando por uno menos el corte de agua de referencia del pozo, tomado de sus 14 registros previos. Con esto el Random Forest alcanzó un R² de **0,77** en el período de prueba, con un error medio absoluto de unos **760 barriles de petróleo por día**, sobre una tasa media de unos 2.440 barriles por día.
>
> También comparé una regresión lineal, que no funcionó, y una red neuronal, que con una semilla llegó a R² de 0,83 pero varió entre 0,45 y 0,89 al repetirla con otras semillas. Por eso elegí el Random Forest como modelo final, por su estabilidad. Las variables de fondo no mejoraron el resultado.
>
> Hay limitaciones que quiero mencionar con honestidad: el modelo **sobreestima en promedio** y su desempeño **varía entre pozos**; en el pozo F-5, que no estaba en el entrenamiento, el error fue alto.
>
> Como extensión, hice un **detector de desviaciones** que marca los días en que la producción real se aleja de la esperada y sugiere hipótesis con reglas de ingeniería. Son solo orientativas: el dataset no tiene eventos etiquetados como emulsión o fugas, así que el sistema no puede confirmar causas.

*(Muestra la tabla de resultados, el gráfico real vs predicho y el de importancia de variables.)*

## 5:00 – 5:45 · La interfaz
> Además desarrollé una aplicación en **Streamlit**. Aquí ajusto las variables operativas y el corte de agua, y obtengo el líquido, el petróleo y el agua estimados. Si ingreso un valor real medido, la app me avisa si la desviación supera el umbral. También tiene un explorador del historial por pozo.

*(Mueve dos o tres controles en vivo y muestra la pestaña de historial.)*

## 5:45 – 6:30 · Conclusiones, ética y cierre
> Como conclusiones: predecir el petróleo directamente no generalizó, porque el corte de agua cambia con el tiempo; un enfoque en dos etapas con Random Forest sí logró un resultado razonable, aunque desigual entre pozos.
>
> En cuanto a ética: es una herramienta **educativa**, basada en un solo campo; no sustituye la medición real ni el criterio del ingeniero, y las hipótesis del detector no son diagnósticos. Documenté los supuestos, incluido el del corte de agua, y los resultados negativos.
>
> Como trabajo futuro, me gustaría compararlo con curvas de declinación y usar datos con eventos etiquetados. Todo el código, los datos y el informe están en mi repositorio de GitHub. Muchas gracias.

---

## Lista de verificación antes de grabar
- [ ] Apareces en cámara durante el video (al inicio y al final, como mínimo).
- [ ] El notebook está ya ejecutado y con los gráficos visibles.
- [ ] La app de Streamlit abre sin errores (`streamlit run app.py`).
- [ ] Duración entre 5 y 7 minutos.
- [ ] Mencionas con tus palabras qué hace cada parte del código; puedes entender y explicar todo lo que muestras.
- [ ] Subes el video (YouTube como "no listado", Drive o similar) y pones el enlace en el README.
