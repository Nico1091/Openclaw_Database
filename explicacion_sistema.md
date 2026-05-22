# Explicación del Sistema Database IA

## Total de Endpoints: 8

### Lista de Endpoints:

1. **GET /** - Página principal (index.html)
2. **GET /api/models** - Obtiene todos los modelos de la base de datos SQL
3. **GET /api/sessions** - Obtiene todas las sesiones de la base de datos SQL
4. **GET /api/skills** - Obtiene todas las skills de la base de datos SQL
5. **GET /api/stats** - Obtiene estadísticas generales (sesiones, modelos, tokens, costos)
6. **GET /api/refresh** - Actualiza datos extraídos de OpenClaw y los guarda en SQL
7. **GET /api/messages** - Obtiene todos los mensajes de conversaciones de SQL
8. **GET /api/messages/<session_id>** - Obtiene mensajes de una sesión específica de SQL

## Funcionamiento

- Todos los datos se almacenan en SQLite (database_ia.db)
- Los endpoints extraen datos directamente de SQL
- El sistema se actualiza automáticamente cada 5 minutos vía auto-refresh
- Las conversaciones se extraen de archivos .jsonl de OpenClaw y se guardan en SQL
- Todo el flujo es: Archivos OpenClaw → SQL → Endpoints → Interfaz Web
