from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.metrics import dp
from kivy.core.window import Window
import json
import os
import random
import datetime
import threading
import audio

# ========== ТЕМА ==========
Window.clearcolor = (0.05, 0.05, 0.08, 1)
ACCENT   = (0.25, 0.65, 0.95, 1)
SUCCESS  = (0.20, 0.80, 0.45, 1)
DANGER   = (0.90, 0.30, 0.35, 1)
WARNING  = (0.95, 0.70, 0.20, 1)
BG_CARD  = (0.10, 0.10, 0.14, 1)
BG_ITEM  = (0.13, 0.13, 0.18, 1)
TEXT_M   = (0.85, 0.85, 0.90, 1)

# ========== ГЛОБАЛЬНЫЕ НАСТРОЙКИ ==========
best_record = 5
noti_pravilnie = {}
test_nomer = 0
maxtest = 3
correct_count = 0
wrong_count = 0

nastroiki = {
    "primi": False, "secunda": False, "tercia": False,
    "cvarta": False, "cvinta": False, "secsta": False, "septima": False
}

INTERVALS = ["прима", "секунда", "терция", "кварта", "квинта", "секста", "септима"]
NASTROIKI_KEYS = ["primi", "secunda", "tercia", "cvarta", "cvinta", "secsta", "septima"]

# ========== УТИЛИТЫ ==========
def data_dir():
    try:
        from android.storage import app_storage_path
        return app_storage_path()
    except ImportError:
        return os.path.dirname(os.path.abspath(__file__))

def jpath(name):
    return os.path.join(data_dir(), name)

def save_results(correct, total):
    path = jpath("results_history.json")
    hist = []
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                hist = json.load(f)
        except:
            pass
    hist.append({
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "correct": correct,
        "total": total
    })
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(hist, f, ensure_ascii=False, indent=4)

def load_history():
    path = jpath("results_history.json")
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return []

def save_history(hist):
    with open(jpath("results_history.json"), 'w', encoding='utf-8') as f:
        json.dump(hist, f, ensure_ascii=False, indent=4)

def styled_popup(title, msg, on_ok=None):
    box = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
    box.add_widget(Label(text=msg, halign='center', color=TEXT_M, font_size='16sp'))
    btn = RoundedButton(text="OK", size_hint_y=None, height=dp(50), bg_color=ACCENT)
    box.add_widget(btn)
    p = Popup(
        title=title, content=box, size_hint=(0.85, 0.35), auto_dismiss=False,
        title_color=TEXT_M, separator_color=ACCENT,
        background_color=(0.06, 0.06, 0.10, 0.98)
    )
    btn.bind(on_release=p.dismiss)
    if on_ok:
        p.bind(on_dismiss=lambda x: on_ok())
    p.open()

# ========== КАСТОМНЫЕ ВИДЖЕТЫ ==========
class RoundedButton(Button):
    def __init__(self, bg_color=ACCENT, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.color = (1, 1, 1, 1)
        self.bold = True
        self.font_size = '16sp'
        with self.canvas.before:
            Color(*bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(18)])
        self.bind(pos=self._upd, size=self._upd)

    def _upd(self, *a):
        self.rect.pos = self.pos
        self.rect.size = self.size

class BgBoxLayout(BoxLayout):
    def __init__(self, bg_color=BG_CARD, radius=[dp(20)], **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=radius)
        self.bind(pos=self._upd, size=self._upd)

    def _upd(self, *a):
        self.rect.pos = self.pos
        self.rect.size = self.size

class StyledInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_active = ''
        self.background_color = BG_ITEM
        self.foreground_color = (1, 1, 1, 1)
        self.cursor_color = ACCENT
        self.halign = 'center'
        self.multiline = False
        self.font_size = '18sp'
        self.padding_y = [dp(10), dp(10)]

class IntervalRow(BgBoxLayout):
    def __init__(self, name, key, **kwargs):
        super().__init__(
            bg_color=BG_ITEM, radius=[dp(12)],
            size_hint_y=None, height=dp(55),
            padding=dp(10), **kwargs
        )
        self.cb = CheckBox(size_hint_x=None, width=dp(40))
        self.cb.active = nastroiki[key]
        self.add_widget(self.cb)
        self.add_widget(Label(
            text=name.capitalize(),
            color=TEXT_M, font_size='16sp', halign='left'
        ))

