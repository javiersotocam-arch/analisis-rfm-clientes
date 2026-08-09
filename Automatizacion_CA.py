# Importación de liberias
import pandas as pd

# Carga de datos
productos =pd.read_csv('Desktop/Caso_Final2_CA/00_Datasets/productos_1224.csv')
clientes =pd.read_csv('Desktop/Caso_Final2_CA/00_Datasets/clientes_1224.csv')

# Transformación de la variable "Fecha" del set de productos
productos['Fecha'] = pd.to_datetime(productos['Fecha'])

# Total Ventas (cantidad + productos) del set de productos
productos['Total_Venta'] = (productos['Cantidad'] * productos['Precio_Unitario'])

# Imputar Tamano_hogar con la moda, dataset de clientes
moda_tamano_hogar = clientes.Tamano_Hogar.mode()[0]
clientes['Tamano_Hogar'] = clientes['Tamano_Hogar'].fillna(moda_tamano_hogar)

# Imputar Nivel_Educativo y Ocupacion por una categoría 'Desconocido', del set de clientes
clientes['Ocupacion'] = clientes['Ocupacion'].fillna('Desconocido')
clientes['Nivel_Educativo'] = clientes['Nivel_Educativo'].fillna('Desconocido')   

# Cambio a tipo fecha, del set de clientes
clientes['Fecha_Nacimiento'] =pd.to_datetime(clientes['Fecha_Nacimiento'])


# Obtenemos última fecha de transacción
fecha_max = productos['Fecha'].max()

# Calcular la recencia en dias para cada cliente
rfm = productos.groupby('ID_Cliente').agg(Recency=('Fecha', lambda x: (fecha_max - x.max()).days))

# Cálculo Frequency
rfm['Frequency']= productos.groupby('ID_Cliente')['ID_Transaccion'].nunique()

# Cálculo Monetary
rfm['Monetary'] = productos.groupby('ID_Cliente')['Total_Venta'].sum()

# Puntuaciones RFM
rfm['r'] = pd.cut(rfm['Recency'],bins = [0,60,120,180,240, rfm['Recency'].max()], labels = [5,4,3,2,1], include_lowest = True)
rfm['f'] = pd.cut(rfm['Frequency'],bins = [1,2,4,6,9, rfm['Frequency'].max()], labels = [1,2,3,4,5], include_lowest = True)
rfm ['m'] = pd.cut(rfm['Monetary'],bins = [0,30,70,150,300, rfm['Monetary'].max()], labels = [1,2,3,4,5], include_lowest = True)

rfm['RFM']= rfm['r'].astype(str) + rfm['f'].astype(str)+ rfm['m'].astype(str)

# Segmentos personalizados
def segmentar_clientes(fila):
    r, f, m = str(fila['r']), str(fila['f']), str(fila['m'])
    
    # Definir condiciones previamente para simplificar el código
    es_alto_r = r in ['4', '5']
    es_alto_f = f in ['4', '5']
    es_alto_m = m in ['4', '5']
    
    es_medio_r = r in ['3']
    es_medio_f = f in ['3']
    es_medio_m = m in ['3']
    
    es_bajo_r = r in ['1', '2']
    es_bajo_f = f in ['1', '2']
    es_bajo_m = m in ['1', '2']
    
    # Aplicar la lógica de los segmentos
    if es_alto_r and es_alto_f and es_alto_m:
        return 'Campeones'
    elif es_alto_r and es_alto_f and (es_alto_m or es_medio_m):
        return 'Clientes Leales'
    elif es_medio_r and es_alto_f and es_alto_m:
        return 'Clientes Rentables'
    elif es_bajo_r and es_medio_f and es_medio_m:
        return 'Leales Potenciales'
    elif es_bajo_r and es_bajo_f and es_alto_m:
        return 'Grandes Gastadores'
    elif es_alto_r and es_bajo_f and es_bajo_m:
        return 'Clientes Recientes'
    elif es_medio_r and es_medio_f and es_medio_m:
        return 'Prometedores'
    elif es_bajo_r and es_bajo_f and es_bajo_m:
        return 'En Riesgo'
    else:
        return 'Dudosos'
# Aplicar la función
rfm['Segmento'] = rfm.apply(segmentar_clientes, axis=1)


# Crear columna mes transacción
productos['MesTransaccion'] = productos['Fecha'].dt.to_period('M')

# Calcular el mes de cohorte
productos['MesCohorte'] = productos.groupby('ID_Cliente')['MesTransaccion'].transform('min')

# Eliminar registros de cohortes no completos
resultados = productos[productos['MesCohorte'] <= '2023-07']

