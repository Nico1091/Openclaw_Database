# Database IA - OpenClaw Dashboard

Sistema automatizado de base de datos y visualización para OpenClaw.

## Características

- **Base de datos SQLite** automática para almacenar conversaciones y modelos
- **Extracción automática** de datos de OpenClaw
- **Interfaz web moderna** y bonita con visualización en tiempo real
- **Auto-refresh** cada 5 minutos para datos actualizados
- **Gráficos interactivos** con Chart.js
- **Diseño responsive** con TailwindCSS

## Estructura

```
database_ia/
├── database_ia.db          # Base de datos SQLite
├── init_database.py        # Script para inicializar la BD
├── data_extractor.py       # Script para extraer datos de OpenClaw
├── app.py                  # Aplicación Flask
├── requirements.txt        # Dependencias
├── templates/
│   └── index.html         # Interfaz web
└── README.md              # Este archivo
```

## Instalación

1. Instalar dependencias:
```bash
pip install -r requirements.txt
```

2. Inicializar la base de datos:
```bash
python init_database.py
```

3. Extraer datos iniciales:
```bash
python data_extractor.py
```

## Uso

Iniciar el servidor web:
```bash
python app.py
```

Luego abrir en el navegador: `http://127.0.0.1:5000`

## Funcionalidades

- **Dashboard principal** con estadísticas en tiempo real
- **Gráficos** de tokens por modelo y sesiones por día
- **Tablas** de modelos disponibles y sesiones recientes
- **Auto-refresh** automático cada 5 minutos
- **Botón de actualización manual** para refresh inmediato

## Datos Almacenados

- **Modelos**: ID, nombre, proveedor, capacidades, costos
- **Sesiones**: ID, modelo, tokens, costos, timestamps
- **Skills**: Habilidades utilizadas por sesión
- **Mensajes**: Historial de conversaciones
- **Métricas**: Estadísticas de uso

## Automatización

El sistema incluye:
- Extracción automática de datos de OpenClaw
- Auto-refresh cada 5 minutos
- Actualización manual vía botón
- Background thread para sincronización continua
