import sqlite3
import re
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout


class BloqueadorApp(App):
    def build(self):
        self.init_db()

        # --- NUEVO: ESTO DESPIERTA EL SERVICIO EN ANDROID ---
        from kivy.utils import platform
        if platform == 'android':
            try:
                from jnius import autoclass
                # IMPORTANTE: Reemplaza 'tu_nombre' por el que pusiste en buildozer.spec
                # La ruta se forma: org.dominio.nombreapp.ServiceNombreServicio
                service_name = 'org.tu_nombre.bloqueador_spam.ServiceFiltrospam'
                service = autoclass(service_name)
                mActivity = autoclass('org.kivy.android.PythonActivity').mActivity
                service.start(mActivity, "")
                print("Servicio de Bloqueo despertado con éxito")
            except Exception as e:
                print(f"Error al iniciar el guardia de fondo: {e}")
        # ----------------------------------------------------

        # Layout principal
        self.main_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        # Título e Instrucciones
        self.main_layout.add_widget(Label(text="[b]FILTRO DE SPAM[/b]", markup=True, size_hint_y=None, height=50))

        # Entrada de número
        self.input_num = TextInput(hint_text="Ej: 809 o 600", multiline=False, size_hint_y=None, height=100)
        self.main_layout.add_widget(self.input_num)

        # Botón agregar
        btn_add = Button(text="BLOQUEAR ESTE PREFIJO", background_color=(0.9, 0.1, 0.1, 1), size_hint_y=None,
                         height=100)
        btn_add.bind(on_press=self.agregar_a_db)
        self.main_layout.add_widget(btn_add)

        # Lista de números bloqueados (Scroll)
        self.scroll = ScrollView()
        self.lista_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.lista_layout.bind(minimum_height=self.lista_layout.setter('height'))
        self.actualizar_lista_visual()

        self.scroll.add_widget(self.lista_layout)
        self.main_layout.add_widget(self.scroll)

        return self.main_layout

    def init_db(self):
        self.conn = sqlite3.connect('bloqueador.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS spam (prefijo TEXT UNIQUE)''')
        # Insertar valores por defecto
        try:
            self.cursor.executemany("INSERT INTO spam VALUES (?)", [('600',), ('809',)])
            self.conn.commit()
        except:
            pass

    def agregar_a_db(self, instance):
        # Limpieza con RegEx: quita (), -, espacios, etc.
        num_limpio = re.sub(r'\D', '', self.input_num.text)
        if num_limpio:
            try:
                self.cursor.execute("INSERT INTO spam VALUES (?)", (num_limpio,))
                self.conn.commit()
                self.actualizar_lista_visual()
                self.input_num.text = ""
            except:
                pass

    def actualizar_lista_visual(self):
        self.lista_layout.clear_widgets()
        self.cursor.execute("SELECT prefijo FROM spam")
        for (p,) in self.cursor.fetchall():
            self.lista_layout.add_widget(Label(text=f"Bloqueado: {p}", size_hint_y=None, height=40))


if __name__ == '__main__':
    BloqueadorApp().run()