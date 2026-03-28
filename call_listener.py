"""
Servicio de escucha de llamadas usando BroadcastReceiver
Funciona con solo permiso READ_PHONE_STATE
"""

import sqlite3
import re
import os
from jnius import autoclass, PythonJavaClass, java_method
from kivy.clock import Clock


# Clases Java necesarias
TelephonyManager = autoclass('android.telephony.TelephonyManager')
PythonActivity = autoclass('org.kivy.android.PythonActivity')
Intent = autoclass('android.content.Intent')
IntentFilter = autoclass('android.content.IntentFilter')


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


class CallReceiver(PythonJavaClass):
    """BroadcastReceiver para detectar llamadas entrantes"""

    __javainterfaces__ = ['android/content/BroadcastReceiver']
    __javacontext__ = 'app'

    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    @java_method('(Landroid/content/Context;Landroid/content/Intent;)V')
    def onReceive(self, context, intent):
        """Método llamado cuando se recibe una transmisión"""
        try:
            if intent.getAction() == TelephonyManager.ACTION_PHONE_STATE_CHANGED:
                state = intent.getStringExtra(TelephonyManager.EXTRA_STATE)
                if state == TelephonyManager.EXTRA_STATE_RINGING:
                    # Llamada entrante
                    incoming_number = intent.getStringExtra(TelephonyManager.EXTRA_INCOMING_NUMBER)
                    numero_limpio = limpiar_numero(incoming_number)
                    print(f"Llamada entrante detectada: {numero_limpio}")

                    if debe_bloquear(numero_limpio):
                        print(f"⚠️ NÚMERO BLOQUEADO: {numero_limpio}")
                        self.callback(numero_limpio, True)
                    else:
                        print(f"✓ Número permitido: {numero_limpio}")
                        self.callback(numero_limpio, False)
        except Exception as e:
            print(f"Error en onReceive: {e}")


class CallListener:
    """Clase principal para iniciar el listener de llamadas"""

    def __init__(self, mostrar_notificacion_callback):
        self.receiver = None
        self.iniciado = False
        self.mostrar_notificacion = mostrar_notificacion_callback

    def iniciar(self):
        """Inicia el listener de llamadas"""
        if self.iniciado:
            print("Listener ya estaba iniciado")
            return True

        try:
            # Obtener la actividad actual
            current_activity = PythonActivity.mActivity

            # Crear el receiver
            self.receiver = CallReceiver(self.on_call_detected)

            # Crear el filtro para llamadas
            intent_filter = IntentFilter()
            intent_filter.addAction(TelephonyManager.ACTION_PHONE_STATE_CHANGED)

            # Registrar el receiver
            current_activity.registerReceiver(self.receiver, intent_filter)

            self.iniciado = True
            print("✅ CallListener iniciado correctamente con BroadcastReceiver")
            return True

        except Exception as e:
            print(f"❌ Error iniciando CallListener: {e}")
            return False

    def detener(self):
        """Detiene el listener de llamadas"""
        if self.receiver and self.iniciado:
            try:
                current_activity = PythonActivity.mActivity
                current_activity.unregisterReceiver(self.receiver)
                self.iniciado = False
                print("CallListener detenido")
            except Exception as e:
                print(f"Error deteniendo: {e}")

    def on_call_detected(self, numero, bloqueado):
        """Callback cuando se detecta una llamada"""
        if bloqueado:
            Clock.schedule_once(
                lambda dt: self.mostrar_notificacion(
                    "🚫 LLAMADA BLOQUEADA",
                    f"Número: {numero}\nPrefijo bloqueado"
                ),
                0
            )
        else:
            print(f"Llamada permitida: {numero}")


# Instancia global
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