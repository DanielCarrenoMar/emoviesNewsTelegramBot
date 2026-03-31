# emoviesNewsTelegramBot

Bot de Telegram para monitorear cursos disponibles en eMOVIES y notificar cuando aparece uno nuevo según filtros configurables por chat.

## Requisitos

- Python 3.11+
- Dependencias de `requirements.txt`
- Token de bot de Telegram

## Variables de entorno

- `TELEGRAM_BOT_TOKEN` (obligatoria)
- `POLL_INTERVAL_SECONDS` (opcional, por defecto `2700`)
- `DB_URL` (obligatoria para persistencia)

## Ejecutar localmente

1. Instalar dependencias:

   ```bash
   pip install -r requirements.txt
   ```

2. Exportar variables de entorno.
3. Ejecutar:

   ```bash
   python main.py
   ```

## Comandos del bot

- `/start` inicia el bot en el chat.
- `/help` muestra ayuda.
- `/filters` permite ver y modificar los filtros activos.
- `/resetfilters` vuelve a filtros por defecto.
- `/check` consulta inmediatamente y notifica cursos nuevos.
- `/on` activa monitoreo automático del chat.
- `/off` pausa monitoreo automático del chat.
- `/courseList` devuelve cursos segun los filtros configurados

## Filtros soportados

- `uni_countries`
- `disciplinary_field`
- `course_university`
- `uni_languages`
- `course_levels`