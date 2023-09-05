from fastapi import FastAPI
import pandas as pd
import html


#instanciamos la api
app = FastAPI()

#Extraemos los datos necesarios para nuestro primer endpoint
endpoint1 = pd.read_csv('data_endpoints/endpoint1.csv')
endpoint1.set_index('user_id', inplace=True)



@app.get('/user_id/{user_id}')
async def userdata(user_id: str = None):
    try:
        user_data = endpoint1.loc[user_id]
        if user_data is not None:
            items = user_data['items']
            precio = user_data['precio_total']
            recomend = user_data['porcentaje_recomendados']
            return f"Gasto total: {precio}, Cantidad de items: {items}, Porcentaje recomendados: {recomend}"
        else:
            return "El usuario no existe en los datos."
    except KeyError:
        return "Error: El usuario no se encontró en los datos o el formato de la solicitud es incorrecto."



endpoint2 = pd.read_csv('data_endpoints/endpoint2.csv')
endpoint2['posted'] = pd.to_datetime(endpoint2['posted'])

@app.get('/countreviews')
async def countreviews(fecha_inicio: str = None, fecha_final: str = None):
    try:
        # Filtrar las fechas
        filtro_fechas = (endpoint2['posted'] >= fecha_inicio) & (endpoint2['posted'] <= fecha_final)
        df_fechas_filtrado = endpoint2[filtro_fechas]
        
        # Calcular la cantidad de usuarios únicos y la cantidad de True
        cantidad_usuarios = df_fechas_filtrado['user_id'].nunique()
        cantidad_trues = df_fechas_filtrado['recommend'].sum()
        
        # Calcular el porcentaje
        if cantidad_usuarios > 0:
            porcentaje = (cantidad_trues / cantidad_usuarios) * 100
        else:
            porcentaje = 0
        
        return f'Cantidad de usuarios: {cantidad_usuarios}, Porcentaje de Trues: {porcentaje:.2f}%'
    except Exception as e:
        return f'Error: {str(e)}'




endpoint3 = pd.read_csv('data_endpoints/endpoint3.csv', encoding='utf-8')
endpoint3['genres'] = endpoint3['genres'].apply(html.unescape)
endpoint3.drop('Unnamed: 0', axis=1, inplace=True)
endpoint3.set_index('genres', inplace=True)



@app.get('/genre/{genero}')
async def genre(genre: str = None):
    try:
        genre_data = endpoint3.loc[genre]
        if genre_data is not None:
            puesto = int(genre_data['Puesto'])
            playtime = int(genre_data['TiempoTotal'])
            response = {
                "genero": genre,
                "puesto": puesto,
                "playtime": playtime
            }
            return response
        else:
            return {"error": f"El género {genre} no se encuentra en los datos."}
    except Exception as e:
        return {"error": str(e)}


endpoint4 = pd.read_csv('data_endpoints/endpoint4.csv')
endpoint4.drop('Unnamed: 0', axis=1, inplace=True)
    
@app.get('/userforgenre/{genero}')
async def userforgenre(genre: str = None):
    try:
        mask = endpoint4[endpoint4['genres'] == genre]
        if not mask.empty:
            list_users = list(mask.user_id.values)
            # Limitar la cantidad de resultados si es necesario
            max_results = 100  # Cambia este valor según tus necesidades
            list_users = list_users[:max_results]
            response = {"users": list_users}
            return response
        else:
            return {"message": f"No se encontraron usuarios para el género {genre}."}
    except Exception as e:
        return {"error": str(e)}

endpoint5 = pd.read_csv('data_endpoints/endpoint5.csv', encoding='utf-8')
endpoint5.drop('Unnamed: 0', axis=1, inplace=True)
endpoint5['release_date'] = pd.to_datetime(endpoint5['release_date'])
endpoint5.dropna(inplace=True)
endpoint5['price'] = endpoint5['price'].astype('float')
endpoint5['release_date'] = endpoint5['release_date'].dt.year


@app.get('/developer/{developer}')
async def developer(developer: str = None):
    try:
        # Filtrar el DataFrame para obtener solo los juegos del desarrollador especificado
        juegos_del_desarrollador = endpoint5[endpoint5['developer'] == developer]

        porcentajes_por_anio = {}

        años_unicos = juegos_del_desarrollador['release_date'].unique().tolist()

        for año in años_unicos:
            juegos_del_año = juegos_del_desarrollador[juegos_del_desarrollador['release_date'] == año]
            juegos_gratis_del_año = juegos_del_año[juegos_del_año['price'] == 0]
            
            porcentaje_juegos_gratis = (len(juegos_gratis_del_año) / len(juegos_del_año)) * 100
            
            porcentajes_por_anio[año] = porcentaje_juegos_gratis

        return {"developer": developer, "porcentajes_por_anio": porcentajes_por_anio}
    except Exception as e:
        return {"error": str(e)}


endpoint6 = pd.read_csv('data_endpoints/endpoint6.csv')
endpoint6.drop('Unnamed: 0', axis=1, inplace=True)
endpoint6['Año'] = endpoint6['Año'].astype(str)


print(endpoint6)




@app.get('/analizarsentimiento/{anio}')
async def analizar_sentimiento_por_año(anio: str = None):
    try:
        mask = endpoint6[endpoint6['Año'] == anio]
        if not mask.empty:
            positivos = int(mask['Positivo'])
            neutro = int(mask['Neutro'])
            negativo = int(mask['Negativo'])
            
            response = {
                "anio": anio,
                "positivos": positivos,
                "negativos": negativo,
                "neutros": neutro
            }
            return response
        else:
            return {"mensaje": f"No se encontraron datos para el año {anio}."}
    except Exception as e:
        return {"error": str(e)}
    


recomendacion = pd.read_csv('data_endpoints/recomendacion.csv')
recomendacion.drop('Unnamed: 0', axis=1, inplace=True)
print(recomendacion[recomendacion['titulo'] == 'Ironbound']['juegos_recomendados'])




@app.get('/recomendacion_juegos/{titulo}')
async def recomendacion_juegos(titulo: str = None):
    try:
        mask = recomendacion[recomendacion['titulo'] == titulo]
        if not mask.empty:
            recomendar = mask['juegos_recomendados'].iloc[0]  # Obtener la lista de juegos recomendados
            return {"juegos_recomendados": recomendar}
        else:
            return {"mensaje": f"No se encontraron datos para el título {titulo}."}
    except Exception as e:
        return {"error": str(e)}