import os
import pandas as pd
import requests
from requests.auth import HTTPBasicAuth
import time
import json

# -------------------------------------------- FUNCIONES ------------------------------------------------------ #

def delete_file(filepath):
    if os.path.isfile(filepath):
        os.remove(filepath)
        print("Archivo eliminado con éxito.")
    else:
        print("El archivo no existe.")

# --------------------------------------------------------------------------------------------------------------- #   

def get_info_secop_json(usuario, contraseña, base_url):
    """Recupera todo el JSON paginado y devuelve:
       - raw_json: lista de dicts
       - raw_df: DataFrame (opcional)"""
    
    raw_json = []
    limit = 1000
    offset = 0
    # Se incorpora funcionalidad para esperar después de pasar un límite de requests por minuto por IP según configuración por defecto.
    request_count = 0
    request_limit = 59
    pause_duration = 70

    while True:
        
        if request_count >= request_limit:
            print(f"Se alcanzó el límite de {request_limit} requests. Esperando {pause_duration} segundos...")
            time.sleep(pause_duration)
            request_count = 0
        
        params = {'$limit': limit, '$offset': offset}
        resp = requests.get(base_url, auth=HTTPBasicAuth(usuario, contraseña), params=params)

        if resp.status_code != 200:
            print(f"Error en la conexión ({resp.status_code}): {resp.text}")
            break

        page = resp.json()  # suele ser una lista de dicts
        if not page:
            # ya no hay más registros
            break

        raw_json.extend(page)
        print(f"Se anexaron {len(page)} objetos JSON (total hasta ahora: {len(raw_json)})")
        offset += limit
        request_count += 1  # Incrementar contador

    raw_df = pd.DataFrame(raw_json)
    print(f"Todo correcto: JSON total={len(raw_json)} registros → DF {raw_df.shape}")
    return raw_df

# --------------------------------------------------------------------------------------------------------------- #  

def read_json(file):
    with open(file, "r", encoding='utf-8') as f:
        json_variable = json.load(f)
        return json_variable

# --------------------------------------------------------------------------------------------------------------- # 

def transform_data(raw_file, mapeo_campos, reemplazos_modalidad_s2, reemplazos_estados_s2):
    df = pd.read_parquet(raw_file)
    df.rename(columns=mapeo_campos, inplace=True)
    df.loc[:,'Fecha de Publicacion del Proceso'] = pd.to_datetime(df['Fecha de Publicacion del Proceso'])
    df.loc[:,'Fecha de Ultima Publicación'] = pd.to_datetime(df['Fecha de Ultima Publicación'])
    df.loc[:,'Fecha de Publicacion (Fase Seleccion)'] = pd.to_datetime(df['Fecha de Publicacion (Fase Seleccion)'])
    df_publicacion = df.copy()
    df = df.sort_values(by='Fecha de Publicacion del Proceso', ascending = False)
    df = df.drop_duplicates(subset='ID del Portafolio', keep='first')
    df_publicacion = df_publicacion.sort_values(by ='Fecha de Publicacion del Proceso',ascending = True)
    df_publicacion = df_publicacion.drop_duplicates(subset='ID del Portafolio', keep='first')
    df_publicacion.set_index('ID del Portafolio',inplace=True)
    df = pd.merge(df, df_publicacion['Fecha de Publicacion del Proceso'], left_on='ID del Portafolio', right_index=True, how='left')
    df.rename(columns={'Fecha de Publicacion del Proceso_y': 'Fecha de Publicacion inicial','Fecha de Publicacion del Proceso_x': 'Fecha de Publicacion final'}, inplace=True)
    df['Modalidad General'] = df['Modalidad de Contratacion'].replace(reemplazos_modalidad_s2)
    df = df[(df['Modalidad General'] != 'Contratación Directa') & (df['Modalidad General'] != 'Solicitud de información a los Proveedores') & (df['Modalidad General'] != 'Contratación régimen especial')]
    df['URLProceso'] = df['URLProceso'].astype(str).str.replace("{'url': '","").str.replace("'}","")
    df = df[df['Nombre del Proveedor Adjudicado']=='No Definido']
    df = df[df['ID del Portafolio'].duplicated()==False]
    df['Estado General'] = df['Estado Resumen'].replace(reemplazos_estados_s2)
    return df

# --------------------------------------------------------------------------------------------------------------- #