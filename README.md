# Airflow ELT Pipeline — Air Quality (OpenAQ, Mexico)

**Author:** Rogelio Novelo  
**Course:** Unit III – ELT Pipeline  

---

## 🌍 Phase 1 — Dataset Selection + Social/Environmental Justification

**Dataset:** OpenAQ – Global Air Quality (PM2.5, PM10, NO2, O3, CO) for Mexico.

### **Real-world Issue**  
La calidad del aire es un problema crítico tanto social como ambiental, ya que la exposición prolongada a contaminantes como PM2.5, PM10 o NO2 incrementa enfermedades respiratorias y cardiovasculares, afectando especialmente a comunidades urbanas vulnerables. Analizar datos históricos permite identificar patrones de contaminación, zonas críticas y variaciones estacionales que ayudan a mejorar estrategias de salud pública, movilidad y alertas ambientales.

### **Who Benefits**  
Gobiernos locales, hospitales, organizaciones ambientales y la ciudadanía pueden utilizar estos insights para diseñar políticas públicas, emitir alertas oportunas, regular el tráfico y priorizar intervenciones en zonas afectadas.

### **Why ELT Is Appropriate**  
Los datos de OpenAQ crecen continuamente, por lo que es necesario conservar la capa cruda (`raw`) intacta. El enfoque ELT carga primero los datos sin modificar y luego ejecuta transformaciones en una segunda capa (`analytics`), permitiendo reprocesamiento, auditoría y flexibilidad conforme evolucionen las reglas de negocio.

---

## ⚙ Phase 2 — Airflow ELT Pipeline (Full Implementation)

Este proyecto implementa una arquitectura **ELT real** usando Apache Airflow:

### 1. **E — Extract**
- El DAG llama a la API pública de OpenAQ.
- Los datos se descargan tal como vienen.
- No se aplica ninguna limpieza en esta etapa.

### 2. **L — Load (Raw Layer)**
Los datos crudos se guardan exactamente como llegan en:

data/raw/air_quality_raw_<timestamp>.csv

Esta capa permanece SIEMPRE intacta.

### 3. **T — Transform (Analytics Layer)**
Una segunda tarea transforma el último archivo raw:

Incluye:
- Limpieza de valores faltantes  
- Corrección de tipos  
- Creación de nuevas columnas (e.g. `hour`)  
- Agregaciones por contaminante  
- Exportación a:

data/analytics/air_quality_analytics.csv



### DAG Principal:
dags/air_quality_elt.py


### Directorios de Datos:
- `data/raw/` → Datos crudos (RAW)
- `data/analytics/` → Datos transformados (ANALYTICS)

### Scheduling
Configurado como:
@daily

Simula cargas automáticas de datos cada día.

### Error Handling
- Retries (`retries=2`)
- Logging de errores
- Uso de `try/except` en el proceso de transformación

### Scaling Feature (Requerido por la rúbrica)
- Separación RAW → ANALYTICS  
- Pipeline preparado para cargas incrementales  
- Transformaciones desacopladas del raw

---

## 📊 Phase 3 — Dashboard Using the Transformed Analytics Table

El dashboard fue creado usando Plotly + pandas en:
dashboard/dashboard_air_quality.ipynb


El dashboard **solo utiliza la capa analytics**, cumpliendo el requisito ELT:

```python
data_path = Path("data/analytics/air_quality_analytics.csv")

