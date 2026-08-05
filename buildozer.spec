[app]
title = Intervals Trainer
package.name = intervaltrainer
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,mp3,json
source.include_patterns = musik/*
version = 0.1
requirements = python3,kivy,android
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

android.api = 33
android.minapi = 21
android.ndk_api = 21
android.ndk = 25b
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
