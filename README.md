# Análisis de Clientes: RFM, Cohortes y LTV

Caso analítico completo sobre el comportamiento de clientes de un negocio, que combina limpieza y exploración de datos (EDA), segmentación RFM, análisis de cohortes y cálculo del valor de vida del cliente (LTV) frente al coste de adquisición (CAC), junto con un script que automatiza todo el pipeline y genera los tablones para el dashboard de Tableau.

## Resultados

- **Datos**: 20.688 clientes y 78.266 líneas de compra de 2023.
- **Repetición**: el 56 % de los clientes compra una sola vez; la retención cae al 21 % en el segundo mes y al 9,9 % en el sexto (media ponderada por cohorte).
- **Segmentos RFM**: "En Riesgo" (5.951 clientes) y "Dudosos" (5.791) son los mayores entre los clientes de las cohortes de enero a julio; "Dudosos" es un grupo heterogéneo que incluye compradores recientes con gasto medio, candidatos a una segunda compra.
- **LTV a 6 meses**: 102,76 € de ventas por cliente, pero solo **30,93 € de margen** frente a un **CAC medio de 69,44 €**. Con ventas, el cliente parece rentable desde el segundo mes; con margen, no recupera lo que costó captarlo en sus primeros 6 meses (ratio LTV/CAC de 0,45).
- **Perfil sociodemográfico**: predecir el LTV con la media del perfil (nivel educativo, ocupación y tamaño del hogar) apenas mejora el error frente a usar la media general (un 1 %), así que el comportamiento de compra predice mejor que el perfil.

## Metodología

1. **EDA**: limpieza de datos, tratamiento de nulos (moda para el tamaño del hogar, categoría "Desconocido" para ocupación y nivel educativo), revisión de outliers y de incoherencias.
2. **RFM**: cálculo de Recency, Frequency y Monetary, puntuación de 1 a 5 por variable y segmentación de clientes.
3. **Cohortes**: agrupación de clientes por mes de primera compra y tasa de retención mes a mes en una ventana de 6 meses.
4. **LTV**: valor de vida del cliente a partir de las ventas y del margen acumulados por cohorte, comparado con el CAC, y punto muerto por segmento sociodemográfico.
5. **Automatización**: todo el proceso en un script único (`automatizacion_ca.py`) que genera los tablones finales de forma reproducible.

## Segmentos identificados (RFM)

Campeones · Clientes Leales · Clientes Rentables · Leales Potenciales · Grandes Gastadores · Clientes Recientes · Prometedores · En Riesgo · Dudosos

## Revisión y correcciones (octubre 2026)

La primera versión del proyecto se revisó a fondo. Las correcciones más importantes:

- **Datos limpios que no lo estaban**: los archivos `_final` se guardaron justo después de cargar los datos, antes de limpiarlos, así que eran copias exactas de los originales (con nulos y sin `Total_Venta`).
- **LTV con margen**: el LTV se comparaba con el CAC usando ventas en lugar de margen, lo que hacía parecer rentable a un cliente que en 6 meses no recupera su coste de captación.
- **LTV ponderado**: la media de las cohortes no tenía en cuenta su tamaño; el LTV correcto es 102,76 € (no 101,41 €).
- **Evaluación del LTV predictivo**: el "error predicho" no comparaba la predicción con la realidad y se calculaba con datos que incluían a la cohorte evaluada. Bien medido, la mejora es del 1 %, no del 75 %.
- **Segmentos contados por clientes**: los recuentos se hacían sobre filas de compra, por lo que los segmentos que más compran salían inflados.
- **Tablones para Tableau**: `tablon_cliente.csv` perdía la columna `ID_Cliente` al exportarse, y los CSV usaban la coma como separador y como decimal a la vez; ahora se exportan con `;` y decimal `,`.
- **Script de automatización**: el script anterior repetía los mismos fallos del script final (perdía `ID_Cliente` y exportaba con separador ambiguo) y usaba una ruta de un ordenador concreto; el nuevo genera exactamente los mismos tablones que el notebook.

El detalle de todas las correcciones está al principio del notebook.

## Contenido del repositorio

- `customer_analytics_corregido.ipynb`: todo el análisis (EDA, RFM, cohortes, LTV y tablones), explicado paso a paso
- `customer_analytics_corregido.pdf`: el mismo notebook en PDF
- `automatizacion_ca.py`: script que genera los tablones finales sin pasar por el notebook

## Datos

Los datos proceden del caso práctico del máster de Data Science for Business (DS4B) y **no se incluyen en el repositorio**. El proyecto usa dos archivos, que deben colocarse en una carpeta `00_Datasets/`:

- `productos_1224.csv`: líneas de compra (cliente, fecha, transacción, producto, coste, cantidad y precio).
- `clientes_1224.csv`: datos sociodemográficos de cada cliente y su coste de adquisición (CAC).

A partir de ellos, el notebook y el script generan en la misma carpeta:

- `tablon_analitico_clientes.csv`: una fila por línea de compra, con RFM, segmento, cohorte, LTV y variables sociodemográficas.
- `tablon_cliente.csv`: una fila por cliente.
- `ltv_mes.csv`: ventas y margen por mes de vida del cliente (M1 a M6).

## Tecnologías utilizadas

- **Python** (pandas, numpy, matplotlib, squarify)
- **Tableau** para el dashboard

## Cómo ejecutarlo

1. Instala las dependencias: `pip install pandas numpy matplotlib squarify`.
2. Coloca `productos_1224.csv` y `clientes_1224.csv` en la carpeta `00_Datasets/`.
3. Ejecuta el notebook de arriba abajo, o directamente `python automatizacion_ca.py` para generar los tablones.

## Autor

Javier Sotoca — portfolio completo: https://sites.google.com/view/javiersotoca/home
