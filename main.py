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


class BloqueadorApp(App):
    def build(self):
        self.init_db()

        # Si estamos en Android, solicitamos el rol de filtrado
        if platform == 'android':
            Clock.schedule_once(self.solicitar_rol_filtrado, 1)

        # Layout principal
        self.main_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        # Título
        self.main_layout.add_widget(Label(
            text="[b]BLOQUEADOR DE SPAM[/b]\n[small]Llama 600 y 809 bloqueadas[/small]",
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

        # Botón para verificar estado del rol
        btn_estado = Button(
            text="VERIFICAR PERMISO DE FILTRADO",
            size_hint_y=None,
            height=80
        )
        btn_estado.bind(on_press=self.verificar_rol)
        self.main_layout.add_widget(btn_estado)

        return self.main_layout

    def init_db(self):
        self.conn = sqlite3.connect('bloqueador.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS spam (
            prefijo TEXT UNIQUE,
            fecha_agregado TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        # Insertar valores por defecto (600 y 809)
        for prefijo in ['600', '809']:
            try:
                self.cursor.execute("INSERT INTO spam (prefijo) VALUES (?)", (prefijo,))
            except:
                pass
        self.conn.commit()

    def agregar_a_db(self, instance):
        num_limpio = re.sub(r'\D', '', self.input_num.text)
        if num_limpio and len(num_limpio) >= 3:
            try:
                self.cursor.execute("INSERT INTO spam (prefijo) VALUES (?)", (num_limpio,))
                self.conn.commit()
                self.actualizar_lista_visual()
                self.input_num.text = ""
                self.mostrar_mensaje("Agregado", f"{num_limpio} será bloqueado")
            except sqlite3.IntegrityError:
                self.mostrar_mensaje("Ya existe", f"{num_limpio} ya está en la lista")
        else:
            self.mostrar_mensaje("Error", "Ingresa al menos 3 dígitos")

    def actualizar_lista_visual(self):
        self.lista_layout.clear_widgets()
        self.cursor.execute("SELECT prefijo FROM spam ORDER BY prefijo")
        for (p,) in self.cursor.fetchall():
            # Layout horizontal para cada ítem
            item_layout = BoxLayout(size_hint_y=None, height=60)

            # Label con el prefijo/número
            lbl = Label(text=f"🔴 {p}", size_hint_x=0.7)

            # Botón eliminar
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
        """Elimina un prefijo/número de la lista de bloqueados"""
        self.cursor.execute("DELETE FROM spam WHERE prefijo = ?", (prefijo,))
        self.conn.commit()
        self.actualizar_lista_visual()
        self.mostrar_mensaje("Eliminado", f"{prefijo} ya no será bloqueado")

    def mostrar_mensaje(self, titulo, mensaje):
        popup = Popup(
            title=titulo,
            content=Label(text=mensaje),
            size_hint=(0.8, 0.4)
        )
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), 2)

    def solicitar_rol_filtrado(self, dt):
        """Solicita al usuario que active la app como filtro de llamadas"""
        if platform == 'android':
            try:
                from jnius import autoclass
                from android import activity

                Context = autoclass('android.content.Context')
                RoleManager = autoclass('android.app.role.RoleManager')

                role_manager = activity.getSystemService(Context.ROLE_SERVICE)

                if role_manager.isRoleAvailable(RoleManager.ROLE_CALL_SCREENING):
                    if not role_manager.isRoleHeld(RoleManager.ROLE_CALL_SCREENING):
                        intent = role_manager.createRequestRoleIntent(RoleManager.ROLE_CALL_SCREENING)
                        activity.startActivityForResult(intent, 1001)
            except Exception as e:
                print(f"Error al solicitar rol: {e}")

    def verificar_rol(self, instance):
    """Verifica si la app tiene el rol de filtrado activado"""
    if platform == 'android':
        try:
            from jnius import autoclass
            from android import activity
            
            Context = autoclass('android.content.Context')
            RoleManager = autoclass('android.app.role.RoleManager')
            
            role_manager = activity.getSystemService(Context.ROLE_SERVICE)
            
            if role_manager.isRoleHeld(RoleManager.ROLE_CALL_SCREENING):
                self.mostrar_mensaje("✅ Activado", "La app tiene permiso para filtrar llamadas")
            else:
                self.mostrar_mensaje("⚠️ No activado", "Debes otorgar el permiso de filtrado en Configuración")
                
                # Intentar abrir la configuración de permisos especiales
                intent = role_manager.createRequestRoleIntent(RoleManager.ROLE_CALL_SCREENING)
                activity.startActivityForResult(intent, 1001)
                
        except Exception as e:
            self.mostrar_mensaje("Error", f"No se pudo verificar: {e}")
            print(f"Error: {e}")
    else:
        self.mostrar_mensaje("Solo Android", "Esta función solo está disponible en Android")


if __name__ == '__main__':
    BloqueadorApp().run()
