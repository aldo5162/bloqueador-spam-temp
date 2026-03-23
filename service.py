import time
import sqlite3
import re
from jnius import autoclass
from os import environ

# Configuramos el entorno para que jnius encuentre las clases de Android
PythonService = autoclass('org.kivy.android.PythonService')
Context = autoclass('android.content.Context')
TelephonyManager = autoclass('android.telephony.TelephonyManager')


def limpiar_numero(numero):
    # Elimina cualquier cosa que no sea un número (paréntesis, espacios, +)
    return re.sub(r'\D', '', str(numero))


def debe_bloquear(numero_entrante):
    num_limpio = limpiar_numero(numero_entrante)

    # Conectamos a la misma DB que creaste en el main.py
    # Nota: En Android el path suele ser el mismo donde está el servicio
    conn = sqlite3.connect('bloqueador.db')
    cursor = conn.cursor()
    cursor.execute("SELECT prefijo FROM spam")
    prefijos = [row[0] for row in cursor.fetchall()]
    conn.close()

    for p in prefijos:
        if num_limpio.startswith(p):
            return True
    return False


def check_calls():
    # Este es el bucle que se queda "vigilando"
    while True:
        # Aquí la lógica de Android 13 requiere que el sistema nos avise,
        # pero para uso personal, este servicio puede monitorear el estado del teléfono.
        # (La implementación completa de CallScreeningService requiere Java nativo,
        # pero este método de 'Service' es el puente más estable en Python).

        # Por ahora, dejamos el servicio corriendo para mantener la app viva.
        time.sleep(5)


if __name__ == '__main__':
    check_calls()