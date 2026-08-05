import os
import json
import random
import time
from kivy.core.audio import SoundLoader

noti_sugranni = {}

SOUNDS_DIR = "musik"

files_list = [
    "C1.mp3", "D1.mp3", "E1.mp3", "F1.mp3", "G1.mp3", "H1.mp3", "B1.mp3",
    "C#1.mp3", "D#1.mp3", "F#1.mp3", "G#1.mp3", "H#1.mp3",
    "C2.mp3", "D2.mp3", "E2.mp3", "F2.mp3", "G2.mp3", "H2.mp3", "B2.mp3",
    "C#2.mp3", "D#2.mp3", "F#2.mp3", "G#2.mp3", "H#2.mp3"
]

files_list_no_diez = [
    "C1.mp3", "D1.mp3", "E1.mp3", "F1.mp3", "G1.mp3", "H1.mp3", "B1.mp3",
    "C2.mp3", "D2.mp3", "E2.mp3", "F2.mp3", "G2.mp3", "H2.mp3", "B2.mp3",
]

def _storage_path(name):
    """На Android пишем в app_storage, на ПК — рядом со скриптом."""
    try:
        from android.storage import app_storage_path
        return os.path.join(app_storage_path(), name)
    except ImportError:
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), name)

def _musik_path(filename):
    base = os.path.dirname(os.path.abspath(__file__))
    p = os.path.join(base, SOUNDS_DIR, filename)
    if os.path.exists(p):
        return p
    return os.path.join(SOUNDS_DIR, filename)

def _play_and_wait(snd1, snd2):
    snd1.play()
    snd2.play()
    while snd1.state == 'play' or snd2.state == 'play':
        time.sleep(0.1)

def play_random_notu():
    p = _musik_path(random.choice(files_list))
    s = SoundLoader.load(p)
    if s:
        s.play()
        while s.state == 'play':
            time.sleep(0.1)

def play_two_random_nots():
    p1 = _musik_path(random.choice(files_list))
    p2 = _musik_path(random.choice(files_list))
    s1 = SoundLoader.load(p1)
    s2 = SoundLoader.load(p2)
    if s1 and s2:
        _play_and_wait(s1, s2)

def play_two_random_nots_type(type):
    namber1 = random.randint(0, 23)
    namber2 = namber1 + type
    if namber2 > 23:
        namber2 = namber2 - 23
    p1 = _musik_path(files_list[namber1])
    p2 = _musik_path(files_list[namber2])
    s1 = SoundLoader.load(p1)
    s2 = SoundLoader.load(p2)
    if s1 and s2:
        _play_and_wait(s1, s2)
    noti_sugranni['нота1'] = files_list[namber1]
    noti_sugranni['нота2'] = files_list[namber2]
    with open(_storage_path('note_save.json'), 'w', encoding='utf-8') as f:
        json.dump(noti_sugranni, f, ensure_ascii=False, indent=4)

def play_random_notu_no_diez():
    p = _musik_path(random.choice(files_list_no_diez))
    s = SoundLoader.load(p)
    if s:
        s.play()
        while s.state == 'play':
            time.sleep(0.1)

def play_two_random_nots_type_no_diez(type):
    namber1 = random.randint(0, 13)
    namber2 = namber1 + type
    if namber2 > 13:
        namber2 = namber2 - 13
    p1 = _musik_path(files_list_no_diez[namber1])
    p2 = _musik_path(files_list_no_diez[namber2])
    s1 = SoundLoader.load(p1)
    s2 = SoundLoader.load(p2)
    if s1 and s2:
        _play_and_wait(s1, s2)
    noti_sugranni['нота1'] = files_list_no_diez[namber1]
    noti_sugranni['нота2'] = files_list_no_diez[namber2]
    with open(_storage_path('note_save.json'), 'w', encoding='utf-8') as f:
        json.dump(noti_sugranni, f, ensure_ascii=False, indent=4)

def play_two_random_nots_no_diez():
    p1 = _musik_path(random.choice(files_list_no_diez))
    p2 = _musik_path(random.choice(files_list_no_diez))
    s1 = SoundLoader.load(p1)
    s2 = SoundLoader.load(p2)
    if s1 and s2:
        _play_and_wait(s1, s2)

def play_two_nots(nota1, nota2):
    p1 = _musik_path(nota1)
    p2 = _musik_path(nota2)
    s1 = SoundLoader.load(p1)
    s2 = SoundLoader.load(p2)
    if s1 and s2:
        _play_and_wait(s1, s2)

def play_notu(nota):
    p = _musik_path(nota)
    s = SoundLoader.load(p)
    if s:
        s.play()
        while s.state == 'play':
            time.sleep(0.1)

def remember():
    with open(_storage_path('note_save.json'), 'r', encoding='utf-8') as f:
        data = json.load(f)
    p1 = _musik_path(data['нота1'])
    p2 = _musik_path(data['нота2'])
    s1 = SoundLoader.load(p1)
    s2 = SoundLoader.load(p2)
    if s1 and s2:
        _play_and_wait(s1, s2)