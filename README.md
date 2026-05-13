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
Muestra la concentración geográfica de defunciones mediante un mapa coroplético con GeoJSON oficial de Colombia. Los departamentos con mayor intensidad de color (azul oscuro) corresponden a **Bogotá D.C.**, **Antioquia** y **Valle del Cauca**, que concentran el mayor volumen de muertes por su alta densidad poblacional y carga de enfermedades crónicas en centros urbanos. Los departamentos de la Amazonía y el Pacífico presentan los menores registros.

### 2. Gráfico de líneas – Muertes por mes
**Enero** (~21.000) y **diciembre** registran los valores más altos del año, con un segundo pico en **julio–agosto** (~21.000). **Febrero** es el mes con menor mortalidad (~18.100). El patrón sugiere mayor carga de muertes en los extremos del año y a mediados, coincidiendo con temporadas de lluvia y circulación de virus respiratorios.

### 3. Gráfico de barras – Top 5 ciudades más violentas (X95)
Homicidios por arma de fuego (código CIE-10 X95): **Santiago de Cali** lidera con **971**, seguido de **Bogotá D.C.** (601), **Medellín** (428), **Barranquilla** (260) y **San José de Cúcuta** (206). Refleja problemas estructurales de violencia urbana en las principales ciudades del país.

### 4. Gráfico circular – 10 ciudades con menor mortalidad
Los 10 municipios con menor registro de muertes — **Nuquí**, **Alto Baudó**, **Taraira**, **Margarita**, **El Encanto**, **Puerto Arica**, **Puerto Alegría**, **Mapiripana**, **San Fernando** y **Hato** — registraron cada uno **1 defunción** (10% del total en este grupo). Indica subregistro en zonas remotas o poblaciones muy pequeñas sin presencia institucional efectiva.

### 5. Tabla – Top 10 causas de muerte
| # | Código | Causa | Total |
|---|--------|-------|-------|
| 1 | I21 | Infarto Agudo del Miocardio | 35.323 |
| 2 | J44 | Enf. Pulmonares Obstructivas Crónicas (EPOC) | 15.804 |
| 3 | X95 | Agresión con disparo de armas de fuego | 9.273 |
| 4 | J18 | Neumonía, organismo no especificado | 7.437 |
| 5 | C16 | Tumor Maligno del Estómago | 5.434 |
| 6 | E14 | Diabetes Mellitus no especificada | 5.249 |
| 7 | C34 | Tumor Maligno de Bronquios y Pulmón | 4.499 |
| 8 | I11 | Enfermedad Cardíaca Hipertensiva | 3.635 |
| 9 | C50 | Tumor Maligno de la Mama | 3.633 |
| 10 | C61 | Tumor Maligno de la Próstata | 3.437 |

Las enfermedades cardiovasculares y respiratorias crónicas dominan, evidenciando la transición epidemiológica en Colombia.

### 6. Barras apiladas – Muertes por sexo y departamento
En todos los departamentos el número de muertes masculinas supera al femenino. La diferencia es más pronunciada en departamentos con alta violencia (Antioquia, Valle del Cauca, Córdoba), donde los homicidios afectan desproporcionadamente a hombres. La mortalidad masculina representa aproximadamente el **55% del total nacional**.

### 7. Histograma – Distribución por ciclo de vida
El grupo **Vejez (60-84 años)** concentra la mayor cantidad de defunciones con **115.453** casos, seguido de **Longevidad (85-100+ años)** con **56.061** y **Adultez intermedia (45-59 años)** con **29.105**. La mortalidad infantil y neonatal (4.520 y 2.771 respectivamente), aunque menor en volumen, sigue siendo relevante en términos de años de vida potencialmente perdidos (AVPP).

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
