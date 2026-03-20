"""
MaterialSettingsDialog — Vista formule/materiali in sola lettura.

Mostra un tab per ogni famiglia con formule e riferimenti normativi,
senza esporre i JSON nel flusso principale. Per esigenze tecniche,
resta disponibile un editor JSON avanzato opzionale.
"""

from __future__ import annotations

import json
import logging
import shutil
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from src.ui.qt.material_editor.logic.material_config import MaterialConfigLoader

logger = logging.getLogger(__name__)


class MaterialSettingsDialog(QDialog):
    """Dialog principale: formule per famiglia in sola lettura."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Impostazioni — Configurazione materiali")
        self.resize(900, 640)

        self._loader = MaterialConfigLoader()

        outer = QVBoxLayout(self)

        info = QLabel(
            "Consulta schemi, formule e riferimenti normativi per ogni famiglia. "
            "Per modifiche tecniche ai file JSON usa l'editor avanzato."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #555; font-size: 11px;")
        outer.addWidget(info)

        self._tabs = QTabWidget()
        outer.addWidget(self._tabs, stretch=1)

        btn_row = QHBoxLayout()
        self._btn_advanced = QPushButton("Editor JSON avanzato")
        self._btn_reload = QPushButton("Ricarica da disco")
        self._btn_close = QPushButton("Chiudi")
        btn_row.addWidget(self._btn_advanced)
        btn_row.addWidget(self._btn_reload)
        btn_row.addStretch()
        btn_row.addWidget(self._btn_close)
        outer.addLayout(btn_row)

        self._btn_advanced.clicked.connect(self._on_open_advanced_editor)
        self._btn_reload.clicked.connect(self._on_reload)
        self._btn_close.clicked.connect(self.accept)

        self._populate_tabs()

    def _populate_tabs(self) -> None:
        """Carica un tab formula-view per ogni famiglia (niente families.json)."""
        self._tabs.clear()

        families = self._loader.load_families()
        for fam in families:
            key = fam["key"]
            label = fam.get("label", key)
            try:
                schema = self._loader.load_schema(key)
            except Exception as exc:
                error_widget = QLabel(f"Impossibile leggere schema {key}: {exc}")
                error_widget.setWordWrap(True)
                self._tabs.addTab(error_widget, label)
                continue

            tab = self._build_family_tab(schema)
            self._tabs.addTab(tab, label)

    def _build_family_tab(self, family_schema: dict) -> QWidget:
        """Costruisce la vista read-only di una famiglia con formule per norma."""
        container = QWidget()
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(6, 6, 6, 6)
        vbox.setSpacing(8)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(8)

        norms = family_schema.get("norme", [])
        visible_count = 0

        for norm in norms:
            if not norm.get("attiva", True):
                continue

            visible_count += 1
            title = norm.get("label", norm.get("key", "Norma"))
            group = QGroupBox(title)
            group.setStyleSheet("QGroupBox { font-weight: bold; margin-top: 6px; }")
            grid = QGridLayout(group)
            grid.setColumnStretch(1, 2)
            grid.setColumnStretch(2, 3)
            grid.setHorizontalSpacing(8)
            grid.setVerticalSpacing(4)

            row = 0
            row = self._add_section_rows(grid, row, "Parametri principali", norm.get("parametri_input", []))
            row = self._add_section_rows(grid, row, "Parametri derivati", norm.get("parametri_derivati", []))

            if row == 0:
                msg = QLabel("Nessun parametro disponibile per questa norma.")
                msg.setStyleSheet("color: #777; font-size: 10px;")
                grid.addWidget(msg, 0, 0, 1, 3)

            content_layout.addWidget(group)

        if visible_count == 0:
            empty = QLabel("Nessuna norma attiva disponibile per questa famiglia.")
            empty.setStyleSheet("color: #777; font-size: 10px;")
            content_layout.addWidget(empty)

        content_layout.addStretch()
        scroll.setWidget(content)
        vbox.addWidget(scroll)

        return container

    def _add_section_rows(self, grid: QGridLayout, row: int, title: str, fields: list[dict]) -> int:
        if not fields:
            return row

        header = QLabel(title)
        header.setStyleSheet("font-weight: 600; color: #555; font-size: 10px;")
        grid.addWidget(header, row, 0, 1, 3)
        row += 1

        for field in fields:
            label = QLabel(_field_label(field))
            label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            descr = field.get("descrizione", "") or "-"
            descr_lbl = QLabel(descr)
            descr_lbl.setWordWrap(True)
            descr_lbl.setStyleSheet("color: #444; font-size: 10px;")

            note_lbl = QLabel(_formula_note(field))
            note_lbl.setWordWrap(True)
            note_lbl.setTextFormat(Qt.TextFormat.RichText)
            note_lbl.setStyleSheet("color: #555; font-size: 10px;")

            grid.addWidget(label, row, 0)
            grid.addWidget(descr_lbl, row, 1)
            grid.addWidget(note_lbl, row, 2)
            row += 1

        return row

    def _on_open_advanced_editor(self) -> None:
        dlg = _AdvancedJsonEditorDialog(self)
        dlg.exec()

    def _on_reload(self) -> None:
        self._loader.reload()
        self._populate_tabs()


class _AdvancedJsonEditorDialog(QDialog):
    """Editor JSON completo opzionale per manutenzione tecnica."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Editor JSON avanzato — Materiali")
        self.resize(900, 640)

        self._loader = MaterialConfigLoader()
        self._tab_data: dict[str, dict] = {}

        outer = QVBoxLayout(self)
        info = QLabel(
            "Vista tecnica avanzata: modifica diretta dei file JSON di configurazione. "
            "Usare con cautela."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #555; font-size: 11px;")
        outer.addWidget(info)

        self._tabs = QTabWidget()
        outer.addWidget(self._tabs, stretch=1)

        btn_row = QHBoxLayout()
        self._btn_save_all = QPushButton("Salva tutto")
        self._btn_reload = QPushButton("Ricarica da disco")
        self._btn_restore = QPushButton("Ripristina da backup…")
        self._btn_close = QPushButton("Chiudi")
        btn_row.addWidget(self._btn_save_all)
        btn_row.addWidget(self._btn_reload)
        btn_row.addWidget(self._btn_restore)
        btn_row.addStretch()
        btn_row.addWidget(self._btn_close)
        outer.addLayout(btn_row)

        self._btn_save_all.clicked.connect(self._on_save_all)
        self._btn_reload.clicked.connect(self._on_reload)
        self._btn_restore.clicked.connect(self._on_restore_from_backup)
        self._btn_close.clicked.connect(self.accept)

        self._populate_tabs()

    def _populate_tabs(self) -> None:
        self._tabs.clear()
        self._tab_data.clear()

        config_dir = self._loader.config_dir()
        families_path = config_dir / "families.json"
        if families_path.exists():
            editor = self._make_editor_tab(families_path)
            self._tabs.addTab(editor, "families.json")
            self._tab_data["__families__"] = {"path": families_path, "editor": editor}

        for fam in self._loader.load_families():
            key = fam["key"]
            label = fam.get("label", key)
            config_path = config_dir / f"{key}_config.json"
            if not config_path.exists():
                self._tabs.addTab(QLabel(f"File non trovato: {config_path}"), label)
                continue
            editor = self._make_editor_tab(config_path)
            self._tabs.addTab(editor, label)
            self._tab_data[key] = {"path": config_path, "editor": editor}

    def _make_editor_tab(self, path: Path) -> QPlainTextEdit:
        editor = QPlainTextEdit()
        editor.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        try:
            text = path.read_text(encoding="utf-8")
            try:
                data = json.loads(text)
                text = json.dumps(data, indent=2, ensure_ascii=False)
            except json.JSONDecodeError:
                pass
            editor.setPlainText(text)
        except Exception as exc:
            editor.setPlainText(f"# Errore lettura file: {exc}")
        return editor

    def _on_save_all(self) -> None:
        validated: list[tuple[Path, str]] = []
        validation_errors: list[str] = []

        for entry in self._tab_data.values():
            path: Path = entry["path"]
            editor: QPlainTextEdit = entry["editor"]
            text = editor.toPlainText().strip()
            try:
                json.loads(text)
                validated.append((path, text))
            except json.JSONDecodeError as exc:
                validation_errors.append(f"{path.name}: JSON non valido — {exc}")

        if validation_errors:
            QMessageBox.warning(
                self,
                "Errore JSON",
                "I seguenti file contengono JSON non valido (nessun file è stato scritto):\n\n"
                + "\n".join(validation_errors),
            )
            return

        backup_paths: list[Path] = []
        for path, _ in validated:
            bak = path.with_suffix(".bak")
            try:
                shutil.copy2(path, bak)
                backup_paths.append(bak)
            except Exception as exc:
                logger.warning("Errore backup %s: %s", path, exc)

        write_errors: list[str] = []
        for path, text in validated:
            try:
                path.write_text(text, encoding="utf-8")
            except Exception as exc:
                write_errors.append(f"{path.name}: errore scrittura — {exc}")
                break

        if write_errors:
            backup_info = (
                "\n\nBackup disponibili in:\n" + "\n".join(str(p) for p in backup_paths)
                if backup_paths else ""
            )
            QMessageBox.warning(
                self,
                "Salvataggio parziale",
                "Scrittura interrotta:\n\n"
                + "\n".join(write_errors)
                + backup_info,
            )
            return

        self._loader.reload()
        QMessageBox.information(self, "Salvato", f"Configurazione salvata correttamente ({len(validated)} file).")

    def _on_reload(self) -> None:
        reply = QMessageBox.question(
            self,
            "Ricarica",
            "Ricaricare i file da disco? Le modifiche non salvate saranno perse.",
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._loader.reload()
            self._populate_tabs()

    def _on_restore_from_backup(self) -> None:
        config_dir = self._loader.config_dir()
        bak_files = sorted(config_dir.glob("*.bak"))

        if not bak_files:
            QMessageBox.information(
                self,
                "Nessun backup",
                "Non sono stati trovati file di backup (.bak) in:\n" + str(config_dir),
            )
            return

        dlg = _RestoreBackupDialog(bak_files, parent=self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        selected = dlg.selected_backups()
        if not selected:
            return

        restored = []
        errors = []
        for bak_path in selected:
            target = bak_path.with_suffix(".json")
            try:
                shutil.copy2(bak_path, target)
                restored.append(target.name)
            except Exception as exc:
                errors.append(f"{bak_path.name}: {exc}")

        self._loader.reload()
        self._populate_tabs()

        msg = f"Ripristinati {len(restored)} file: " + ", ".join(restored)
        if errors:
            msg += "\n\nErrori:\n" + "\n".join(errors)
            QMessageBox.warning(self, "Ripristino parziale", msg)
        else:
            QMessageBox.information(self, "Ripristino completato", msg)


class _RestoreBackupDialog(QDialog):
    """Dialog interno per la selezione dei backup da ripristinare."""

    def __init__(self, bak_files: list[Path], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Ripristina da backup")
        self.resize(420, 280)
        self._bak_files = bak_files

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Seleziona i backup da ripristinare (Ctrl+click per selezione multipla):"))

        self._list = QListWidget()
        self._list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        for p in bak_files:
            self._list.addItem(p.name)
        layout.addWidget(self._list)

        btn_row = QHBoxLayout()
        btn_ok = QPushButton("Ripristina selezionati")
        btn_cancel = QPushButton("Annulla")
        btn_row.addWidget(btn_ok)
        btn_row.addStretch()
        btn_row.addWidget(btn_cancel)
        layout.addLayout(btn_row)

        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)

    def selected_backups(self) -> list[Path]:
        return [self._bak_files[i.row()] for i in self._list.selectedIndexes()]


def _field_label(field: dict) -> str:
    lbl = field.get("label", field.get("key", "?"))
    unit = field.get("unita", "")
    return f"{lbl} [{unit}]" if unit else str(lbl)


def _formula_note(field: dict) -> str:
    formula_html = field.get("formula_html", "")
    formula_latex = field.get("formula_latex", "")
    formula_plain = field.get("formula", "")
    rif_norm = field.get("rif_norm", "")

    if formula_html:
        formula_text = formula_html
    elif formula_latex:
        formula_text = f"<i>{formula_latex}</i>"
    elif formula_plain:
        formula_text = f"<code>{formula_plain}</code>"
    else:
        formula_text = "<span style='color:#888'>Formula non definita</span>"

    if rif_norm and rif_norm != "—":
        return f"<small>{formula_text}<br><span style='color:#888'>[{rif_norm}]</span></small>"
    return f"<small>{formula_text}</small>"
