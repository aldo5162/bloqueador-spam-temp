[app]

title = Bloqueador Spam
package.name = bloqueador_spam
package.domain = org.bloqueador_spam.app

source.dir = .
source.include_exts = py,png,jpg,kv,db,spec

version = 1.0.0

requirements = python3, kivy==2.1.0, pyjnius==1.4.0, sqlite3, cython==0.29.36

orientation = portrait
fullscreen = 0

icon = icon.png

android.permissions = READ_PHONE_STATE

android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33
android.build_tools = 33.0.0

android.accept_sdk_license = True

[buildozer]

log_level = 2
warn_on_root = 1