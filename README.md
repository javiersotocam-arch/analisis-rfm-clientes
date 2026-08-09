# Análisis de Clientes: RFM, Cohortes y LTV

Caso analítico completo sobre el comportamiento de clientes de un negocio, que combina limpieza y exploración de datos (EDA), segmentación RFM, análisis de cohortes y cálculo del valor de vida del cliente (LTV), junto con un script que automatiza todo el pipeline de principio a fin.

## Contenido del repositorio

- `01_EDA.ipynb`: carga, limpieza y análisis exploratorio de los datos de productos y clientes (nulos, duplicados, outliers, tipado de variables).
- `02_RFM.ipynb`: cálculo de Recency, Frequency y Monetary por cliente, asignación de puntuaciones y creación de segmentos personalizados (Campeones, En Riesgo, Grandes Gastadores, etc.).
- `03_Cohortes.ipynb`: análisis de cohortes mensuales, tabla de retención de clientes y tasa de retención media.
- `04_LTV.ipynb`: cálculo del Lifetime Value (LTV) por cohorte y por cliente, comparación con el CAC (Coste de Adquisición de Cliente) y análisis del punto muerto por segmento sociodemográfico.
- `05_Script_final.ipynb`: notebook que integra el pipeline completo (RFM + Cohortes + LTV) y genera los tablones analíticos finales.
- `Automatizacion_CA.py`: script en Python que automatiza todo el proceso anterior de forma programática, desde la carga de datos hasta la exportación de los tablones finales.
- `00_Datasets/`: carpeta con los datasets utilizados y generados por el proyecto.

## Datasets

Dentro de `00_Datasets/`:

- `productos_final.csv`: transacciones de productos (fecha, cliente, categoría, cantidad, precio, etc.).
- `clientes_final.csv`: datos sociodemográficos de clientes (género, nivel educativo, ocupación, tamaño del hogar, CAC).
- `tablon_cliente.csv`: tablón final a nivel de cliente, con RFM, segmento, LTV y variables sociodemográficas.
- `tablon_analitico_clientes.csv`: tablón analítico detallado a nivel de transacción, con todas las variables calculadas.
- `ltv_mes.csv`: evolución de las ventas agregadas por mes de vida del cliente (M1 a M6).

## Metodología

1. **EDA**: limpieza de datos, tratamiento de nulos y outliers, cambio de tipologías.
2. **RFM**: cálculo de Recency, Frequency y Monetary, puntuación 1-5 por variable y segmentación de clientes.
3. **Cohortes**: agrupación de clientes por mes de primera compra (cohorte) y cálculo de la tasa de retención mes a mes.
4. **LTV**: cálculo del valor de vida del cliente a partir de las ventas acumuladas por cohorte, comparado con el coste de adquisición (CAC).
5. **Automatización**: consolidación de todo el proceso en un script único (`Automatizacion_CA.py`) para generar los tablones finales de forma reproducible.

## Segmentos identificados (RFM)

- Campeones
- Clientes Leales
- Clientes Rentables
- Leales Potenciales
- Grandes Gastadores
- Clientes Recientes
- Prometedores
- En Riesgo
- Dudosos

## Tecnologías utilizadas

- Python
- pandas
- matplotlib
- squarify (treemaps)

## Cómo ejecutarlo

1. Clona este repositorio.
2. Instala las dependencias: `pip install pandas matplotlib squarify`.
3. Asegúrate de tener los datasets en la carpeta `00_Datasets/` (ya incluidos en este repositorio).
4. Ejecuta los notebooks en orden (`01_EDA` → `02_RFM` → `03_Cohortes` → `04_LTV` → `05_Script_final`), o directamente `Automatizacion_CA.py` para generar los tablones finales sin pasar por los notebooks.
