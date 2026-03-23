[app]

title = Bloqueador Spam
package.name = bloqueador_spam
package.domain = org.bloqueador_spam.app

source.dir = .
source.include_exts = py,png,jpg,kv,db

version = 1.0.0

requirements = python3==3.10.0,kivy,pyjnius,sqlite3

orientation = portrait
fullscreen = 0

android.permissions = android.permission.READ_PHONE_STATE

android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33
android.build_tools = 33.0.2

android.add_services = service.py

# Temporalmente comentada para evitar error de sintaxis en build.gradle
# android.gradle_dependencies = 'androidx.core:core:1.9.0'

[buildozer]

log_level = 2
warn_on_root = 1
