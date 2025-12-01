# Airflow ELT Pipeline — Air Quality (OpenAQ, Mexico)

**Author:** Rogelio Novelo  
**Course:** Unit III – ELT Pipeline  

---

## 🌍 Phase 1 — Dataset Selection + Social/Environmental Justification

**Dataset:** OpenAQ – Global Air Quality (PM2.5, PM10, NO2, O3, CO) for Mexico.

### **Real-world Issue**  
La calidad del aire es un problema crítico tanto social como ambiental, ya que la exposición prolongada a contaminantes como PM2.5, PM10 o NO2 incrementa enfermedades respiratorias y cardiovasculares, afectando especialmente a comunidades urbanas vulnerables.

Analizar datos históricos permite identificar patrones de contaminación, zonas críticas y variaciones estacionales que mejoran estrategias de salud pública y movilidad.

### **Who Benefits**  
Gobiernos locales, hospitales, organizaciones ambientales y ciudadanos que requieren monitorear zonas críticas, emitir alertas o diseñar políticas públicas.

### **Why ELT Is Appropriate**  
El dataset crece continuamente, por lo que es necesario conservar la capa cruda (`raw`) intacta.  
ELT permite:
- Guardar siempre los datos sin modificar  
- Aplicar transformaciones posteriores (analytics)  
- Reprocesar cuando cambien reglas de negocio  

---

## ⚙ Phase 2 — Airflow ELT Pipeline (Full Implementation)

Este proyecto implementa una arquitectura **ELT real** usando Apache Airflow.

---

### 1️⃣ Extract (E)

- El DAG llama la API de OpenAQ  
- Descarga datos sin limpiar  
- Guarda el archivo crudo directamente en `/data/raw/`

---

### 2️⃣ Load (L)

Los datos crudos se guardan como:

data/raw/air_quality_raw_<timestamp>.csv

👉 *La capa RAW nunca se modifica.*

---

### 3️⃣ Transform (T)

Una segunda tarea procesa el archivo RAW más reciente:

Incluye:
- Limpieza de valores faltantes  
- Corrección de tipos  
- Creación de columna `hour`  
- Promedio por contaminante  
- Guardado en:
data/analytics/air_quality_analytics.csv


---

### 📁 Directorios

data/raw/ → RAW layer
data/analytics/ → Analytics layer
dags/ → Airflow DAGs
dashboard/ → Notebook del dashboard
docs/ → Imágenes (dashboard.png)


---

### 📡 Scheduling

@daily
Simula cargas automáticas de datos cada día.

---

### ⚠ Error Handling

- Retries (`retries=2`)
- Logging de errores
- try/except en transformación

---

### 🚀 Scaling Feature

- RAW → ANALYTICS totalmente separado  
- Pipeline preparado para cargas incrementales  
- Transformaciones desacopladas  

---

## 📊 Phase 3 — Dashboard Using the Analytics Table

El dashboard está en:
dashboard/dashboard_air_quality.ipynb

```python
from pathlib import Path
import pandas as pd

data_path = Path("data/analytics/air_quality_analytics.csv")
df = pd.read_csv(data_path)