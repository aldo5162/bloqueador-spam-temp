import sqlite3
import re
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.utils import platform

# Importar el listener de llamadas
from call_listener import iniciar_call_listener, detener_call_listener, call_listener_activo


class BloqueadorApp(App):
    def build(self):
        self.init_db()

        # Crear layout principal
        self.main_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        # Título
        self.main_layout.add_widget(Label(
            text="[b]BLOQUEADOR DE SPAM[/b]\n[small]Bloquea llamadas 600 y 809[/small]",
            markup=True,
            size_hint_y=None,
            height=80
        ))

        # Entrada de número
        self.input_num = TextInput(
            hint_text="Ej: 600 o 809 o 912345678",
            multiline=False,
            size_hint_y=None,
            height=80
        )
        self.main_layout.add_widget(self.input_num)

        # Botón agregar
        btn_add = Button(
            text="BLOQUEAR ESTE PREFIJO/NÚMERO",
            background_color=(0.9, 0.2, 0.2, 1),
            size_hint_y=None,
            height=80
        )
        btn_add.bind(on_press=self.agregar_a_db)
        self.main_layout.add_widget(btn_add)

        # Separador
        self.main_layout.add_widget(Label(
            text="Prefijos y números bloqueados:",
            size_hint_y=None,
            height=40
        ))

        # Lista de números bloqueados
        self.scroll = ScrollView()
        self.lista_layout = GridLayout(cols=1, spacing=8, size_hint_y=None)
        self.lista_layout.bind(minimum_height=self.lista_layout.setter('height'))
        self.actualizar_lista_visual()

        self.scroll.add_widget(self.lista_layout)
        self.main_layout.add_widget(self.scroll)

        # Botón para verificar estado del servicio
        btn_estado = Button(
            text="VERIFICAR SERVICIO DE ESCUCHA",
            size_hint_y=None,
            height=80
        )
        btn_estado.bind(on_press=self.verificar_servicio)
        self.main_layout.add_widget(btn_estado)

        # Botón para reiniciar servicio (por si falla)
        btn_reiniciar = Button(
            text="REINICIAR SERVICIO DE ESCUCHA",
            size_hint_y=None,
            height=60,
            background_color=(0.3, 0.5, 0.7, 1)
        )
        btn_reiniciar.bind(on_press=self.reiniciar_servicio)
        self.main_layout.add_widget(btn_reiniciar)

        # Iniciar el listener de llamadas si estamos en Android
        if platform == 'android':
            Clock.schedule_once(lambda dt: self.iniciar_listener_llamadas(), 2)

        return self.main_layout

    def init_db(self):
        """Inicializa la base de datos con los prefijos por defecto"""
        self.conn = sqlite3.connect('bloqueador.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS spam (
            prefijo TEXT UNIQUE,
            fecha_agregado TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        for prefijo in ['600', '809']:
            try:
                self.cursor.execute("INSERT INTO spam (prefijo) VALUES (?)", (prefijo,))
            except:
                pass
        self.conn.commit()

    def agregar_a_db(self, instance):
        """Agrega un nuevo prefijo o número a bloquear"""
        num_limpio = re.sub(r'\D', '', self.input_num.text)
        if num_limpio and len(num_limpio) >= 3:
            try:
                self.cursor.execute("INSERT INTO spam (prefijo) VALUES (?)", (num_limpio,))
                self.conn.commit()
                self.actualizar_lista_visual()
                self.input_num.text = ""
                self.mostrar_mensaje("✓ Agregado", f"{num_limpio}\nserá bloqueado")
            except sqlite3.IntegrityError:
                self.mostrar_mensaje("⚠️ Ya existe", f"{num_limpio}\nya está en la lista")
        else:
            self.mostrar_mensaje("❌ Error", "Ingresa al menos\n3 dígitos")

    def actualizar_lista_visual(self):
        """Actualiza la lista visual de números bloqueados"""
        self.lista_layout.clear_widgets()
        self.cursor.execute("SELECT prefijo FROM spam ORDER BY prefijo")
        for (p,) in self.cursor.fetchall():
            item_layout = BoxLayout(size_hint_y=None, height=60)
            lbl = Label(text=f"🔴 {p}", size_hint_x=0.7)
            btn_eliminar = Button(
                text="ELIMINAR",
                size_hint_x=0.3,
                background_color=(0.8, 0.2, 0.2, 1)
            )
            btn_eliminar.bind(on_press=lambda inst, pref=p: self.eliminar_prefijo(pref))
            item_layout.add_widget(lbl)
            item_layout.add_widget(btn_eliminar)
            self.lista_layout.add_widget(item_layout)

    def eliminar_prefijo(self, prefijo):
        """Elimina un prefijo de la lista de bloqueados"""
        self.cursor.execute("DELETE FROM spam WHERE prefijo = ?", (prefijo,))
        self.conn.commit()
        self.actualizar_lista_visual()
        self.mostrar_mensaje("🗑️ Eliminado", f"{prefijo}\nya no será bloqueado")

    def mostrar_mensaje(self, titulo, mensaje):
        """Muestra un mensaje emergente"""
        popup = Popup(
            title=titulo,
            content=Label(
                text=mensaje,
                halign='center',
                valign='middle',
                text_size=(self.main_layout.width * 0.8, None)
            ),
            size_hint=(0.85, 0.4),
            title_size=18,
            title_align='center'
        )
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), 3)

    def iniciar_listener_llamadas(self):
        """Inicia el listener de llamadas en segundo plano"""
        if platform == 'android':
            resultado = iniciar_call_listener(self.mostrar_notificacion_bloqueo)
            if resultado:
                print("✅ Listener de llamadas iniciado")
                self.mostrar_mensaje("✅ Servicio activo", "La app está escuchando\nllamadas entrantes")
            else:
                print("❌ Error al iniciar listener")
                self.mostrar_mensaje("❌ Error", "No se pudo iniciar\nel servicio de escucha")

    def detener_listener_llamadas(self):
        """Detiene el listener de llamadas"""
        if platform == 'android':
            detener_call_listener()
            print("Listener de llamadas detenido")

    def reiniciar_servicio(self, instance):
        """Reinicia el servicio de escucha de llamadas"""
        if platform == 'android':
            self.mostrar_mensaje("🔄 Reiniciando", "Deteniendo y reiniciando\nel servicio...")
            self.detener_listener_llamadas()
            Clock.schedule_once(lambda dt: self.iniciar_listener_llamadas(), 1)

    def verificar_servicio(self, instance):
        """Verifica si el servicio de escucha está activo"""
        if platform == 'android':
            if call_listener_activo():
                self.mostrar_mensaje("✅ Servicio activo", "La app está escuchando\nllamadas entrantes")
            else:
                self.mostrar_mensaje("⚠️ Servicio inactivo", "El servicio no está activo\nPresiona REINICIAR")
        else:
            self.mostrar_mensaje("📱 Solo Android", "Esta función solo está\ndisponible en Android")

    def mostrar_notificacion_bloqueo(self, titulo, mensaje):
        """Muestra una notificación de bloqueo (desde el hilo principal)"""
        self.mostrar_mensaje(titulo, mensaje)


if __name__ == '__main__':
    BloqueadorApp().run()