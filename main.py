from fastapi import FastAPI
import pandas as pd
import html


#instanciamos la api
app = FastAPI()

endpoint1 = pd.read_csv('data_endpoints/endpoint1.csv')
endpoint1.set_index('user_id', inplace=True)



@app.get('/user_id/{user_id}')
async def userdata(user_id: str = None):
    items = endpoint1.loc[user_id]['items']
    precio = endpoint1.loc[user_id]['precio_total']
    recomend = endpoint1.loc[user_id]['porcentaje_recomendados']

    return f"Gasto total: {precio}, Cantidad de items: {items}, Porcentaje recomendados: {recomend}"

endpoint2 = pd.read_csv('data_endpoints/endpoint2.csv')
endpoint2['posted'] = pd.to_datetime(endpoint2['posted'])

@app.get('/countreviews')
async def countreviews(fecha_inicio: str = None, fecha_final: str = None):
    filtro_fechas = (endpoint2['posted'] >= fecha_inicio) & (endpoint2['posted'] <= fecha_final)
    df_fechas_filtrado = endpoint2[filtro_fechas]
    cantidad_usuarios = df_fechas_filtrado['user_id'].nunique()
    cantidad_trues = df_fechas_filtrado[df_fechas_filtrado['recommend'] == True].shape[0]
    porcentaje = (cantidad_trues / cantidad_usuarios) * 100
    return f'Cantidad de usuarios: {cantidad_usuarios}, Porcentaje de Trues: {porcentaje}'


endpoint3 = pd.read_csv('data_endpoints/endpoint3.csv', encoding='utf-8')
endpoint3['genres'] = endpoint3['genres'].apply(html.unescape)
endpoint3.drop('Unnamed: 0', axis=1, inplace=True)
endpoint3.set_index('genres', inplace=True)

print(endpoint3.loc['Action']['Puesto'])



@app.get('/genre/{genero}')
async def genre(genre: str = None):
    try:
        puesto = int(endpoint3.loc[genre]['Puesto'])
        playtime = int(endpoint3.loc[genre]['TiempoTotal'])
        return f"El genero {genre} se encuentra en el puesto {puesto} con un playtime de {playtime}"
    except Exception as e:
        return {"error": str(e)}


endpoint4 = pd.read_csv('data_endpoints/endpoint4.csv')
endpoint4.drop('Unnamed: 0', axis=1, inplace=True)
    
@app.get('/userforgenre/{genero}')
async def userforgenre(genre: str = None):
    mask = endpoint4[endpoint4['genres'] == genre]
    list_users = list(mask.user_id.values)
    return list_users

endpoint5 = pd.read_csv('data_endpoints/endpoint5.csv', encoding='utf-8')
endpoint5.drop('Unnamed: 0', axis=1, inplace=True)
endpoint5['release_date'] = pd.to_datetime(endpoint5['release_date'])
endpoint5.dropna(inplace=True)
endpoint5['price'] = endpoint5['price'].astype('float')
endpoint5['release_date'] = endpoint5['release_date'].dt.year


@app.get('/developer/{developer}')
async def developer(developer: str = None):
    # Filtrar el DataFrame para obtener solo los juegos del desarrollador especificado
    juegos_del_desarrollador = endpoint5[endpoint5['developer'] == developer]

    porcentajes_por_anio = {}

    años_unicos = juegos_del_desarrollador['release_date'].unique().tolist()

    for año in años_unicos:
        juegos_del_año = juegos_del_desarrollador[juegos_del_desarrollador['release_date'] == año]
        juegos_gratis_del_año = juegos_del_año[juegos_del_año['price'] == 0]
        
        porcentaje_juegos_gratis = (len(juegos_gratis_del_año) / len(juegos_del_año)) * 100
        
        porcentajes_por_anio[año] = porcentaje_juegos_gratis

    return porcentajes_por_anio


endpoint6 = pd.read_csv('data_endpoints/endpoint6.csv')
endpoint6.drop('Unnamed: 0', axis=1, inplace=True)
endpoint6['Año'] = endpoint6['Año'].astype(str)


print(endpoint6)




@app.get('/analizarsentimiento/{anio}')
async def analizar_sentimiento_por_año(anio: str = None):
    mask = endpoint6[endpoint6['Año'] == anio]
    positivos = int(mask['Positivo'])
    neutro = int(mask['Neutro'])
    negativo = int(mask['Negativo'])
    return f"En el anio: {anio}, hubieron {positivos}, reviews positivas, {negativo}, reviews negativas y {neutro} reviews neutras"