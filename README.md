# 🔄 SECOP II - Extracción y Transformación Automática de Datos con Apache Airflow

Automatización inteligente del monitoreo de contratos en SECOP II con Apache Airflow. Extrae, transforma y organiza datos públicos de procesos de contratación publicados en tiempo real para análisis estratégicos. 

Este proyecto permite la **automatización del proceso de extracción y transformación** de datos públicos provenientes de la plataforma [SECOP II](https://www.colombiacompra.gov.co/secop/secop-ii), usando Airflow para la orquestación y Python para el procesamiento.

## 📂 Estructura del Proyecto

![image](https://github.com/user-attachments/assets/3e3a081b-cf7b-42e6-a7e3-725e4102474c)

## ⚙️ DAG principal

- **ID del DAG:** `procesos_secop`
- **Frecuencia:** Cada 5 horas (`0 */5 * * *`)
- **Tareas:**
  - `tarea_extract`: Se conecta a la API de SECOP II, descarga los datos y los guarda como `raw_data.parquet`.
  - `tarea_transform`: Lee los datos crudos, realiza transformaciones necesarias y genera un archivo `clean_data.parquet`.
Por defecto las tratamos como archivos parquet por eficiencia del proceso. Sin embargo, es posible adaptarlo a cualquier formato tabular (ej: .csv, .xlsx)

## 🧠 Funcionalidades

- Descarga paginada desde la API de SECOP II (soporta autenticación básica).
- Transformación de campos con reglas de negocio:
  - Mapeo de nombres de columnas.
  - Filtrado por estados y modalidad de contratación.
  - Conversión de fechas.
  - Estandarización de URL y campos clave.
- Limpieza de duplicados y datos incompletos.

## 🔐 Manejo de credenciales

Las credenciales para acceder a la API de SECOP II están gestionadas mediante **Variables de Airflow**, configuradas en la interfaz web:
- `USER`
- `PASSWORD`
- `BASEURLPROCESOS`

## ⚙️ Requisitos:

- Python 3.8+
- Apache Airflow 2.x
- Pandas
- Requests
- (Opcional) .env para pruebas locales

📊 Casos de uso:

- Monitoreo de procesos de contratación sin adjudicación.
- Análisis de modalidades de contratación más usadas actualmente.
- Integración con dashboards en Power BI o plataformas analíticas tanto para proveedores como entidades estatales.
