import os
import random
import unicodedata

# Usaremos librerías simples: sounddevice para grabar, scipy para WAV, speech_recognition y googletrans
try:
    import sounddevice as sd
    from scipy.io.wavfile import write
    import numpy as np
except Exception:
    print("Faltan librerías de audio (sounddevice/scipy/numpy). Instala requirements.txt.")
    raise

try:
    import speech_recognition as sr
except Exception:
    print("Falta 'SpeechRecognition'. Instala requirements.txt.")
    raise

try:
    from googletrans import Translator
except Exception:
    print("Falta 'googletrans'. Instala requirements.txt.")
    raise

from difflib import SequenceMatcher


def normalize_text(s):
    # limpiar y normalizar texto para comparaciones robustas.
    # Quitar tildes y dejar solo alfanuméricos y espacios
    s = s.lower()
    s = unicodedata.normalize('NFD', s)
    s = ''.join(ch for ch in s if unicodedata.category(ch) != 'Mn')
    return ''.join(ch for ch in s if ch.isalnum() or ch.isspace()).strip()


def record_audio(filename, duration=3, fs=44100):
    # avisar al usuario y grabar audio en mono. Se escala antes de guardar
    print(f"▶️  Grabando {duration} segundos... Habla ahora")
    try:
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
        sd.wait()
    except Exception as e:
        print("Error al grabar. Revisa el micrófono:", e)
        return False

    try:
        peak = np.max(np.abs(recording))
        if peak == 0:
            scaled = np.int16(recording * 32767)
        else:
            scaled = np.int16(recording / peak * 32767)
        write(filename, fs, scaled)
        return True
    except Exception as e:
        print("No se pudo guardar el audio:", e)
        return False


def recognize_speech_from_file(filename):
    # envolver reconocimiento con manejo de excepciones para fallos comunes
    r = sr.Recognizer()
    try:
        with sr.AudioFile(filename) as source:
            audio = r.record(source)
        text = r.recognize_google(audio, language='en-US')
        return text
    except sr.UnknownValueError:
        return None
    except Exception as e:
        print("Error en reconocimiento de voz:", e)
        return None


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def select_level():
    options = {
        '1': 'facil',
        '2': 'medio',
        '3': 'dificil'
    }
    print("\nSelecciona nivel de dificultad:")
    print("1) 🟢 Fácil   2) 🟡 Medio   3) 🔴 Difícil")
    choice = input("Tu elección (1/2/3): ").strip()
    return options.get(choice, 'facil')


def main():
    # Diccionario por niveles (varias palabras por nivel)
    words_by_level = {
        'facil': ['cat', 'dog', 'house', 'book', 'car'],
        'medio': ['apple', 'water', 'table', 'chair', 'window'],
        'dificil': ['elephant', 'bicycle', 'refrigerator', 'development', 'extraordinary']
    }

    print("\n=== 🎯 Juego de Pronunciación (Esp → En) ===")
    print("Reglas: seleccionar nivel → se muestra palabra en español → pronuncia en inglés.")
    print("Se graba, se transcribe, se traduce la transcripción para feedback y se compara.")
    print("El juego termina cuando cometes 3 errores. ¡Suerte! 🍀\n")

    level = select_level()
    print(f"Has seleccionado: {level}\n")

    # Mapa de palabras español->inglés para mostrar la palabra en español
    # Se eligen palabras inglesas pero mostramos su equivalente en español al jugador.
    en_to_es = {
        'cat': 'gato', 'dog': 'perro', 'house': 'casa', 'book': 'libro', 'car': 'coche',
        'apple': 'manzana', 'water': 'agua', 'table': 'mesa', 'chair': 'silla', 'window': 'ventana',
        'elephant': 'elefante', 'bicycle': 'bicicleta', 'refrigerator': 'heladera',
        'development': 'desarrollo', 'extraordinary': 'extraordinario'
    }

    translator = Translator()
    score = 0
    errors = 0
    round_num = 0
    tmpdir = 'tmp_records'
    os.makedirs(tmpdir, exist_ok=True)

    # bucle principal del juego. Se permiten hasta 3 errores antes de terminar.
    # La IA recomendó registrar rondas, puntuación y errores para feedback claro.
    while errors < 3:
        round_num += 1
        # elegir palabra en inglés del nivel
        word_en = random.choice(words_by_level[level])
        word_es = en_to_es.get(word_en, '---')

        print(f"Ronda {round_num} — Palabra: {word_es} → traduce y pronuncia en inglés")
        input("Presiona Enter y luego habla la traducción en inglés...")
        fname = os.path.join(tmpdir, f"rec_{round_num}.wav")
        ok = record_audio(fname, duration=3)
        if not ok:
            print("No se grabó. Intenta otra vez.")
            continue

        recognized = recognize_speech_from_file(fname)
        if recognized is None:
            print("No se reconoció audio. Error +1")
            errors += 1
            print(f"Puntuación: {score} | Errores: {errors}/3\n")
            continue

        # convertir todo a minúsculas y normalizar
        recognized = recognized.lower()
        norm_rec = normalize_text(recognized)
        norm_target = normalize_text(word_en)

        print(f"🔊 Transcripción: {recognized}")
        # feedback: traducir la transcripción al español para que el jugador vea lo que se entendió
        try:
            back = translator.translate(recognized, dest='es').text
            print(f"🔁 Interpretado como (es): {back}")
        except Exception:
            print("(No se pudo traducir la transcripción)")

        ratio = similar(norm_rec, norm_target)
        print(f"Comparando: '{norm_rec}' vs '{norm_target}' → similitud {ratio:.2f}")

        # umbral simple
        if ratio >= 0.75:
            print("✅ Correcto! +1 punto.\n")
            score += 1
        else:
            print(f"❌ Incorrecto. Esperado: {word_en}\n")
            errors += 1

        print(f"Puntuación actual: {score} | Errores: {errors}/3\n")

    # fin del juego
    print("=== FIN DEL JUEGO ===")
    print("\nResumen final:")
    print(f"Rondas jugadas: {round_num}")
    print(f"Puntos: {score}")
    print("Gracias por jugar! 🏆\n")


if __name__ == '__main__':
    main()
 