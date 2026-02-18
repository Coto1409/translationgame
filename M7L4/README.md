# Juego de pronunciación (consola)

Pequeño juego de consola en Python donde se muestra una palabra en español y el jugador debe pronunciar su traducción en inglés.

Instalación:

```bash
python -m pip install -r requirements.txt
```

**Requisitos (versiones actuales):**

- Python: 3.11.1
- sounddevice==0.5.5
- scipy==1.17.0
- numpy==1.26.4
- SpeechRecognition==3.14.5
- googletrans==4.0.0rc1

Uso:

```bash
python main.py
```

Notas:
- El programa graba ~3 segundos por respuesta usando `sounddevice` y guarda WAV temporales en `tmp_records`.
- Usa `SpeechRecognition` (Google Web Speech) para transcribir el audio.
- Usa `googletrans` para mostrar la traducción de la transcripción al español como feedback.
- Si la transcripción y la traducción esperada tienen similitud > 0.7 se considera correcta (comparación fuzzy).

Comentarios en el código están en español para facilitar futuras mejoras con IA integrada.
