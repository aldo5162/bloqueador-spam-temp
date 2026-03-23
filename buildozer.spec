[app]

title = Bloqueador Spam
package.name = bloqueador_spam
package.domain = org.bloqueador_spam.app

source.dir = .
source.include_exts = py,png,jpg,kv,db

version = 1.0.0

requirements = python3,kivy,pyjnius,sqlite3

orientation = portrait
fullscreen = 0

# Permisos mínimos necesarios para CallScreeningService
android.permissions = android.permission.READ_PHONE_STATE

# API level 33 = Android 13
android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33

# Forzar una versión específica de build-tools (estable)
android.build_tools = 33.0.2

# Servicio de filtrado de llamadas
android.add_services = service.py

# Forzar versión de libffi para evitar errores en Ubuntu 24.04
android.ndk_shared = False
android.allow_ndk_ffi = True

# Metadatos para que Android reconozca el servicio como CallScreeningService
android.gradle_dependencies = 'androidx.core:core:1.9.0'

[buildozer]

log_level = 2
warn_on_root = 1