"""
MaterialThemeLogic — Gestione tema dark/light, preferenze
"""

from PySide6.QtWidgets import QApplication

class MaterialThemeLogic:
    @staticmethod
    def set_theme(app: QApplication, theme: str):
        # Cambia tema (dark/light)
        pass

    @staticmethod
    def save_theme_pref(theme: str):
        # Salva preferenza tema
        pass

    @staticmethod
    def load_theme_pref() -> str:
        # Carica preferenza tema
        return 'light'

# Per test rapido
if __name__ == "__main__":
    pass
