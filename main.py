import sys
import os
import logging
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLineEdit, QPushButton, QLabel, QDesktopWidget, QScrollArea,
                             QMessageBox, QFileDialog, QMenuBar, QAction, QSystemTrayIcon, 
                             QMenu, QComboBox, QInputDialog, QCheckBox, QTextEdit)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QRect, QSettings, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor, QPixmap,  QTextCursor

# Настройка логирования
#logging.basicConfig(filename="notes.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Путь к файлам
TEXT_FILE = "notes.txt"
#BACKUP_FILE = "notes_backup.txt"
SETTINGS_FILE = "settings.ini"

class Localization:
    def __init__(self, lang="ru"):
        self.lang = lang
        self.translations = {
            "ru": {
                "title": "NoteApp",
                "expand": "Развернуть",
                "add": "+",
                "edit_mode": "Режим редактирования",
                "saved": "Заметка сохранена!",
                "error": "Ошибка",
                "error_saving": "Ошибка при сохранении!",
                "error_loading": "Ошибка при загрузке!",
                "error_backup": "Ошибка при создании резервной копии!",
                "edit_note": "Редактировать заметку",
                "enter_note": "Введите заметку",
                "add_note": "Добавить заметку",
                "show_all_notes": "Показать все заметки",
                "show": "Показать",
                "quit": "Выход",
                "language": "Язык",
                "select_language": "Выберите язык",
                "clear_file": "Очистить файл",
                "are_you_sure_clear": "Вы уверены, что хотите очистить файл?",
                "search": "Поиск",
                "export": "Экспорт",
                "import": "Импорт",
                "tags": "Теги",
                "reminder": "Напоминание",
                "settings": "Настройки",
                "ru":"Русский",
                "en":"Английский",
                "theme":"Тема",
                "theme_light": "Светлая тема",
                "theme_dark": "Темная тема",
                "edit_mode":"Изменить текст"
            },
            "en": {
                "title": "NoteApp",
                "expand": "Expand",
                "add": "+",
                "edit_mode": "Edit mode",
                "saved": "Note saved!",
                "error": "Error",
                "error_saving": "Error saving!",
                "error_loading": "Error loading!",
                "error_backup": "Error creating backup!",
                "edit_note": "Edit note",
                "enter_note": "Enter note",
                "add_note": "Add note",
                "show_all_notes": "Show all notes",
                "show": "Show",
                "quit": "Quit",
                "language": "Language",
                "select_language": "Select language",
                "clear_file": "Clear file",
                "are_you_sure_clear": "Are you sure you want to clear the file?",
                "search": "Search",
                "export": "Export",
                "import": "Import",
                "tags": "Tags",
                "reminder": "Reminder",
                "settings": "Settings",
                "ru":"Russian",
                "en":"English",
                "theme":"Theme",
                "theme_light": "Light theme",
                "theme_dark": "Dark theme",
                "edit_mode":"Edit text"
            }
        }

    def get(self, key):
        return self.translations[self.lang].get(key, key)

    def set_language(self, new_lang):
        self.lang = new_lang
        return self