# ========== БАЗОВЫЙ ЭКРАН С ФОНОМ ==========
class BaseScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        with self.canvas.before:
            Color(0.05, 0.05, 0.08, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._upd_bg, size=self._upd_bg)

    def _upd_bg(self, *a):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

# ========== ЭКРАНЫ ==========
class StartScreen(BaseScreen):
    def __init__(self, **kw):
        super().__init__(**kw)
        anchor = AnchorLayout(padding=dp(20))
        root = BoxLayout(orientation='vertical', spacing=dp(15), size_hint=(0.95, 0.92))

        root.add_widget(Label(
            text="🎵  Потренируемся?",
            font_size='32sp', bold=True, color=ACCENT,
            size_hint_y=None, height=dp(60)
        ))
        root.add_widget(Label(
            text="Выберите интервалы для тренировки",
            font_size='14sp', color=(0.6, 0.6, 0.7, 1),
            size_hint_y=None, height=dp(25)
        ))

        card = BgBoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        grid = GridLayout(cols=2, spacing=dp(10), size_hint_y=None)
        self.checks = {}
        rows = []
        for key, name in zip(NASTROIKI_KEYS, INTERVALS):
            row = IntervalRow(name, key)
            self.checks[key] = row.cb
            rows.append(row)
        grid.height = dp(len(rows) * 65)
        for r in rows:
            grid.add_widget(r)
        card.add_widget(grid)

        row_q = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(15), padding=[0, dp(10), 0, 0])
        row_q.add_widget(Label(text="Вопросов:", color=TEXT_M, font_size='16sp', size_hint_x=None, width=dp(120)))
        self.inp = StyledInput(text="3", input_filter='int', size_hint_x=None, width=dp(80))
        row_q.add_widget(self.inp)
        row_q.add_widget(Label())
        card.add_widget(row_q)
        root.add_widget(card)

        btns = BoxLayout(orientation='vertical', spacing=dp(12), size_hint_y=None, height=dp(220))
        btns.add_widget(RoundedButton(text="▶  Начать тест", bg_color=SUCCESS, on_press=self.start))
        btns.add_widget(RoundedButton(text="📊  Статистика", bg_color=(0.35, 0.45, 0.75, 1), on_press=self.open_stats))
        btns.add_widget(RoundedButton(text="ℹ️  О программе", bg_color=(0.45, 0.45, 0.55, 1), on_press=lambda x: setattr(self.manager, 'current', 'about')))
        btns.add_widget(RoundedButton(text="✖  Выход", bg_color=DANGER, on_press=lambda x: App.get_running_app().stop()))
        root.add_widget(btns)

        anchor.add_widget(root)
        self.add_widget(anchor)

    def on_enter(self):
        for k, cb in self.checks.items():
            cb.active = nastroiki[k]

    def start(self, *a):
        global maxtest, test_nomer, correct_count, wrong_count
        for k, cb in self.checks.items():
            nastroiki[k] = cb.active
        try:
            maxtest = int(self.inp.text)
            if maxtest < 1:
                maxtest = 1
        except:
            maxtest = 3
        if sum(nastroiki.values()) < 2:
            styled_popup("Ошибка", "Выберите хотя бы 2 варианта")
            return
        test_nomer = 0
        correct_count = 0
        wrong_count = 0
        self.manager.get_screen('test').reset()
        self.manager.current = 'test'

    def open_stats(self, *a):
        self.manager.get_screen('stats').load()
        self.manager.current = 'stats'

class AboutScreen(BaseScreen):
    def __init__(self, **kw):
        super().__init__(**kw)
        a = AnchorLayout(padding=dp(30))
        box = BoxLayout(orientation='vertical', spacing=dp(20), size_hint=(0.9, 0.6))
        box.add_widget(Label(text="О программе", font_size='26sp', bold=True, color=ACCENT))
        box.add_widget(Label(
            text="Тренажер музыкальных интервалов\nv1.0\n\nТренируй слух, угадывай интервалы\nи становись лучше каждый день!",
            halign='center', color=TEXT_M, font_size='15sp'
        ))
        box.add_widget(RoundedButton(
            text="←  Назад", bg_color=(0.4, 0.4, 0.5, 1),
            size_hint_y=None, height=dp(55),
            on_press=lambda x: setattr(self.manager, 'current', 'start')
        ))
        a.add_widget(box)
        self.add_widget(a)

