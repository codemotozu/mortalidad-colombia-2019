# Dashboard de Mortalidad · Colombia 2019

## Introducción del proyecto
Aplicación web analítica interactiva que visualiza los datos de mortalidad no fetal de Colombia para el año 2019, desarrollada con **Python**, **Plotly** y **Dash**, y desplegada en **Azure App Service**.

## Objetivo
Analizar patrones demográficos y regionales de la mortalidad en Colombia 2019 mediante visualizaciones interactivas que permiten identificar tendencias, comparar departamentos y municipios, y explorar causas de muerte y distribución por edad y sexo.

## Estructura del proyecto
```
mortalidad_colombia/
├── app.py                                      # Aplicación principal Dash (lógica + layout)
├── requirements.txt                            # Dependencias Python
├── startup.txt                                 # Comando de inicio para Azure App Service
├── README.md                                   # Este archivo
├── .github/
│   └── workflows/
│       └── main_mortalidad-colombia-2019.yml   # Pipeline CI/CD GitHub Actions → Azure
└── data/
    ├── Anexo1.NoFetal2019_CE_15-03-23.xlsx     # Datos de mortalidad no fetal DANE 2019
    ├── Divipola_CE_.xlsx                       # División político-administrativa (DIVIPOLA)
    ├── Anexo2.CodigosDeMuerte_CE_15-03-23.xlsx # Catálogo de causas de muerte CIE-10 DANE
    └── Colombia.geo.json                       # GeoJSON de departamentos colombianos
```

## Visualizaciones con explicación de resultados

### 1. Mapa – Distribución de muertes por departamento
Muestra la concentración geográfica de defunciones. **Bogotá D.C.** (38.760), **Antioquia** (34.473) y **Valle del Cauca** (28.443) concentran el mayor volumen, lo que refleja tanto su alta densidad poblacional como la carga de enfermedades crónicas en centros urbanos.

### 2. Gráfico de líneas – Muertes por mes
La tendencia mensual revela que los meses de **enero y marzo** presentan picos de mortalidad, asociados a enfermedades respiratorias en temporadas frías. Se observa una leve disminución en mitad del año y un repunte al final.

### 3. Gráfico de barras – Top 5 ciudades más violentas (X95)
**Santiago de Cali** lidera con 971 homicidios por arma de fuego (código X95), seguido por Bogotá (601) y Medellín (428). Esto refleja problemas estructurales de violencia urbana concentrados en las tres principales ciudades del país.

### 4. Gráfico circular – 10 ciudades con menor mortalidad
Municipios como **Alto Baudó**, **Nuquí** y otros registraron solo 1 defunción en 2019, lo que puede indicar subregistro en zonas remotas o poblaciones muy pequeñas.

### 5. Tabla – Top 10 causas de muerte
El **Infarto Agudo del Miocardio (I21)** es la principal causa con 35.323 casos, seguido de **EPOC (J44)** con 15.804. Las enfermedades cardiovasculares y respiratorias dominan, evidenciando la transición epidemiológica en Colombia.

### 6. Barras apiladas – Muertes por sexo y departamento
En todos los departamentos el número de muertes masculinas supera al femenino, siendo la diferencia más pronunciada en departamentos con alta violencia. La mortalidad masculina representa ~55% del total nacional.

### 7. Histograma – Distribución por ciclo de vida
El grupo **Vejez (60-84 años)** concentra la mayor cantidad de defunciones, seguido de **Adultez intermedia (45-59 años)**. La mortalidad infantil y neonatal, aunque menor en volumen, sigue siendo relevante en términos de años de vida potencialmente perdidos.

## Requisitos
```
dash==2.18.2
plotly==5.24.1
pandas==2.2.3
openpyxl==3.1.5
gunicorn==23.0.0
```

## Instalación y ejecución local
```bash
# 1. Clonar el repositorio
git clone https://github.com/codemotozu/mortalidad-colombia-2019.git
cd mortalidad-colombia-2019

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar la app
python app.py
# → Abrir http://localhost:8050
```

## Despliegue en Azure App Service

### Requisitos previos
- Cuenta Azure (gratuita para estudiantes: $100 USD/año)
- Azure CLI instalado o acceso al portal web
- Repositorio en GitHub con el código

### Pasos

**1. Subir código a GitHub**
```bash
git init
git add .
git commit -m "Dashboard mortalidad Colombia 2019"
git branch -M main
git remote add origin https://github.com/codemotozu/mortalidad-colombia-2019.git
git push -u origin main
```

**2. Crear App Service en Azure Portal**
- Ir a `portal.azure.com` → **Crear recurso** → **Web App**
- Configuración:
  - **Runtime**: Python 3.11
  - **SO**: Linux
  - **Plan**: Free (F1) o Basic (B1)
  - **Región**: East US (o la más cercana)

**3. Conectar con GitHub (CI/CD)**
- En la App Service: **Deployment Center** → **GitHub**
- Seleccionar repositorio y rama `main`
- Azure desplegará automáticamente en cada push

**4. Configurar comando de inicio**
- En **Configuration** → **General Settings** → **Startup Command**:
```
gunicorn --bind=0.0.0.0 --timeout 600 app:server
```

**5. Verificar el despliegue**
- URL pública: `https://mortalidad-colombia-2019-eea0dvaveqdsgvew.eastus-01.azurewebsites.net/`

## Software utilizado
- **Python 3.11** – Lenguaje de programación
- **Dash 2.18** – Framework para apps web analíticas
- **Plotly 5.24** – Visualizaciones interactivas
- **Pandas 2.2** – Manipulación y análisis de datos
- **Gunicorn** – Servidor WSGI para producción
- **Azure App Service** – Plataforma PaaS para despliegue

## Fuente de datos
DANE – Estadísticas Vitales (EEVV) 2019: https://www.dane.gov.co/index.php/estadisticas-por-tema/salud/nacimientos-y-defunciones
