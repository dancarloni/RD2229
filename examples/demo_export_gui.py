"""Demo GUI Export Backup.
======================

Dimostra la funzionalità "Esporta backup..." dalla GUI principale.

Per testare:
1. Esegui questo script
2. Nella finestra principale, clicca su "File → Esporta backup..."
3. Scegli cosa esportare (Sezioni, Materiali, Entrambi)
4. Seleziona il percorso e il formato (JSON o CSV)
5. Verifica il messaggio di conferma

Autore: Sistema automatico
Data: 2025
"""

import tempfile
from pathlib import Path

from sections_app.ui.module_selector import ModuleSelectorWindow

from core_models.materials import Material, MaterialRepository
from sections_app.models.sections import CircularSection, RectangularSection, TSection
from sections_app.services.repository import CsvSectionSerializer, SectionRepository


def main():
    """Avvia la GUI con dati di esempio."""
    print("\n" + "=" * 70)
    print("  DEMO GUI EXPORT BACKUP")
    print("=" * 70)
    print("\nPreparazione dati di test...")

    # Crea repository temporanei con dati di test
    temp_dir = tempfile.mkdtemp()
    temp_path = Path(temp_dir)

    # Repository sezioni con dati di esempio (canonical .jsons in temp)
    sec_dir = temp_path / "sec_repository"
    sec_dir.mkdir(exist_ok=True)
    section_repo = SectionRepository(json_file=str(sec_dir / "sec_repository.jsons"))

    rect = RectangularSection(name="Pilastro 30x50", width=300, height=500)
    circ = CircularSection(name="Palo Circolare D40", diameter=400)
    tsec = TSection(name="Trave a T", flange_width=500, flange_thickness=100, web_thickness=150, web_height=700)

    section_repo.add_section(rect)
    section_repo.add_section(circ)
    section_repo.add_section(tsec)

    print(f"✓ Aggiunte {len(section_repo.get_all_sections())} sezioni")

    # Repository materiali con dati di esempio
    material_repo = MaterialRepository(json_file=str(temp_path / "materials.json"))

    mat1 = Material(id="C25/30", name="Calcestruzzo C25/30", type="concrete", properties={"fck": 25.0})
    mat2 = Material(id="C30/37", name="Calcestruzzo C30/37", type="concrete", properties={"fck": 30.0})
    mat3 = Material(id="B450C", name="Acciaio B450C", type="steel", properties={"fyk": 450.0})

    material_repo.add(mat1)
    material_repo.add(mat2)
    material_repo.add(mat3)

    print(f"✓ Aggiunti {len(material_repo.get_all())} materiali")

    print("\n" + "=" * 70)
    print("  ISTRUZIONI")
    print("=" * 70)
    print("\n1. Nella finestra principale, clicca su 'File → Esporta backup...'")
    print("2. Scegli cosa esportare:")
    print("   • Sezioni: esporta solo le sezioni (JSON o CSV)")
    print("   • Materiali: esporta solo i materiali (JSON)")
    print("   • Entrambi: crea due file separati")
    print("3. Scegli il percorso e il nome del file")
    print("4. Verifica il messaggio di conferma")
    print("\n" + "=" * 70 + "\n")

    # Avvia la GUI
    serializer = CsvSectionSerializer()
    window = ModuleSelectorWindow(section_repo, serializer, material_repo)

    print("GUI avviata. Chiudi la finestra per terminare.\n")
    window.mainloop()

    print("\n✓ Demo completato!")
    print(f"✓ File temporanei: {temp_path}")
    print("  (verranno eliminati automaticamente alla chiusura)\n")


if __name__ == "__main__":
    main()
