"""
Servicio de filtrado de llamadas para Android 13+
Implementa CallScreeningService usando pyjnius
"""

from jnius import autoclass, PythonJavaClass, java_method
import sqlite3
import re

# Clases Java necesarias
CallScreeningService = autoclass('android.telecom.CallScreeningService')
Call = autoclass('android.telecom.Call')
CallResponse = autoclass('android.telecom.CallResponse')
Uri = autoclass('android.net.Uri')


def limpiar_numero(numero):
    """Elimina todo excepto dígitos del número de teléfono"""
    if not numero:
        return ""
    return re.sub(r'\D', '', str(numero))


def obtener_prefijos_bloqueados():
    """Lee la base de datos y devuelve la lista de prefijos/números a bloquear"""
    try:
        conn = sqlite3.connect('/data/data/org.bloqueador_spam.app/files/bloqueador.db')
        cursor = conn.cursor()
        cursor.execute("SELECT prefijo FROM spam")
        prefijos = [row[0] for row in cursor.fetchall()]
        conn.close()
        return prefijos
    except Exception as e:
        print(f"Error leyendo DB: {e}")
        return ['600', '809']  # Valores por defecto si falla


class MiCallScreeningService(PythonJavaClass):
    """Implementación Python del servicio de filtrado de llamadas"""

    __javainterfaces__ = ['android/telecom/CallScreeningService']
    __javacontext__ = 'app'

    @java_method('(Landroid/telecom/Call$Details;)V')
    def onScreenCall(self, call_details):
        """
        Método llamado por Android cuando llega una llamada entrante.
        Este es el punto de entrada principal.
        """
        try:
            # Obtener el número de teléfono
            handle = call_details.getHandle()
            if handle is None:
                return

            numero_uri = handle.getSchemeSpecificPart()
            numero_limpio = limpiar_numero(numero_uri)

            print(f"Llamada entrante detectada: {numero_limpio}")

            # Verificar si debe bloquearse
            if self.debe_bloquear(numero_limpio):
                print(f"Bloqueando llamada: {numero_limpio}")
                self.bloquear_llamada()
            else:
                print(f"Permitiendo llamada: {numero_limpio}")
                self.permitir_llamada()

        except Exception as e:
            print(f"Error en onScreenCall: {e}")
            # En caso de error, permitir la llamada para no bloquear por error
            self.permitir_llamada()

    def debe_bloquear(self, numero):
        """Determina si el número debe ser bloqueado"""
        if not numero:
            return False

        prefijos = obtener_prefijos_bloqueados()

        for prefijo in prefijos:
            if numero.startswith(prefijo):
                return True

        return False

    def bloquear_llamada(self):
        """Construye y envía la respuesta de bloqueo"""
        try:
            # Construir la respuesta de bloqueo
            response_builder = CallResponse.Builder()
            response_builder.setDisallowCall(True)
            response_builder.setRejectCall(True)
            response_builder.setSkipCallLog(True)
            response_builder.setSkipNotification(True)
            response = response_builder.build()

            # Enviar la respuesta al sistema
            self.respondToCall(None, response)

        except Exception as e:
            print(f"Error al bloquear: {e}")

    def permitir_llamada(self):
        """Permite que la llamada proceda normalmente"""
        try:
            response_builder = CallResponse.Builder()
            response_builder.setDisallowCall(False)
            response = response_builder.build()

            self.respondToCall(None, response)

        except Exception as e:
            print(f"Error al permitir: {e}")


# Para depuración, imprimir que el servicio está cargado
print("Servicio CallScreeningService cargado correctamente")