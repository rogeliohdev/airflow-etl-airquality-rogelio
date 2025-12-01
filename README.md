# Airflow ELT Pipeline — Air Quality (OpenAQ, Mexico)

**Author:** Rogelio Novelo  
**Course:** Unit III – ELT Pipeline  

---

## 🌍 Phase 1 — Dataset Selection + Social/Environmental Justification

**Dataset:** OpenAQ – Global Air Quality (PM2.5, PM10, NO2, O3, CO) for Mexico.

**Real-world issue.**  
La calidad del aire es un problema crítico tanto social como ambiental, ya que la exposición prolongada a contaminantes como PM2.5, PM10 o NO2 incrementa enfermedades respiratorias y cardiovasculares, afectando especialmente a comunidades urbanas urbanas vulnerables. Analizar datos históricos de calidad del aire permite identificar patrones de contaminación, horas o zonas críticas y cambios estacionales que ayudan a mejorar estrategias de salud pública y movilidad.

**Who benefits.**  
Gobiernos locales, hospitales, organizaciones ambientales y la ciudadanía en general pueden usar estos insights para diseñar políticas públicas, definir zonas de alerta, ajustar movilidad y priorizar intervenciones en áreas con mayor riesgo.

**Why ELT is appropriate.**  
Los datos de OpenAQ son *continuos* y crecen con el tiempo, por lo que es importante conservar siempre la capa de datos crudos (`raw`) sin modificarla. Esto permite reprocesar la historia cuando cambian las reglas de negocio o las transformaciones. El enfoque ELT (Extract → Load → Transform) carga primero los datos crudos en una capa de almacenamiento y después aplica transformaciones en una capa de analytics, lo cual es ideal para datasets en crecimiento y para experimentación analítica.

---

## ⚙ Phase 2 — Airflow ELT Pipeline (Full Implementation)

This project implements a **true ELT architecture**:

1. **E — Extract**  
   - Airflow llama a la API pública de OpenAQ para descargar mediciones de calidad del aire de México.
   - El script NO limpia nada en esta etapa.

2. **L — Load (Raw Layer)**  
   - Los datos se cargan tal cual vienen a archivos CSV en:  
     `data/raw/air_quality_raw_<timestamp>.csv`  
   - Esta carpeta representa la **tabla raw**: siempre permanece intacta.

3. **T — Transform (Analytics Layer)**  
   - Una segunda tarea de Airflow lee el archivo raw más reciente.
   - Aplica las transformaciones requeridas:
     - Limpieza de valores faltantes (`dropna` en `value`)
     - Corrección de tipos (`value` como `float`, fechas como `datetime`)
     - Creación de una nueva columna (`hour` a partir de la fecha)
     - Agregación del valor promedio por contaminante (`parameter`)
   - El resultado se guarda en la capa de analytics:  
     `data/analytics/air_quality_analytics.csv`  
   - La capa raw no se modifica nunca.

### DAGs & Files

- **ELT DAG principal:**  
  `dags/air_quality_elt.py`  
  - `extract_raw_task` → descarga y guarda en `/data/raw/`  
  - `transform_analytics_task` → lee raw y escribe en `/data/analytics/`

- **Directorios de datos (creados automáticamente si no existen):**
  - `data/raw/` → CSVs crudos
  - `data/analytics/` → CSV transformado para analytics/dashboard

### Scheduling

El DAG está