class TestScreen(BaseScreen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.answer = ""
        self.idx = 0
        root = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))

        self.lbl = Label(
            text="Вопрос 1 из 3", font_size='22sp', bold=True,
            color=ACCENT, size_hint_y=None, height=dp(50)
        )
        root.add_widget(self.lbl)

        card = BgBoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        self.g = GridLayout(cols=2, spacing=dp(12))
        self.btns = []
        for _ in range(7):
            btn = RoundedButton(bg_color=(0.22, 0.28, 0.40, 1), font_size='18sp')
            btn.bind(on_press=self.check)
            self.btns.append(btn)
            self.g.add_widget(btn)
        card.add_widget(self.g)
        root.add_widget(card)

        ctrl = BoxLayout(size_hint_y=None, height=dp(55), spacing=dp(15))
        ctrl.add_widget(RoundedButton(text="🔁  Повторить", bg_color=WARNING, on_press=lambda x: threading.Thread(target=audio.remember, daemon=True).start()))
        ctrl.add_widget(RoundedButton(text="🏠  В меню", bg_color=(0.4, 0.4, 0.5, 1), on_press=lambda x: setattr(self.manager, 'current', 'start')))
        root.add_widget(ctrl)

        self.add_widget(root)

    def reset(self):
        global test_nomer
        test_nomer = 0
        self.next_q()

    def next_q(self):
        global test_nomer, maxtest
        if test_nomer >= maxtest:
            self.manager.get_screen('result').show()
            self.manager.current = 'result'
            return
        self.lbl.text = f"Вопрос {test_nomer + 1} из {maxtest}"

        avail = {i: INTERVALS[i] for i, k in enumerate(NASTROIKI_KEYS) if nastroiki[k]}
        if len(avail) < 2:
            styled_popup("Ошибка", "Недостаточно интервалов", lambda: setattr(self.manager, 'current', 'start'))
            return

        self.idx = random.choice(list(avail.keys()))
        self.answer = avail[self.idx]
        noti_pravilnie['правильныйОтвет'] = self.answer
        try:
            with open(jpath('anser_save.json'), 'w', encoding='utf-8') as f:
                json.dump(noti_pravilnie, f, ensure_ascii=False, indent=4)
        except:
            pass

        # Звук в потоке, чтобы UI не зависал
        threading.Thread(target=audio.play_two_random_nots_type_no_diez, args=(self.idx,), daemon=True).start()

        shuf = INTERVALS.copy()
        random.shuffle(shuf)
        for i, btn in enumerate(self.btns):
            btn.text = shuf[i]

    def check(self, inst):
        global test_nomer, correct_count, wrong_count
        if inst.text == self.answer:
            correct_count += 1
            test_nomer += 1
            styled_popup("Ура!", "Вы правы!", self.next_q)
        else:
            wrong_count += 1
            test_nomer += 1
            styled_popup("Вы не правы!", f"Верный ответ — {noti_pravilnie.get('правильныйОтвет', '?')}.", self.next_q)

class ResultScreen(BaseScreen):
    def __init__(self, **kw):
        super().__init__(**kw)
        a = AnchorLayout(padding=dp(30))
        box = BoxLayout(orientation='vertical', spacing=dp(25), size_hint=(0.9, 0.55))
        box.add_widget(Label(text="🎉  Тест завершён!", font_size='28sp', bold=True, color=SUCCESS))
        self.lbl = Label(text="результат 0 из 0", font_size='24sp', bold=True, color=TEXT_M)
        box.add_widget(self.lbl)

        b = BoxLayout(orientation='vertical', spacing=dp(15), size_hint_y=None, height=dp(140))
        b.add_widget(RoundedButton(text="🏠  В главное меню", bg_color=ACCENT, on_press=lambda x: setattr(self.manager, 'current', 'start')))
        b.add_widget(RoundedButton(text="✖  Выйти", bg_color=DANGER, on_press=lambda x: App.get_running_app().stop()))
        box.add_widget(b)
        a.add_widget(box)
        self.add_widget(a)

    def show(self):
        global correct_count, maxtest
        save_results(correct_count, maxtest)
        self.lbl.text = f"результат {correct_count} из {maxtest}"

