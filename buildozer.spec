[app]

title = Bloqueador Spam
package.name = bloqueador_spam
package.domain = org.bloqueador_spam.app

source.dir = .
source.include_exts = py,png,jpg,kv,db

version = 1.0.0

requirements = python3, kivy==2.1.0, pyjnius==1.4.0, sqlite3, cython==0.29.36

orientation = portrait
fullscreen = 0

android.permissions = android.permission.READ_PHONE_STATE

android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33
android.build_tools = 30.0.3

# Servicio de filtrado de llamadas
android.add_services = service.py

# Permiso necesario para CallScreeningService
android.gradle_dependencies = androidx.core:core:1.9.0

[buildozer]

log_level = 2
warn_on_root = 1