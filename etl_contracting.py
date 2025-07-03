from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, time, timedelta
import pandas as pd
from airflow.models import Variable

import os
import sys

curr_folder = os.path.dirname(os.path.abspath(__file__))
sys.path.append(curr_folder)
raw_file = os.path.join(curr_folder,'outputs/raw_data.parquet')
clean_file = os.path.join(curr_folder,'outputs/clean_data.parquet')
usuario = Variable.get("USER")
contraseña = Variable.get("PASSWORD")
base_url = Variable.get("BASEURLPROCESOS")

import funciones.funciones_complementarias as fc

def extract_dag():
    raw_df = fc.get_info_secop_json(usuario, contraseña, base_url)
    raw_df.to_parquet(raw_file, index=False)

def transform_dag():
    mapeo_campos_file = os.path.join(curr_folder,'support/mapeo_campos.json')
    mapeo_campos = fc.read_json(mapeo_campos_file)
    reemplazos_modalidad_s2_file = os.path.join(curr_folder,'support/reemplazos_modalidad_s2.json')
    reemplazos_modalidad_s2 = fc.read_json(reemplazos_modalidad_s2_file)
    reemplazos_estados_s2_file = os.path.join(curr_folder,'support/reemplazos_estados_s2.json')
    reemplazos_estados_s2 = fc.read_json(reemplazos_estados_s2_file)
    df = fc.transform_data(raw_file, mapeo_campos, reemplazos_modalidad_s2, reemplazos_estados_s2)
    df.to_parquet(clean_file, index=False)

default_args = {
    'start_date':datetime(2025, 6, 17),
    'sla':timedelta(minutes=20),
    'catchup':False
}

with DAG(dag_id='Pruebas_contratos_secop', default_args=default_args, schedule_interval='0 */5 * * *', ) as dag:
    
    tarea_extract = PythonOperator(task_id='tarea_extract', python_callable=extract_dag)
    tarea_transform = PythonOperator(task_id='tarea_transform', python_callable=transform_dag)
    
    tarea_extract >> tarea_transform