class StatsScreen(BaseScreen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.hist = []
        self.selected = None
        root = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))

        root.add_widget(Label(text="📊  История результатов", font_size='22sp', bold=True, color=ACCENT, size_hint_y=None, height=dp(45)))

        self.scroll = ScrollView()
        self.grid = GridLayout(cols=1, spacing=dp(8), size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll.add_widget(self.grid)
        root.add_widget(self.scroll)

        self.sum_lbl = Label(text="", font_size='13sp', color=(0.6, 0.6, 0.7, 1), size_hint_y=None, height=dp(35))
        root.add_widget(self.sum_lbl)

        b = BoxLayout(size_hint_y=None, height=dp(55), spacing=dp(10))
        b.add_widget(RoundedButton(text="➕  Добавить", bg_color=SUCCESS, on_press=self.add))
        b.add_widget(RoundedButton(text="✏️  Изменить", bg_color=WARNING, on_press=self.edit))
        b.add_widget(RoundedButton(text="🗑️  Удалить", bg_color=DANGER, on_press=self.delete))
        root.add_widget(b)

        root.add_widget(RoundedButton(
            text="←  Назад", bg_color=(0.4, 0.4, 0.5, 1),
            size_hint_y=None, height=dp(55),
            on_press=lambda x: setattr(self.manager, 'current', 'start')
        ))
        self.add_widget(root)

    def load(self):
        self.hist = load_history()
        self.refresh()

    def refresh(self):
        self.grid.clear_widgets()
        for i, e in enumerate(self.hist):
            date = e.get("timestamp", "-")
            c = e.get("correct", 0)
            t = e.get("total", 0)
            p = f"{c / t * 100:.1f}%" if t else "0%"
            btn = RoundedButton(
                text=f"{i + 1}.  {date}  |  {c} / {t}  ({p})",
                bg_color=(0.18, 0.20, 0.28, 1) if i != self.selected else (0.25, 0.40, 0.70, 1),
                font_size='14sp', size_hint_y=None, height=dp(48)
            )
            btn.bind(on_press=lambda x, idx=i: self.select(idx))
            self.grid.add_widget(btn)
        n = len(self.hist)
        if n:
            avg = sum(e.get("correct", 0) for e in self.hist) / n
            best = max(e.get("correct", 0) for e in self.hist)
            self.sum_lbl.text = f"Всего попыток: {n}   |   Среднее: {avg:.1f}   |   Лучший: {best}"
        else:
            self.sum_lbl.text = "Пока нет данных"
        self.selected = None

    def select(self, idx):
        self.selected = idx
        self.refresh()

    def add(self, *a):
        self.dialog(None)

    def edit(self, *a):
        if self.selected is None:
            styled_popup("Внимание", "Сначала нажмите на строку")
            return
        self.dialog(self.selected)

    def delete(self, *a):
        if self.selected is None:
            styled_popup("Внимание", "Сначала нажмите на строку")
            return
        if self.selected < len(self.hist):
            self.hist.pop(self.selected)
            save_history(self.hist)
            self.refresh()
            styled_popup("Готово", "Запись удалена")

    def dialog(self, idx):
        is_ed = idx is not None
        box = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(12))
        box.add_widget(Label(text="Правильных ответов:", color=TEXT_M, font_size='15sp'))
        i_c = StyledInput(text=str(self.hist[idx]["correct"]) if is_ed else "0", input_filter='int')
        box.add_widget(i_c)
        box.add_widget(Label(text="Всего вопросов:", color=TEXT_M, font_size='15sp'))
        i_t = StyledInput(text=str(self.hist[idx]["total"]) if is_ed else "3", input_filter='int')
        box.add_widget(i_t)

        def save(*a):
            try:
                c = int(i_c.text)
                t = int(i_t.text)
                if c < 0 or t <= 0 or c > t:
                    raise ValueError
            except:
                styled_popup("Ошибка", "Введите корректные числа\n(правильно ≤ всего, всего > 0)")
                return
            ent = {
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "correct": c,
                "total": t
            }
            if is_ed:
                self.hist[idx] = ent
            else:
                self.hist.append(ent)
            save_history(self.hist)
            self.refresh()
            p.dismiss()
            styled_popup("Готово", "Сохранено")

        box.add_widget(RoundedButton(text="💾  Сохранить", bg_color=ACCENT, size_hint_y=None, height=dp(55), on_press=save))
        p = Popup(title="Запись", content=box, size_hint=(0.85, 0.55),
                  title_color=TEXT_M, separator_color=ACCENT,
                  background_color=(0.06, 0.06, 0.10, 0.98))
        p.open()

class IntervalsApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(StartScreen(name='start'))
        sm.add_widget(AboutScreen(name='about'))
        sm.add_widget(TestScreen(name='test'))
        sm.add_widget(ResultScreen(name='result'))
        sm.add_widget(StatsScreen(name='stats'))
        return sm

if __name__ == '__main__':
    IntervalsApp().run()