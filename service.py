"""
Servicio de filtrado de llamadas para Android 13+
Implementación simplificada
"""

import sqlite3
import re
import os

try:
    from jnius import autoclass, PythonJavaClass, java_method
    from android.storage import app_storage_path

    CallScreeningService = autoclass('android.telecom.CallScreeningService')
    Call = autoclass('android.telecom.Call')
    CallResponse = autoclass('android.telecom.CallResponse')

    JNI_AVAILABLE = True
except:
    JNI_AVAILABLE = False
    print("JNI no disponible - modo prueba")


def limpiar_numero(numero):
    """Elimina todo excepto dígitos del número de teléfono"""
    if not numero:
        return ""
    return re.sub(r'\D', '', str(numero))


def obtener_prefijos_bloqueados():
    """Lee la base de datos y devuelve la lista de prefijos/números a bloquear"""
    try:
        if JNI_AVAILABLE:
            db_path = os.path.join(app_storage_path(), 'bloqueador.db')
        else:
            db_path = 'bloqueador.db'

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT prefijo FROM spam")
        prefijos = [row[0] for row in cursor.fetchall()]
        conn.close()
        return prefijos
    except Exception as e:
        print(f"Error leyendo DB: {e}")
        return ['600', '809']


class MiCallScreeningService(PythonJavaClass):
    """Implementación Python del servicio de filtrado de llamadas"""

    __javainterfaces__ = ['android/telecom/CallScreeningService']
    __javacontext__ = 'app'

    @java_method('(Landroid/telecom/Call$Details;)V')
    def onScreenCall(self, call_details):
        try:
            handle = call_details.getHandle()
            if handle is None:
                self.permitir_llamada()
                return

            numero = handle.getSchemeSpecificPart()
            numero_limpio = limpiar_numero(numero)

            print(f"Llamada detectada: {numero_limpio}")

            if self.debe_bloquear(numero_limpio):
                print(f"Bloqueando: {numero_limpio}")
                self.bloquear_llamada()
            else:
                print(f"Permitiendo: {numero_limpio}")
                self.permitir_llamada()

        except Exception as e:
            print(f"Error: {e}")
            self.permitir_llamada()

    def debe_bloquear(self, numero):
        if not numero:
            return False

        prefijos = obtener_prefijos_bloqueados()

        for prefijo in prefijos:
            if numero.startswith(prefijo):
                return True
        return False

    def bloquear_llamada(self):
        try:
            builder = CallResponse.Builder()
            builder.setDisallowCall(True)
            builder.setRejectCall(True)
            builder.setSkipCallLog(True)
            builder.setSkipNotification(True)
            response = builder.build()
            self.respondToCall(None, response)
        except Exception as e:
            print(f"Error bloqueando: {e}")

    def permitir_llamada(self):
        try:
            builder = CallResponse.Builder()
            builder.setDisallowCall(False)
            response = builder.build()
            self.respondToCall(None, response)
        except Exception as e:
            print(f"Error permitiendo: {e}")


print("Servicio CallScreeningService cargado")