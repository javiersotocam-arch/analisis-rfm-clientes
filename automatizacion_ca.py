"""Automatización del caso de Customer Analytics: de los CSV de origen a los tablones para Tableau.

Reproduce, sin la parte exploratoria, la lógica corregida del notebook `customer_analytics_corregido.ipynb`:
limpieza, RFM, cohortes de 6 meses, LTV (ventas y margen) y tablones finales.

Uso:
    python automatizacion_ca.py                 # lee y escribe en 00_Datasets/
    python automatizacion_ca.py ruta/a/datos    # otra carpeta
"""
import sys
from pathlib import Path

import pandas as pd

RUTA = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('00_Datasets')
COHORTE_MAX = '2023-07'   # última cohorte con 6 meses completos de datos
MESES_VIDA = 6
OPCIONES_CSV = dict(sep=';', decimal=',', index=False, encoding='utf-8-sig')


def cargar_y_limpiar(ruta):
    productos = pd.read_csv(ruta / 'productos_1224.csv', parse_dates=['Fecha'])
    clientes = pd.read_csv(ruta / 'clientes_1224.csv', parse_dates=['Fecha_Nacimiento'])

    productos['Total_Venta'] = productos['Cantidad'] * productos['Precio_Unitario']
    productos['Margen'] = (productos['Precio_Unitario'] - productos['Coste_Unitario']) * productos['Cantidad']

    clientes['Tamano_Hogar'] = clientes['Tamano_Hogar'].fillna(clientes['Tamano_Hogar'].mode()[0])
    clientes['Ocupacion'] = clientes['Ocupacion'].fillna('Desconocido')
    clientes['Nivel_Educativo'] = clientes['Nivel_Educativo'].fillna('Desconocido')
    return productos, clientes


def segmentar_clientes(fila):
    r, f, m = int(fila['r']), int(fila['f']), int(fila['m'])
    alto_r, alto_f, alto_m = r >= 4, f >= 4, m >= 4
    medio_r, medio_f, medio_m = r == 3, f == 3, m == 3
    bajo_r, bajo_f, bajo_m = r <= 2, f <= 2, m <= 2

    if alto_r and alto_f and alto_m:
        return 'Campeones'
    if alto_r and alto_f and medio_m:
        return 'Clientes Leales'
    if medio_r and alto_f and alto_m:
        return 'Clientes Rentables'
    if bajo_r and medio_f and medio_m:
        return 'Leales Potenciales'
    if bajo_r and bajo_f and alto_m:
        return 'Grandes Gastadores'
    if alto_r and bajo_f and bajo_m:
        return 'Clientes Recientes'
    if medio_r and medio_f and medio_m:
        return 'Prometedores'
    if bajo_r and bajo_f and bajo_m:
        return 'En Riesgo'
    return 'Dudosos'


def calcular_rfm(productos):
    fecha_max = productos['Fecha'].max()
    rfm = productos.groupby('ID_Cliente').agg(
        Recency=('Fecha', lambda x: (fecha_max - x.max()).days),
        Frequency=('ID_Transaccion', 'nunique'),
        Monetary=('Total_Venta', 'sum'),
    )
    rfm['r'] = pd.cut(rfm['Recency'], bins=[0, 60, 120, 180, 240, rfm['Recency'].max()], labels=[5, 4, 3, 2, 1], include_lowest=True)
    rfm['f'] = pd.cut(rfm['Frequency'], bins=[1, 2, 4, 6, 9, rfm['Frequency'].max()], labels=[1, 2, 3, 4, 5], include_lowest=True)
    rfm['m'] = pd.cut(rfm['Monetary'], bins=[0, 30, 70, 150, 300, rfm['Monetary'].max()], labels=[1, 2, 3, 4, 5], include_lowest=True)
    rfm['RFM'] = rfm['r'].astype(str) + rfm['f'].astype(str) + rfm['m'].astype(str)
    rfm['Segmento'] = rfm.apply(segmentar_clientes, axis=1)
    return rfm


def ventana_cohortes(productos, clientes):
    datos = productos.copy()
    datos['MesTransaccion'] = datos['Fecha'].dt.to_period('M')
    datos['MesCohorte'] = datos.groupby('ID_Cliente')['MesTransaccion'].transform('min')
    datos = datos[datos['MesCohorte'] <= COHORTE_MAX].copy()

    meses = (datos['MesTransaccion'] - datos['MesCohorte']).apply(lambda x: x.n)
    datos = datos[meses < MESES_VIDA].copy()
    datos['MesCliente'] = 'M' + (meses[meses < MESES_VIDA] + 1).astype(str)
    datos['MesTransaccion'] = datos['MesTransaccion'].dt.to_timestamp()
    datos['MesCohorte'] = datos['MesCohorte'].dt.to_timestamp()
    return datos.merge(clientes[['ID_Cliente', 'CAC']], on='ID_Cliente', how='left')


def construir_tablones(productos, clientes):
    rfm = calcular_rfm(productos)
    resultados = ventana_cohortes(productos, clientes)
    ltv_cliente = resultados.groupby('ID_Cliente').agg(ltv=('Total_Venta', 'sum'), ltv_margen=('Margen', 'sum'))
    sociodemo = clientes[['ID_Cliente', 'Genero', 'Nivel_Educativo', 'Ocupacion', 'Tamano_Hogar']]

    tablon_analitico = (resultados
                        .merge(rfm, on='ID_Cliente', how='left')
                        .merge(sociodemo, on='ID_Cliente', how='left')
                        .merge(ltv_cliente, on='ID_Cliente', how='left'))
    assert len(tablon_analitico) == len(resultados), 'Un merge ha duplicado filas'

    columnas_cliente = ['MesCohorte', 'CAC', 'Recency', 'Frequency', 'Monetary', 'r', 'f', 'm', 'Segmento',
                        'Genero', 'Nivel_Educativo', 'Ocupacion', 'Tamano_Hogar', 'ltv', 'ltv_margen']
    tablon_cliente = tablon_analitico.groupby('ID_Cliente')[columnas_cliente].first().reset_index()

    ltv_mes = (tablon_analitico.groupby('MesCliente')
               .agg(Total_Venta=('Total_Venta', 'sum'), Margen=('Margen', 'sum'), ID_Cliente=('ID_Cliente', 'nunique')))
    ltv_mes['M1'] = ltv_mes.loc['M1', 'ID_Cliente']
    ltv_mes['Ventas_por_M1'] = ltv_mes['Total_Venta'] / ltv_mes['M1']
    ltv_mes['Margen_por_M1'] = ltv_mes['Margen'] / ltv_mes['M1']
    return tablon_analitico, tablon_cliente, ltv_mes.reset_index()


def main():
    productos, clientes = cargar_y_limpiar(RUTA)
    tablon_analitico, tablon_cliente, ltv_mes = construir_tablones(productos, clientes)

    tablon_analitico.to_csv(RUTA / 'tablon_analitico_clientes.csv', **OPCIONES_CSV)
    tablon_cliente.to_csv(RUTA / 'tablon_cliente.csv', **OPCIONES_CSV)
    ltv_mes.to_csv(RUTA / 'ltv_mes.csv', **OPCIONES_CSV)

    print(f'tablon_analitico_clientes.csv: {len(tablon_analitico):,} filas')
    print(f'tablon_cliente.csv:            {len(tablon_cliente):,} clientes')
    print(f"LTV a 6 meses: {ltv_mes['Ventas_por_M1'].sum():.2f} de ventas, {ltv_mes['Margen_por_M1'].sum():.2f} de margen")


if __name__ == '__main__':
    main()
