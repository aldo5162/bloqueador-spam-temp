[app]
title = Bloqueador Spam
package.name = bloqueador_spam
package.domain = org.bloqueador_sapam.app
source.dir = .
source.include_exts = py,png,jpg,kv,db
version = 1.0

# Requisitos indispensables
requirements = python3,kivy,jnius,sqlite3

# Orientación y pantalla
orientation = portrait
fullscreen = 0

# PERMISOS CRÍTICOS (Para Android 13+)
android.permissions = android.permission.READ_PHONE_STATE, android.permission.ANSWER_PHONE_CALLS, android.permission.MODIFY_PHONE_STATE, android.permission.READ_CALL_LOG, android.permission.FOREGROUND_SERVICE

# Configuración de API para Android 13
android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33

# Registro del servicio de fondo (el que "escucha" las llamadas)
android.services = FiltroSpam:service.py

[buildozer]
log_level = 2
warn_on_root = 1