class SmallForm(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings(SETTINGS_FILE, QSettings.IniFormat)
        self.lang = self.settings.value("language", "ru")
        self.theme = self.settings.value("theme", "light")
        self.loc = Localization(self.lang)
        self.initUI()
        self.load_notes()
        self.setup_tray()

    def initUI(self):
        self.setWindowTitle(self.loc.get("title"))
        self.setFixedSize(350, 60)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setWindowIcon(QIcon("icon.png"))

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        self.note_input = QLineEdit()
        self.note_input.setFont(QFont("Segoe UI", 11))
        self.note_input.setPlaceholderText(self.loc.get("enter_note"))
        self.note_input.setStyleSheet("""
            QLineEdit { border: 1px solid #757575; border-radius: 8px; padding: 8px; background-color: #FFFFFF; color: #333333;}
            QLineEdit:focus { border: 1px solid #757575; background-color: #F5F5F5;}
        """)
        main_layout.addWidget(self.note_input, stretch=1)

        self.add_button = QPushButton(self.loc.get("add"))
        self.add_button.setFixedSize(32, 32)
        self.add_button.setStyleSheet("""
            QPushButton { background-color: #607D8B; color: #FFFFFF; border-radius: 16px; font-size: 18px; border: none;}
            QPushButton:hover { background-color: #455A64; }
        """)
        self.add_button.clicked.connect(self.save_note)
        main_layout.addWidget(self.add_button)

        self.expand_button = QPushButton(self.loc.get("expand"))
        self.expand_button.setFixedSize(100, 32)
        self.expand_button.setStyleSheet("""
            QPushButton { background-color: #607D8B; color: #FFFFFF; border-radius: 8px; font-size: 11px; border: none;}
            QPushButton:hover { background-color: #455A64; }
        """)
        self.expand_button.clicked.connect(self.open_large_form)
        main_layout.addWidget(self.expand_button)

        self.apply_theme()
        self.load_position()
        self.start_animation()

    def apply_theme(self):
        if self.theme == "dark":
            self.setStyleSheet("background-color: #424242; color: #FFFFFF;")
            self.note_input.setStyleSheet("""
                QLineEdit { border: 1px solid #555555; border-radius: 8px; padding: 8px; background-color: #3C3C3C; color: #FFFFFF; }
            """)
        else:
            self.setStyleSheet("background-color: #F5F5F5; color: #333333;")
            self.note_input.setStyleSheet("""
                QLineEdit { border: 1px solid #757575; border-radius: 8px; padding: 8px; background-color: #FFFFFF; color: #333333; }
            """)

    def start_animation(self):
        #self.animation = QPropertyAnimation(self, b"geometry")
        #self.animation.setDuration(300)
        #self.animation.setStartValue(QRect(self.x(), self.y()+50, self.width(), self.height()))
        #self.animation.setEndValue(QRect(self.x(), self.y(), self.width(), self.height()))
        #self.animation.start()
        pass

    def setup_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("icon.png"))
        tray_menu = QMenu()
        show_action = tray_menu.addAction(self.loc.get("show"))
        show_action.triggered.connect(self.show)
        quit_action = tray_menu.addAction(self.loc.get("quit"))
        quit_action.triggered.connect(QApplication.quit)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def position_near_taskbar(self):
        available_geometry = QDesktopWidget().availableGeometry()
        self.move(available_geometry.width() - self.width() - 15, available_geometry.height() - self.height() - 15)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return and event.modifiers() & Qt.ShiftModifier:
            self.save_note()
            event.accept()
        else:
            super().keyPressEvent(event)

    def save_note(self):
        note_text = self.note_input.text().strip()
        if note_text:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_note = f"{current_time}\n{note_text}\n\n"
            with open(TEXT_FILE, "a", encoding="utf-8") as f:
                f.write(new_note)
            self.note_input.clear()
            self.show_notification(self.loc.get("saved"), "success")

    def load_notes(self):
        pass

    def show_notification(self, message, type_="success"):
        self.setStyleSheet(f"background-color: {'#A5D6A7' if type_ == 'success' else '#EF9A9A'}; color: #333333;")
        QTimer.singleShot(500, lambda: self.apply_theme())

    def load_position(self):
        pos = self.settings.value("position", None)
        if pos:
            self.move(pos)
        else:
            self.position_near_taskbar()

    def closeEvent(self, event):
        self.settings.setValue("position", self.pos())
        self.settings.setValue("theme", self.theme)
        self.settings.setValue("language", self.lang)
        event.accept()

    def open_large_form(self):
        self.large_form = LargeForm(self)
        self.large_form.show()
        self.hide()

    def update_ui_language(self):
        self.setWindowTitle(self.loc.get("title"))
        self.note_input.setPlaceholderText(self.loc.get("enter_note"))
        self.add_button.setText(self.loc.get("add"))
        self.expand_button.setText(self.loc.get("expand"))

