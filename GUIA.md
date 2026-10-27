# Pregunta del día en Telegram · Prolince

## 1. Crear el bot
1. En Telegram abre @BotFather y envía `/newbot`.
2. Ponle nombre (p. ej. «Prolince Pregunta del Día») y un usuario terminado en `bot`.
3. Copia el token (algo como `123456789:AAH...`). No lo compartas.

## 2. Añadir el bot al canal
1. Canal → Administradores → Añadir administrador → busca el bot.
2. Deja activado «Publicar mensajes». Lo demás puede ir desactivado.
3. Anota el identificador del canal: `@nombredelcanal` si es público.
   Si es privado: reenvía un mensaje del canal a @userinfobot (o @RawDataBot) y copia el id `-100...`.

## 3. Crear el repositorio en GitHub
1. github.com → New repository → nombre `pregunta-del-dia` → **Private** → Create.
2. «uploading an existing file»: arrastra `pregunta_del_dia.py`, `GUIA.md` y la carpeta `bancos/`
   con los cuatro CSV dentro → Commit changes.
3. El flujo programado va en una carpeta oculta, así que créalo a mano:
   Add file → Create new file → en el nombre escribe `.github/workflows/pregunta-del-dia.yml`
   → pega el contenido del archivo `pregunta-del-dia.yml` → Commit changes.

## 4. Guardar el token y el canal
Settings → Secrets and variables → Actions → New repository secret:
- `TELEGRAM_TOKEN` = token del bot
- `TELEGRAM_CHAT`  = `@nombredelcanal` o `-100...`

## 5. Permitir que guarde el registro
Settings → Actions → General → Workflow permissions → **Read and write permissions** → Save.

## 6. Probar
Actions → «Pregunta del día» → Run workflow (puedes elegir banco) → Run.
En unos 30 s debe aparecer la encuesta en el canal y un archivo `estado.json` en el repositorio.
Prueba una vez cada banco.

## A partir de ahí
- Publica sola a las 08:00 y 18:00 UTC (09:00/19:00 en invierno, 10:00/20:00 en verano).
  GitHub puede retrasar unos minutos las ejecuciones programadas.
- Para actualizar un banco: sube el CSV nuevo a `bancos/` (con número de versión mayor o sustituyendo el anterior).
- Para cambiar horas: edita las líneas `cron` del .yml (hora UTC).
- Para cambiar el reparto: añade en el .yml, bajo `env:`, una línea
  `ROTACION: conocimientos,ingles,conocimientos,gramatica,conocimientos,ortografia` con el orden que queráis.
- Si algo falla, Actions → la ejecución en rojo → abre el paso para ver el error.
