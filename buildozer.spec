[app]
title = ShoonyaOne
package.name = shoonyaone
package.domain = org.shoonya
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,html,css,js
version = 2.0.0
requirements = python3,kivy,google-genai,requests,colorama

orientation = portrait
fullscreen = 0
android.permissions = INTERNET,ACCESS_NETWORK_STATE,CAMERA,RECORD_AUDIO,FLASHLIGHT,VIBRATE,SEND_SMS,READ_CONTACTS,CALL_PHONE

# Android API & NDK settings
android.api = 34
android.minapi = 26
android.ndk = 25b
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
