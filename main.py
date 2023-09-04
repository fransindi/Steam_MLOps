from fastapi import FastAPI
import pandas as pd
import html

#instanciamos la api
app = FastAPI()

endpoint1 = pd.read_csv('data_endpoints/endpoint1.csv')
endpoint2 = pd.read_csv('data_endpoints/endpoint2.csv')
endpoint3 = pd.read_csv('data_endpoints/endpoint3.csv', encoding='utf-8')
endpoint4 = pd.read_csv('data_endpoints/endpoint4.csv')
endpoint5 = pd.read_csv('data_endpoints/endpoint5.csv')


endpoint1.set_index('user_id', inplace=True)
endpoint2['posted'] = pd.to_datetime(endpoint2['posted'])
endpoint3['genres'] = endpoint3['genres'].apply(html.unescape)


print(endpoint3[endpoint3['genres'] == 'Action']['Puesto'].values[0])


@app.get('/user_id/{user_id}')
async def userdata(user_id: str = None):
    items = endpoint1.loc[user_id]['items']
    precio = endpoint1.loc[user_id]['precio_total']
    recomend = endpoint1.loc[user_id]['porcentaje_recomendados']

    return f"Gasto total: {precio}, Cantidad de items: {items}, Porcentaje recomendados: {recomend}"

@app.get('/countreviews')
async def countreviews(fecha_inicio: str = None, fecha_final: str = None):
    filtro_fechas = (endpoint2['posted'] >= fecha_inicio) & (endpoint2['posted'] <= fecha_final)
    df_fechas_filtrado = endpoint2[filtro_fechas]
    cantidad_usuarios = df_fechas_filtrado['user_id'].nunique()
    cantidad_trues = df_fechas_filtrado[df_fechas_filtrado['recommend'] == True].shape[0]
    porcentaje = (cantidad_trues / cantidad_usuarios) * 100
    return f'Cantidad de usuarios: {cantidad_usuarios}, Porcentaje de Trues: {porcentaje}'


@app.get('/genre/{genero}')
async def genre(genre: str = None):
    genre = genre.strip()  # Elimina espacios en blanco alrededor del género
    
    filtro = endpoint3[endpoint3['genres'] == genre]
    if not filtro.empty:
        puesto = int(filtro['Puesto'].values[0])
        return {"Puesto": puesto}
    else:
        return {"Mensaje": "Género no encontrado"}
    
