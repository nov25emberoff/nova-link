"""
Nova Link — локальный чат-мессенджер бренда Nova Tech
========================================================
Библиотека: KivyMD (Kivy)
Хранение сообщений: только в оперативной памяти устройства (список Python).
Сервер не используется, интернет не требуется.

Запуск: python main.py  (или через Pydroid 3, см. инструкцию в конце файла)
"""

import time

from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField
from kivymd.uix.toolbar import MDTopAppBar

# ---------------------------------------------------------------------------
# Фирменные цвета Nova Tech
# ---------------------------------------------------------------------------
COLOR_BG = (0.04, 0.04, 0.04, 1)          # почти чёрный фон
COLOR_SURFACE = (0.10, 0.10, 0.10, 1)     # фон полей ввода / панелей
COLOR_ORANGE = (1.0, 0.55, 0.0, 1)        # фирменный оранжевый
COLOR_ORANGE_DARK = (0.75, 0.40, 0.0, 1)  # оранжевый для чужих акцентов
COLOR_TEXT = (1, 1, 1, 1)                 # белый текст
COLOR_TEXT_MUTED = (0.75, 0.75, 0.75, 1)

Window.clearcolor = COLOR_BG


# ---------------------------------------------------------------------------
# Пузырь сообщения
# ---------------------------------------------------------------------------
class MessageBubble(BoxLayout):
    """Один пузырь сообщения в чате."""

    def __init__(self, author, text, is_me=True, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint_y = None
        self.padding = (dp(14), dp(8), dp(14), dp(8))
        self.spacing = dp(2)

        bubble_color = COLOR_ORANGE if is_me else COLOR_SURFACE
        text_color = (0, 0, 0, 1) if is_me else COLOR_TEXT

        with self.canvas.before:
            Color(*bubble_color)
            self._rect = RoundedRectangle(radius=[dp(16)])
        self.bind(pos=self._update_rect, size=self._update_rect)

        author_label = Label(
            text=author,
            font_size=dp(11),
            color=(0, 0, 0, 0.6) if is_me else COLOR_ORANGE,
            size_hint_y=None,
            height=dp(14),
            halign="left",
            valign="middle",
        )
        author_label.bind(size=lambda w, *_: setattr(w, "text_size", w.size))

        msg_label = Label(
            text=text,
            color=text_color,
            font_size=dp(15),
            size_hint_y=None,
            halign="left",
            valign="top",
        )
        msg_label.bind(
            width=lambda w, *_: setattr(w, "text_size", (w.width, None))
        )
        msg_label.bind(texture_size=lambda w, ts: setattr(w, "height", ts[1]))

        self.add_widget(author_label)
        self.add_widget(msg_label)

        # Пересчитываем высоту пузыря, когда меняется высота текста
        msg_label.bind(height=self._recalc_height)
        self._msg_label = msg_label
        self._author_label = author_label
        Clock.schedule_once(lambda dt: self._recalc_height(msg_label, msg_label.height), 0)

    def _update_rect(self, *_):
        self._rect.pos = self.pos
        self._rect.size = self.size

    def _recalc_height(self, *_):
        self.height = self._author_label.height + self._msg_label.height + dp(20)


class BubbleRow(BoxLayout):
    """Строка-обёртка, чтобы прижать пузырь влево или вправо."""

    def __init__(self, bubble, is_me=True, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.padding = (dp(10), dp(4))
        bubble.size_hint_x = 0.75
        spacer = Label(size_hint_x=0.25)
        if is_me:
            self.add_widget(spacer)
            self.add_widget(bubble)
        else:
            self.add_widget(bubble)
            self.add_widget(spacer)
        bubble.bind(height=lambda w, h: setattr(self, "height", h + dp(8)))
        Clock.schedule_once(lambda dt: setattr(self, "height", bubble.height + dp(8)), 0)


# ---------------------------------------------------------------------------
# Экран входа
# ---------------------------------------------------------------------------
class LoginScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "login"
        self.md_bg_color = COLOR_BG

        root = MDBoxLayout(
            orientation="vertical",
            padding=dp(32),
            spacing=dp(20),
        )

        root.add_widget(BoxLayout(size_hint_y=0.15))

        # Иконка + название приложения ("Nova Link" при запуске)
        logo_box = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(140),
            spacing=dp(6),
        )
        icon_btn = MDIconButton(
            icon="message-text",
            icon_size=dp(64),
            theme_icon_color="Custom",
            icon_color=COLOR_ORANGE,
            pos_hint={"center_x": 0.5},
            disabled=True,
        )
        title_label = MDLabel(
            text="Nova Link",
            halign="center",
            font_style="H4",
            theme_text_color="Custom",
            text_color=COLOR_TEXT,
            bold=True,
        )
        subtitle_label = MDLabel(
            text="Локальный мессенджер Nova Tech",
            halign="center",
            theme_text_color="Custom",
            text_color=COLOR_TEXT_MUTED,
            font_style="Caption",
        )
        logo_box.add_widget(icon_btn)
        logo_box.add_widget(title_label)
        logo_box.add_widget(subtitle_label)
        root.add_widget(logo_box)

        root.add_widget(BoxLayout(size_hint_y=None, height=dp(20)))

        self.username_field = MDTextField(
            hint_text="Имя пользователя (например, nov25ember)",
            mode="rectangle",
            size_hint_x=1,
            pos_hint={"center_x": 0.5},
            line_color_normal=COLOR_ORANGE,
            line_color_focus=COLOR_ORANGE,
            hint_text_color_normal=COLOR_TEXT_MUTED,
            hint_text_color_focus=COLOR_ORANGE,
            text_color_normal=COLOR_TEXT,
            text_color_focus=COLOR_TEXT,
        )
        root.add_widget(self.username_field)

        self.error_label = MDLabel(
            text="",
            theme_text_color="Custom",
            text_color=(1, 0.3, 0.3, 1),
            font_style="Caption",
            size_hint_y=None,
            height=dp(20),
        )
        root.add_widget(self.error_label)

        login_btn = MDRaisedButton(
            text="Войти",
            md_bg_color=COLOR_ORANGE,
            text_color=(0, 0, 0, 1),
            pos_hint={"center_x": 0.5},
            size_hint_x=1,
            height=dp(48),
            font_style="H6" if False else None,
        )
        login_btn.bind(on_release=self.on_login)
        root.add_widget(login_btn)

        root.add_widget(BoxLayout())  # растяжка вниз

        self.add_widget(root)

    def on_login(self, *_):
        username = self.username_field.text.strip()
        if not username:
            self.error_label.text = "Введите имя пользователя"
            return
        app = MDApp.get_running_app()
        app.username = username
        chat_screen = self.manager.get_screen("chat")
        chat_screen.set_username(username)
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = "chat"


# ---------------------------------------------------------------------------
# Экран чата
# ---------------------------------------------------------------------------
class ChatScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "chat"
        self.md_bg_color = COLOR_BG
        self.username = "Вы"

        root = MDBoxLayout(orientation="vertical")

        # Верхняя панель
        self.toolbar = MDTopAppBar(
            title="Nova Link",
            left_action_items=[["message-text", lambda x: None]],
            elevation=0,
            md_bg_color=(0.06, 0.06, 0.06, 1),
            specific_text_color=COLOR_TEXT,
        )
        root.add_widget(self.toolbar)

        # Область сообщений
        self.scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        self.messages_box = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(2),
            padding=(0, dp(10)),
        )
        self.messages_box.bind(
            minimum_height=self.messages_box.setter("height")
        )
        self.scroll.add_widget(self.messages_box)
        root.add_widget(self.scroll)

        # Нижняя панель ввода
        input_bar = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(64),
            padding=(dp(10), dp(8)),
            spacing=dp(8),
            md_bg_color=(0.08, 0.08, 0.08, 1),
        )
        self.text_field = MDTextField(
            hint_text="Написать сообщение...",
            mode="rectangle",
            multiline=False,
            line_color_normal=COLOR_ORANGE,
            line_color_focus=COLOR_ORANGE,
            hint_text_color_normal=COLOR_TEXT_MUTED,
            text_color_normal=COLOR_TEXT,
            text_color_focus=COLOR_TEXT,
        )
        self.text_field.bind(on_text_validate=self.on_send)

        send_btn = MDIconButton(
            icon="send",
            theme_icon_color="Custom",
            icon_color=(0, 0, 0, 1),
            md_bg_color=COLOR_ORANGE,
        )
        send_btn.bind(on_release=self.on_send)

        input_bar.add_widget(self.text_field)
        input_bar.add_widget(send_btn)
        root.add_widget(input_bar)

        self.add_widget(root)

        # Хранилище сообщений в памяти устройства
        self.messages = []

    def set_username(self, username):
        self.username = username
        self.toolbar.title = f"Nova Link — {username}"
        if not self.messages:
            self.add_message(
                "Nova Bot",
                f"Добро пожаловать в Nova Link, {username}! Это локальный чат — "
                f"сообщения хранятся только в памяти этого устройства.",
                is_me=False,
            )

    def add_message(self, author, text, is_me):
        self.messages.append(
            {"author": author, "text": text, "is_me": is_me, "time": time.time()}
        )
        bubble = MessageBubble(author=author, text=text, is_me=is_me)
        row = BubbleRow(bubble, is_me=is_me)
        self.messages_box.add_widget(row)
        Clock.schedule_once(self._scroll_to_bottom, 0.05)

    def _scroll_to_bottom(self, *_):
        self.scroll.scroll_y = 0

    def on_send(self, *_):
        text = self.text_field.text.strip()
        if not text:
            return
        self.add_message(self.username, text, is_me=True)
        self.text_field.text = ""

        # Небольшая демонстрационная авто-реплика (можно удалить при желании)
        Clock.schedule_once(lambda dt: self._demo_reply(text), 0.8)

    def _demo_reply(self, original_text):
        self.add_message(
            "Nova Bot",
            f"Сообщение получено: «{original_text}»",
            is_me=False,
        )


# ---------------------------------------------------------------------------
# Приложение
# ---------------------------------------------------------------------------
class NovaLinkApp(MDApp):
    def build(self):
        self.title = "Nova Link"  # название приложения при запуске
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Orange"
        self.username = ""

        sm = ScreenManager()
        sm.add_widget(LoginScreen())
        sm.add_widget(ChatScreen())
        sm.current = "login"
        return sm


if __name__ == "__main__":
    import os
    import sys
    import traceback

    # Куда сохранять файл с текстом ошибки, если приложение упадёт.
    # Файл появится в той же папке, где лежит main.py.
    _crash_log_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "nova_link_crash.txt"
    )

    try:
        NovaLinkApp().run()
    except Exception:
        error_text = traceback.format_exc()
        try:
            with open(_crash_log_path, "w", encoding="utf-8") as f:
                f.write(error_text)
        except Exception:
            pass
        # Дублируем в стандартный вывод на случай, если консоль всё же доступна
        print("=" * 60)
        print("ПРОИЗОШЛА ОШИБКА. Текст ошибки сохранён в файл:")
        print(_crash_log_path)
        print("=" * 60)
        print(error_text)
        raise
