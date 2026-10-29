# U1-A5 Manejo de errores y seguridad básica en Flask

## Ejecutar
1. Activa el venv de BD_Web: `..\venv\Scripts\activate`
2. `pip install -r requirements.txt`
3. `python app.py` -> http://127.0.0.1:5000 (debug desactivado para que se vea 500.html)
4. Opcional: copia `.env.example` a `.env` y pon tu `SENTRY_DSN` para activar Sentry.

## Rutas para probar
| Error | Cómo provocarlo |
|-------|-----------------|
| 400 | `GET /videogame/1` (falta `?vista=resumen` o `?vista=completa`) |
| 404 | `GET /cualquier-ruta-inexistente` o `/videogame/999?vista=completa` |
| 405 | `curl -X PUT http://127.0.0.1:5000/videogame/1` |
| 500 | `GET /forzar-error` (ejecuta 1/0; el traceback queda en `errors.log`) |
| API JSON | `GET /api/juegos/999`, `GET /api/no-existe`, `curl -X PATCH http://127.0.0.1:5000/api/juegos` |

## Archivos clave
- `app.py`: fábrica `create_app()`, manejadores de error, logging a `errors.log` y Sentry.
- `api/__init__.py`: hace que Flask-RESTful use los manejadores de `app.py` (JSON uniforme).
- `templates/400.html`, `404.html`, `405.html`, `500.html`: extienden `base.html`.
- `capturas/`: evidencias. `Reporte U1 A5 Manejo de Errores.pdf`: reporte.
