"""
Servicio de escucha de llamadas usando PhoneStateListener
Funciona con solo permiso READ_PHONE_STATE
"""

import sqlite3
import re
import os
from jnius import autoclass, PythonJavaClass, java_method
from kivy.clock import Clock

# Clases Java necesarias
TelephonyManager = autoclass('android.telephony.TelephonyManager')
PhoneStateListener = autoclass('android.telephony.PhoneStateListener')
PythonActivity = autoclass('org.kivy.android.PythonActivity')


def limpiar_numero(numero):
    """Elimina todo excepto dígitos del número de teléfono"""
    if not numero:
        return ""
    return re.sub(r'\D', '', str(numero))


def obtener_prefijos_bloqueados():
    """Lee la base de datos y devuelve la lista de prefijos/números a bloquear"""
    try:
        from android.storage import app_storage_path
        db_path = os.path.join(app_storage_path(), 'bloqueador.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT prefijo FROM spam")
        prefijos = [row[0] for row in cursor.fetchall()]
        conn.close()
        return prefijos
    except Exception as e:
        print(f"Error leyendo DB: {e}")
        return ['600', '809']


def debe_bloquear(numero):
    """Determina si el número debe ser bloqueado"""
    if not numero:
        return False
    prefijos = obtener_prefijos_bloqueados()
    for prefijo in prefijos:
        if numero.startswith(prefijo):
            return True
    return False


class MiPhoneStateListener(PythonJavaClass):
    """Escucha el estado del teléfono para detectar llamadas entrantes"""

    __javainterfaces__ = ['android/telephony/PhoneStateListener']
    __javacontext__ = 'app'

    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    @java_method('(ILjava/lang/String;)V')
    def onCallStateChanged(self, state, phoneNumber):
        """Método llamado cuando cambia el estado de la llamada"""
        if state == TelephonyManager.CALL_STATE_RINGING:
            # Llamada entrante
            numero_limpio = limpiar_numero(phoneNumber)
            print(f"Llamada entrante detectada: {numero_limpio}")

            if debe_bloquear(numero_limpio):
                print(f"⚠️ NÚMERO BLOQUEADO: {numero_limpio}")
                self.callback(numero_limpio, True)
            else:
                print(f"✓ Número permitido: {numero_limpio}")
                self.callback(numero_limpio, False)


class CallListener:
    """Clase principal para iniciar el listener de llamadas"""

    def __init__(self, mostrar_notificacion_callback):
        self.listener = None
        self.telephony_manager = None
        self.mostrar_notificacion = mostrar_notificacion_callback
        self.iniciado = False

    def iniciar(self):
        """Inicia el listener de llamadas"""
        if self.iniciado:
            print("Listener ya estaba iniciado")
            return True

        try:
            # Obtener la actividad actual
            current_activity = PythonActivity.mActivity

            # Obtener el servicio de telefonía
            self.telephony_manager = current_activity.getSystemService(
                current_activity.TELEPHONY_SERVICE
            )

            # Crear el listener
            self.listener = MiPhoneStateListener(self.on_call_detected)

            # Registrar el listener
            self.telephony_manager.listen(
                self.listener,
                PhoneStateListener.LISTEN_CALL_STATE
            )

            self.iniciado = True
            print("✅ CallListener iniciado correctamente")
            return True

        except Exception as e:
            print(f"❌ Error iniciando CallListener: {e}")
            return False

    def detener(self):
        """Detiene el listener de llamadas"""
        if self.listener and self.telephony_manager:
            self.telephony_manager.listen(self.listener, 0)
            self.iniciado = False
            print("CallListener detenido")

    def on_call_detected(self, numero, bloqueado):
        """Callback cuando se detecta una llamada"""
        if bloqueado:
            # Mostrar notificación en la UI (desde el hilo principal)
            Clock.schedule_once(
                lambda dt: self.mostrar_notificacion(
                    "🚫 LLAMADA BLOQUEADA",
                    f"Número: {numero}\nPrefijo bloqueado"
                ),
                0
            )
        else:
            print(f"Llamada permitida: {numero}")


# Instancia global para usar desde main.py
_call_listener_instance = None


def iniciar_call_listener(mostrar_notificacion_callback):
    """Función global para iniciar el listener"""
    global _call_listener_instance
    if _call_listener_instance is None:
        _call_listener_instance = CallListener(mostrar_notificacion_callback)
    return _call_listener_instance.iniciar()


def detener_call_listener():
    """Función global para detener el listener"""
    global _call_listener_instance
    if _call_listener_instance:
        _call_listener_instance.detener()
        _call_listener_instance = None


def call_listener_activo():
    """Verifica si el listener está activo"""
    global _call_listener_instance
    return _call_listener_instance is not None and _call_listener_instance.iniciado