# Transformar las variables Mes a datetime
resultados = resultados.copy()
resultados['MesTransaccion'] = pd.to_datetime(resultados['MesTransaccion'].astype(str), format = '%Y-%m')
resultados['MesCohorte'] = pd.to_datetime(resultados['MesCohorte'].astype(str), format = '%Y-%m')

# Eliminar registros que no entran en el mes de cohorte de estudio
resultados_filtrados = resultados[resultados['MesTransaccion'] <= resultados['MesCohorte'] + pd.DateOffset(months = 5)]

# Crear la variable del mes desde el punto de vista del cliente
resultados_filtrados =  resultados_filtrados.copy()
#paso 1: Crear columnas temporales tipo Period [M]
mes_transaccion_period = resultados_filtrados['MesTransaccion'].dt.to_period('M')
mes_cohorte_period = resultados_filtrados['MesCohorte'].dt.to_period('M')
# paso 2: calcular la diferencia en meses de columnas temporales
diferencia_meses = mes_transaccion_period - mes_cohorte_period
# paso 3: crear la nueva columna MesCliente con la diferencia calculada
resultados_filtrados.loc[:, 'MesCliente'] = 'M' + diferencia_meses.apply(lambda x: str(x.n+1))


# Crear tabla pivotada a nivel de mes cliente
tabla_cohortes = pd.pivot_table(
    resultados_filtrados,
    index = 'MesCohorte',
    columns = 'MesCliente',
    values = 'ID_Cliente',
    aggfunc = 'nunique' 
).fillna(0).astype(int) 

# Calcular la tabla de retención
tabla_retencion = tabla_cohortes.div(tabla_cohortes['M1'], axis =0) * 100
tabla_retencion = tabla_retencion.round(1)


# Calcular el CAC medio con un merge utilizando 'ID_Cliente' como clave
resultados_filtrados = resultados_filtrados.merge(
    clientes[['ID_Cliente', 'CAC']], # Selecciona solo 'ID_Cliente' y 'CAC' de clientes
    on = 'ID_Cliente',
    how = 'left'
)

# Lo agregamos a nivel de cliente
cac_cliente = resultados_filtrados.groupby('ID_Cliente')['CAC'].first()
cac_medio = cac_cliente.mean()

# Cálculo de LTV por cliente
# Agrupamos por clientes y sumamos sus ventas totales
ltv_cliente = resultados_filtrados.groupby('ID_Cliente')[['Total_Venta']].sum()
ltv_cliente.columns = ['ltv']


# tablon analitico 

# Obtenemos los sociodemográficos en una variable
sociodemo = clientes[['ID_Cliente','Genero','Nivel_Educativo','Ocupacion','Tamano_Hogar']]


tablon_analitico = resultados_filtrados.merge(
    rfm,
    on = 'ID_Cliente',
    how = 'left'    
)

# Unir variables sociodemográficas
tablon_analitico = tablon_analitico.merge(
    sociodemo,
    on = 'ID_Cliente',
    how = 'left'
)

tablon_analitico = tablon_analitico.merge(
    ltv_cliente,
    on = 'ID_Cliente',
    how = 'left'
)

# Tablón a nivel cliente
tablon_cliente = tablon_analitico.groupby('ID_Cliente').agg({
       'MesCohorte':'first',
       'CAC':'first',
       'Recency':'first',
       'Frequency':'first',
       'Monetary':'first',
       'r':'first',
       'f':'first',
       'm':'first',
       'Segmento':'first',
       'Genero':'first',
       'Nivel_Educativo':'first',
       'Ocupacion':'first',
       'Tamano_Hogar':'first',
       'ltv':'first'
})


### tablon ltv_mes

ltv_mes = tablon_analitico.groupby(['ID_Cliente', 'MesCliente']).agg({'Total_Venta':'sum'}).reset_index()

ltv_agrupado = ltv_mes.groupby('MesCliente').agg(
    {'Total_Venta':'sum',
     'ID_Cliente':'nunique'}
)

# Calcular la base del estudio
ltv_agrupado['M1'] = ltv_agrupado.loc['M1','ID_Cliente']

ltv_agrupado['Ventas_por_M1'] = ltv_agrupado['Total_Venta'] / ltv_agrupado['M1']
ltv_agrupado = ltv_agrupado.reset_index()


# Exportar tablon final
tablon_analitico.to_csv('Desktop/Caso_Final2_CA/00_Datasets/tablon_analitico_clientes.csv', decimal = ',', index = False)

# Exportar tablon nivel cliente
tablon_cliente.to_csv('Desktop/Caso_Final2_CA/00_Datasets/tablon_cliente.csv', decimal = ',', index = False)

# Exportar tablon ltv_mes
ltv_agrupado.to_csv('Desktop/Caso_Final2_CA/00_Datasets/ltv_mes.csv', decimal = ',', index = False)
