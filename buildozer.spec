[app]

title = Bloqueador Spam
package.name = bloqueador_spam
package.domain = org.bloqueador_spam.app

source.dir = .
source.include_exts = py,png,jpg,kv,db

version = 1.0.0

# Usar versiones específicas que funcionan bien juntas
requirements = python3==3.10.0, kivy==2.1.0, pyjnius==1.4.0, sqlite3, cython==0.29.36

orientation = portrait
fullscreen = 0

# Permisos mínimos necesarios para CallScreeningService
android.permissions = android.permission.READ_PHONE_STATE

# API level 33 = Android 13
android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33

# Forzar una versión específica de build-tools
android.build_tools = 33.0.2

# Servicio de filtrado de llamadas
android.add_services = service.py

# Metadatos para que Android reconozca el servicio como CallScreeningService
android.gradle_dependencies = 'androidx.core:core:1.9.0'

# Configuración adicional para pyjnius
android.ndk_shared = False

[buildozer]

log_level = 2
warn_on_root = 1