# emoviesNewsTelegramBot

Bot de Telegram para monitorear cursos disponibles en eMOVIES y notificar cuando aparece uno nuevo según filtros configurables por chat.

## Requisitos

- Python 3.11+
- Dependencias de `requirements.txt`
- Token de bot de Telegram

## Variables de entorno

- `TELEGRAM_BOT_TOKEN` (obligatoria)
- `POLL_INTERVAL_SECONDS` (opcional, por defecto `300`)

## Ejecutar localmente

1. Instalar dependencias:

   ```bash
   pip install -r requirements.txt
   ```

2. Exportar variables de entorno.
3. Ejecutar:

   ```bash
   python bot.py
   ```

## Comandos del bot

- `/start` inicia el bot en el chat.
- `/help` muestra ayuda.
- `/menu` abre el menú interactivo para configurar filtros.
- `/filters` muestra los filtros activos.
- `/setfilter clave valor` cambia un filtro (ejemplo: `/setfilter disciplinary_field 280`).
- `/setfilter clave=valor` formato alternativo.
- `/resetfilters` vuelve a filtros por defecto.
- `/loadurl URL` carga filtros desde una URL de la API.
- `/check` consulta inmediatamente y notifica cursos nuevos.
- `/on` activa monitoreo automático del chat.
- `/off` pausa monitoreo automático del chat.

## Filtros soportados

- `uni_countries`
- `disciplinary_field`
- `course_university`
- `uni_languages`
- `course_levels`
- `course_drafts`
- `uni_search`
- `page`

## Deploy en Render

Este repositorio incluye `render.yaml` para desplegar como **Worker**.

1. Subir el proyecto a GitHub.
2. En Render: **New +** → **Blueprint**.
3. Seleccionar tu repositorio.
4. Configurar `TELEGRAM_BOT_TOKEN` en variables de entorno.
5. Deploy.

> Nota: el estado (`bot_state.json`) se guarda en disco local del contenedor. Si Render reinicia la instancia, ese estado puede perderse.