[app]

title = Nova Link
package.name = novalink
package.domain = org.novatech

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 0.1

requirements = python3,kivy==2.3.0,kivymd==1.1.1,pillow

orientation = portrait
fullscreen = 0

android.permissions = INTERNET

android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
android.archs = arm64-v8a, armeabi-v7a

p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 1