class LargeForm(QMainWindow):
    def __init__(self, small_form):
        super().__init__()
        self.small_form = small_form
        self.loc = self.small_form.loc
        self.theme = self.small_form.theme
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.loc.get("title"))
        self.setMinimumSize(600, 400)
        self.setWindowIcon(QIcon("icon.png"))

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        self.create_menu_bar()
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setStyleSheet("""
            QTextEdit { border: 1px solid #757575; border-radius: 8px; padding: 8px; background-color: #FFFFFF; color: #333333; }
        """)
        main_layout.addWidget(self.text_edit)

        bottom_panel = QHBoxLayout()
        bottom_panel.setSpacing(8)

        self.note_input = QLineEdit()
        self.note_input.setPlaceholderText(self.loc.get("enter_note"))
        self.note_input.setStyleSheet("""
            QLineEdit { border: 1px solid #757575; border-radius: 8px; padding: 8px; background-color: #FFFFFF; color: #333333; }
            QLineEdit:focus { border: 1px solid #757575; background-color: #F5F5F5;}
        """)
        bottom_panel.addWidget(self.note_input, stretch=1)

        self.add_button = QPushButton(self.loc.get("add"))
        self.add_button.setFixedSize(32, 32)
        self.add_button.setStyleSheet("""
            QPushButton { background-color: #607D8B; color: #FFFFFF; border-radius: 16px; font-size: 18px; border: none; }
            QPushButton:hover { background-color: #455A64; }
        """)
        self.add_button.clicked.connect(self.save_note)
        bottom_panel.addWidget(self.add_button)

        self.edit_checkbox = QCheckBox(self.loc.get("edit_mode"))
        self.edit_checkbox.stateChanged.connect(self.toggle_edit_mode)
        main_layout.addWidget(self.edit_checkbox)
        main_layout.addLayout(bottom_panel)
        self.load_notes()
        self.apply_theme()

    def auto_save(self):
        with open(TEXT_FILE, "w", encoding="utf-8") as f:
            f.write(self.text_edit.toPlainText())

    def create_menu_bar(self):
        menu_bar = self.menuBar()
        menu_bar.clear()
        settings_menu = QMenu(self.loc.get("settings"), self)
        clear_action = QAction(self.loc.get("clear_file"), self)
        export_action = QAction(self.loc.get("export"), self)
        import_action = QAction(self.loc.get("import"), self)
        settings_menu.addAction(clear_action)
        settings_menu.addAction(export_action)
        settings_menu.addAction(import_action)
        menu_bar.addMenu(settings_menu)
        language_menu = QMenu(self.loc.get("language"), self)
        ru_action = QAction(self.loc.get("ru"), self)
        en_action = QAction(self.loc.get("en"), self)
        language_menu.addAction(ru_action)
        language_menu.addAction(en_action)
        menu_bar.addMenu(language_menu)
        theme_menu = QMenu(self.loc.get("theme"), self)
        light_theme = QAction(self.loc.get("theme_light"), self)
        dark_theme = QAction(self.loc.get("theme_dark"), self)
        theme_menu.addAction(light_theme)
        theme_menu.addAction(dark_theme)
        menu_bar.addMenu(theme_menu)


        ru_action.triggered.connect(lambda: self.change_language("ru"))
        en_action.triggered.connect(lambda: self.change_language("en"))
        clear_action.triggered.connect(self.clear_file)
        export_action.triggered.connect(self.export_notes)
        import_action.triggered.connect(self.import_notes)
        light_theme.triggered.connect(lambda: self.change_theme("light"))
        dark_theme.triggered.connect(lambda: self.change_theme("dark"))
        


    def change_language(self, new_lang):
        self.loc = self.loc.set_language(new_lang)
        self.small_form.loc = self.loc
        self.small_form.lang = new_lang
        self.update_ui_language()
        self.small_form.update_ui_language()
        self.update_menu_language()

    def update_menu_language(self):
        self.create_menu_bar()  # Обновляем меню

    def change_theme(self, new_theme):
        self.theme = new_theme
        self.small_form.theme = new_theme
        self.apply_theme()
        self.small_form.apply_theme()

    def update_ui_language(self):
        self.setWindowTitle(self.loc.get("title"))
        self.note_input.setPlaceholderText(self.loc.get("enter_note"))
        self.add_button.setText(self.loc.get("add"))
        self.edit_checkbox.setText(self.loc.get("edit_mode"))
        self.load_notes()

    def load_notes(self):
        if os.path.exists(TEXT_FILE):
            with open(TEXT_FILE, "r", encoding="utf-8") as f:
                text = f.read()
                self.text_edit.setText(text)
                self.text_edit.verticalScrollBar().setValue(self.text_edit.verticalScrollBar().maximum())
                self.text_edit.moveCursor(QTextCursor.End)
    
    def save_note(self):
        self.auto_save()
        note_text = self.note_input.text().strip()
        if note_text:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_note = f"{current_time}\n{note_text}\n\n"
            with open(TEXT_FILE, "a", encoding="utf-8") as f:
                f.write(new_note)
            self.note_input.clear()
            self.show_notification(self.loc.get("saved"), "success")
            self.load_notes()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return and event.modifiers() & Qt.ShiftModifier:
            self.save_note()
            event.accept()
        else:
            super().keyPressEvent(event)

    def toggle_edit_mode(self, state):
        self.text_edit.setReadOnly(not state)
        if state:
            self.auto_save()
        self.save_note()

    def auto_save(self):
        with open(TEXT_FILE, "w", encoding="utf-8") as f:
            f.write(self.text_edit.toPlainText())
        self.load_notes()

    def clear_file(self):
        reply = QMessageBox.question(self, self.loc.get("clear_file"), self.loc.get("are_you_sure_clear"), QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            with open(TEXT_FILE, "w", encoding="utf-8") as f:
                f.write("")
            self.load_notes()

    def export_notes(self):
        file_name, _ = QFileDialog.getSaveFileName(self, self.loc.get("export"), "", "Text Files (*.txt)")
        if file_name:
            try:
                with open(file_name, "w", encoding="utf-8") as f:
                    f.write(self.text_edit.toPlainText())
            except Exception as e:
                self.show_notification(self.loc.get("error_saving") + f"\n{e}", "error")

    def import_notes(self):
        file_name, _ = QFileDialog.getOpenFileName(self, self.loc.get("import"), "", "Text Files (*.txt)")
        if file_name:
            try:
                with open(file_name, "r", encoding="utf-8") as f:
                    text = f.read()
                    with open(TEXT_FILE, "a", encoding="utf-8") as notes_file:
                        notes_file.write(text)
                self.load_notes()
            except Exception as e:
                self.show_notification(self.loc.get("error_loading") + f"\n{e}", "error")

    def show_notification(self, message, type_="success"):
        self.setStyleSheet(f"background-color: {'#A5D6A7' if type_ == 'success' else '#EF9A9A'}; color: #333333;")
        QTimer.singleShot(500, lambda: self.apply_theme())

    def closeEvent(self, event):
        self.small_form.show()
        event.accept()

    def apply_theme(self):
        if self.theme == "dark":
            self.setStyleSheet("background-color: #424242; color: #FFFFFF;")
        else:
            self.setStyleSheet("background-color: #F5F5F5; color: #333333;")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    small_form = SmallForm()
    small_form.show()
    sys.exit(app.exec_())