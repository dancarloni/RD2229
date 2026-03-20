"""
MaterialSettingsDialog — Dialog per editare i file di configurazione dei materiali.

Mostra un tab per ogni famiglia con il contenuto JSON del file di configurazione;
permette di modificare e salvare le formule/parametri senza uscire dall'applicazione.
"""

from __future__ import annotations

import json
import logging
import shutil
from pathlib import Path

from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSizePolicy,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from src.ui.qt.material_editor.logic.material_config import MaterialConfigLoader

logger = logging.getLogger(__name__)


class MaterialSettingsDialog(QDialog):
    """Dialog per la configurazione dei materiali (famiglie, norme, formule)."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Impostazioni — Configurazione materiali")
        self.resize(800, 600)

        self._loader = MaterialConfigLoader()
        self._tab_data: dict[str, dict] = {}  # key famiglia → {path, editor}

        outer = QVBoxLayout(self)

        info = QLabel(
            "Modifica i parametri, le formule e le norme per ogni famiglia. "
            "Salva per applicare immediatamente le modifiche."
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

    # ── setup ────────────────────────────────────────────────────────────────

    def _populate_tabs(self) -> None:
        """Carica le tab per ogni famiglia config."""
        self._tabs.clear()
        self._tab_data.clear()

        families = self._loader.load_families()
        # Aggiunge anche il tab families.json
        config_dir = self._loader.config_dir()

        families_path = config_dir / "families.json"
        if families_path.exists():
            editor = self._make_editor_tab(families_path)
            self._tabs.addTab(editor, "families.json")
            self._tab_data["__families__"] = {"path": families_path, "editor": editor}

        for fam in families:
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
        """Crea un editor di testo per un file JSON."""
        editor = QPlainTextEdit()
        editor.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        editor.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        try:
            text = path.read_text(encoding="utf-8")
            # Pretty-print per leggibilità
            try:
                data = json.loads(text)
                text = json.dumps(data, indent=2, ensure_ascii=False)
            except json.JSONDecodeError:
                pass  # usa testo grezzo se non è JSON valido
            editor.setPlainText(text)
        except Exception as exc:
            editor.setPlainText(f"# Errore lettura file: {exc}")
        return editor

    # ── handlers ─────────────────────────────────────────────────────────────

    def _on_save_all(self) -> None:
        """Salva tutti i file modificati sul disco con backup transazionale.

        Logica:
        1. Valida tutti i JSON (errore → non scrivere nulla)
        2. Crea backup .bak per ogni file
        3. Scrive tutti i file; se uno fallisce non scrive i successivi
        4. In caso di fallimento mostra warning con path backup disponibili

        # [MATERIAL_EDITOR_DESIGN.md] MaterialSettingsDialog backup logic
        """
        validated: list[tuple[Path, str]] = []

        # Fase 1: validazione JSON (tutti prima di toccare i file)
        validation_errors: list[str] = []
        for key, entry in self._tab_data.items():
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
                "I seguenti file contengono JSON non valido "
                "(nessun file è stato scritto):\n\n" + "\n".join(validation_errors),
            )
            return

        # Fase 2: crea backup .bak (sovrascrive eventuale backup precedente)
        backup_paths: list[Path] = []
        backup_errors: list[str] = []
        for path, _ in validated:
            bak = path.with_suffix(".bak")
            try:
                shutil.copy2(path, bak)
                backup_paths.append(bak)
                logger.debug("Backup creato: %s", bak)
            except Exception as exc:
                backup_errors.append(f"{path.name}: impossibile creare backup — {exc}")

        if backup_errors:
            # Non bloccante: avvisa ma continua
            logger.warning("Errori durante creazione backup: %s", backup_errors)

        # Fase 3: scrittura transazionale (prima errore → stop)
        write_errors: list[str] = []
        written: list[Path] = []
        for path, text in validated:
            try:
                path.write_text(text, encoding="utf-8")
                written.append(path)
            except Exception as exc:
                write_errors.append(f"{path.name}: errore scrittura — {exc}")
                break  # stop: non scrivere altri file

        if write_errors:
            backup_info = (
                "\n\nBackup disponibili in:\n"
                + "\n".join(str(p) for p in backup_paths)
                if backup_paths else ""
            )
            QMessageBox.warning(
                self,
                "Salvataggio parziale",
                f"Scrittura interrotta:\n\n"
                + "\n".join(write_errors)
                + f"\n\n{len(written)}/{len(validated)} file scritti."
                + backup_info,
            )
            return

        # Successo
        try:
            self._loader.reload()
        except Exception:
            pass
        logger.info("Configurazione materiali salvata (%d file)", len(written))
        QMessageBox.information(
            self, "Salvato",
            f"Configurazione salvata correttamente ({len(written)} file)."
        )

    def _on_reload(self) -> None:
        """Ricarica i file da disco, perdendo le modifiche non salvate."""
        reply = QMessageBox.question(
            self,
            "Ricarica",
            "Ricaricare i file da disco? Le modifiche non salvate saranno perse.",
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._loader.reload()
            self._populate_tabs()

    def _on_restore_from_backup(self) -> None:
        """Mostra i backup disponibili e permette di ripristinare i file originali.

        Cerca i file .bak nella stessa directory dei config e permette di
        ripristinarli sovrascrivendo il file corrente.
        """
        config_dir = self._loader.config_dir()
        bak_files = sorted(config_dir.glob("*.bak"))

        if not bak_files:
            QMessageBox.information(
                self, "Nessun backup",
                "Non sono stati trovati file di backup (.bak) in:\n" + str(config_dir)
            )
            return

        # Dialog selezione backup
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
                logger.info("Ripristinato da backup: %s → %s", bak_path, target)
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
