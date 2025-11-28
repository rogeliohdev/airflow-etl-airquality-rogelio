# \# Airflow ETL Pipeline — Air Quality (OpenAQ)

# 

# \*\*Author:\*\* Rogelio Novelo  

# \*\*Course:\*\* Unit III – ETL Pipeline  

# 

# ---

# 

# \## 🌍 Phase 1 — Dataset Selection + Problem Justification

# 

# \*\*Dataset:\*\* OpenAQ – Global Air Quality (PM2.5, PM10, NO2, O3, CO)

# 

# La calidad del aire es un tema crítico tanto social como ambiental, ya que la exposición prolongada a contaminantes como PM2.5, PM10 o NO2 incrementa enfermedades respiratorias y cardiovasculares, afectando especialmente a comunidades urbanas vulnerables. Analizar datos históricos de calidad del aire permite identificar patrones de contaminación, horas o zonas críticas y cambios estacionales que ayudan a mejorar estrategias de salud pública y movilidad. Este análisis contribuye a que gobiernos locales, ciudadanos, hospitales y organizaciones ambientales puedan tomar decisiones informadas para reducir riesgos, optimizar alertas y priorizar intervenciones en zonas afectadas, beneficiando la salud y bienestar de toda la comunidad.

# 

# ---

# 

# \## ⚙ Phase 2 — Airflow ETL Pipeline

# 

# The ETL pipeline:

# 

# \- Extracts air quality data from the OpenAQ public API (Mexico)

# \- Cleans the data (duplicates, missing values, type formatting)

# \- Filters main pollutants and aggregates average values by city and parameter

# \- Stores the cleaned dataset in the local `data/` folder

# \- Uses retries and logging for basic error handling

# \- Includes a scaling improvement (chunk processing + filtering)

# 

# DAG file: `dags/air\_quality\_etl.py`

# 

# ---

# 

# \## 📊 Phase 3 — Dashboard (Python)

# 

# The dashboard (Python + Plotly) reads the cleaned dataset and includes:

# 

# \- 1 KPI (overall mean pollution level)

# \- 2 charts (pollution by parameter and ranking by pollutant)

# 

# Dashboard file: `dashboard/dashboard\_air\_quality.ipynb`

# 

# ---

# 

# \## 🚀 How to Run (summary)

# 

# 1\. Put this repo inside your Airflow `dags` folder (or mount it with Docker).

# 2\. Start Airflow webserver and scheduler.

# 3\. Trigger DAG `air\_quality\_etl`.

# 4\. After the ETL finishes, the cleaned CSV will be in `data/air\_quality\_clean.csv`.

# 5\. Open the dashboard notebook and run all cells to generate the charts and KPI.



