"""Funzioni di input/output per le sezioni in formato CSV."""

import csv
import logging
from uuid import uuid4

from ..config import CSV_HEADERS
from ..domain import (
    CircularHollowSection,
    CircularSection,
    CSection,
    InvertedTSection,
    InvertedVSection,
    ISection,
    LSection,
    PiSection,
    RectangularHollowSection,
    RectangularSection,
    Section,
    TSection,
    VSection,
)

logger = logging.getLogger(__name__)


def create_section_from_dict(data: dict[str, str]) -> Section:
    """Factory per creare una sezione da un dizionario letto dal CSV.

    Args:
        data: Dizionario con i dati della sezione dal CSV

    Returns:
        Istanza della sezione appropriata

    Raises:
        ValueError: Se il tipo di sezione non è riconosciuto o i dati sono invalidi
    """
    section_type = (data.get("section_type") or "").strip().upper()
    name = (data.get("name") or "").strip() or section_type
    note = (data.get("note") or "").strip()
    rotation_angle_deg = float(data.get("rotation_angle_deg") or 0)

    # Crea la sezione in base al tipo
    if section_type == "RECTANGULAR":
        width = float(data.get("width") or 0)
        height = float(data.get("height") or 0)
        _ensure_positive(width, "width")
        _ensure_positive(height, "height")
        dimensions = {"width": width, "height": height}
        section = RectangularSection(
            section_id=str(uuid4()),
            name=name,
            dimensions=dimensions,
            rotation_angle_deg=rotation_angle_deg,
            note=note,
        )

    # Crea la sezione in base al tipo
    if section_type == "RECTANGULAR":
        width = float(data.get("width") or 0)
        height = float(data.get("height") or 0)
        _ensure_positive(width, "width")
        _ensure_positive(height, "height")
        dimensions = {"width": width, "height": height}
        section = RectangularSection(
            section_id=str(uuid4()),
            name=name,
            dimensions=dimensions,
            rotation_angle_deg=rotation_angle_deg,
            note=note,
        )

    elif section_type == "CIRCULAR":
        diameter = float(data.get("diameter") or 0)
        _ensure_positive(diameter, "diameter")
        dimensions = {"diameter": diameter}
        section = CircularSection(
            section_id=str(uuid4()),
            name=name,
            dimensions=dimensions,
            rotation_angle_deg=rotation_angle_deg,
            note=note,
        )

    elif section_type == "T_SECTION":
        flange_width = float(data.get("flange_width") or 0)
        flange_thickness = float(data.get("flange_thickness") or 0)
        web_thickness = float(data.get("web_thickness") or 0)
        web_height = float(data.get("web_height") or 0)
        _ensure_positive(flange_width, "flange_width")
        _ensure_positive(flange_thickness, "flange_thickness")
        _ensure_positive(web_thickness, "web_thickness")
        _ensure_positive(web_height, "web_height")
        dimensions = {
            "flange_width": flange_width,
            "flange_thickness": flange_thickness,
            "web_thickness": web_thickness,
            "web_height": web_height,
        }
        section = TSection(
            section_id=str(uuid4()),
            name=name,
            dimensions=dimensions,
            rotation_angle_deg=rotation_angle_deg,
            note=note,
        )

    elif section_type == "L_SECTION":
        width = float(data.get("width") or 0)
        height = float(data.get("height") or 0)
        # Usa campi specifici per L-section o fallback per compatibilità
        t_horizontal_val = data.get("t_horizontal") or data.get("flange_thickness")
        t_vertical_val = data.get("t_vertical") or data.get("web_thickness")
        t_horizontal = float(t_horizontal_val or 0)
        t_vertical = float(t_vertical_val or 0)
        _ensure_positive(width, "width")
        _ensure_positive(height, "height")
        _ensure_positive(t_horizontal, "t_horizontal")
        _ensure_positive(t_vertical, "t_vertical")
        dimensions = {
            "width": width,
            "height": height,
            "t_horizontal": t_horizontal,
            "t_vertical": t_vertical,
        }
        section = LSection(
            section_id=str(uuid4()),
            name=name,
            dimensions=dimensions,
            rotation_angle_deg=rotation_angle_deg,
            note=note,
        )

    elif section_type == "I_SECTION":
        flange_width = float(data.get("flange_width") or 0)
        flange_thickness = float(data.get("flange_thickness") or 0)
        web_height = float(data.get("web_height") or 0)
        web_thickness = float(data.get("web_thickness") or 0)
        _ensure_positive(flange_width, "flange_width")
        _ensure_positive(flange_thickness, "flange_thickness")
        _ensure_positive(web_height, "web_height")
        _ensure_positive(web_thickness, "web_thickness")
        dimensions = {
            "flange_width": flange_width,
            "flange_thickness": flange_thickness,
            "web_height": web_height,
            "web_thickness": web_thickness,
        }
        section = ISection(
            section_id=str(uuid4()),
            name=name,
            dimensions=dimensions,
            rotation_angle_deg=rotation_angle_deg,
            note=note,
        )

    elif section_type == "PI_SECTION":
        flange_width = float(data.get("flange_width") or 0)
        flange_thickness = float(data.get("flange_thickness") or 0)
        web_height = float(data.get("web_height") or 0)
        web_thickness = float(data.get("web_thickness") or 0)
        _ensure_positive(flange_width, "flange_width")
        _ensure_positive(flange_thickness, "flange_thickness")
        _ensure_positive(web_height, "web_height")
        _ensure_positive(web_thickness, "web_thickness")
        dimensions = {
            "flange_width": flange_width,
            "flange_thickness": flange_thickness,
            "web_height": web_height,
            "web_thickness": web_thickness,
        }
        section = PiSection(
            section_id=str(uuid4()),
            name=name,
            dimensions=dimensions,
            rotation_angle_deg=rotation_angle_deg,
            note=note,
        )

    elif section_type == "INVERTED_T_SECTION":
        flange_width = float(data.get("flange_width") or 0)
        flange_thickness = float(data.get("flange_thickness") or 0)
        web_thickness = float(data.get("web_thickness") or 0)
        web_height = float(data.get("web_height") or 0)
        _ensure_positive(flange_width, "flange_width")
        _ensure_positive(flange_thickness, "flange_thickness")
        _ensure_positive(web_thickness, "web_thickness")
        _ensure_positive(web_height, "web_height")
        dimensions = {
            "flange_width": flange_width,
            "flange_thickness": flange_thickness,
            "web_thickness": web_thickness,
            "web_height": web_height,
        }
        section = InvertedTSection(
            section_id=str(uuid4()),
            name=name,
            dimensions=dimensions,
            rotation_angle_deg=rotation_angle_deg,
            note=note,
        )

    elif section_type == "C_SECTION":
        width = float(data.get("width") or 0)
        height = float(data.get("height") or 0)
        flange_thickness = float(data.get("flange_thickness") or 0)
        web_thickness = float(data.get("web_thickness") or 0)
        _ensure_positive(width, "width")
        _ensure_positive(height, "height")
        _ensure_positive(flange_thickness, "flange_thickness")
        _ensure_positive(web_thickness, "web_thickness")
        dimensions = {
            "width": width,
            "height": height,
            "flange_thickness": flange_thickness,
            "web_thickness": web_thickness,
        }
        section = CSection(
            section_id=str(uuid4()),
            name=name,
            dimensions=dimensions,
            rotation_angle_deg=rotation_angle_deg,
            note=note,
        )

    elif section_type == "CIRCULAR_HOLLOW":
        outer_diameter = float(data.get("diameter") or data.get("outer_diameter") or 0)
        thickness = float(data.get("web_thickness") or data.get("thickness") or 0)
        _ensure_positive(outer_diameter, "outer_diameter")
        _ensure_positive(thickness, "thickness")
        dimensions = {"outer_diameter": outer_diameter, "thickness": thickness}
        section = CircularHollowSection(
            section_id=str(uuid4()),
            name=name,
            dimensions=dimensions,
            rotation_angle_deg=rotation_angle_deg,
            note=note,
        )

    elif section_type == "RECTANGULAR_HOLLOW":
        width = float(data.get("width") or 0)
        height = float(data.get("height") or 0)
        thickness = float(data.get("web_thickness") or data.get("thickness") or 0)
        _ensure_positive(width, "width")
        _ensure_positive(height, "height")
        _ensure_positive(thickness, "thickness")
        dimensions = {"width": width, "height": height, "thickness": thickness}
        section = RectangularHollowSection(
            section_id=str(uuid4()),
            name=name,
            dimensions=dimensions,
            rotation_angle_deg=rotation_angle_deg,
            note=note,
        )

    elif section_type == "V_SECTION":
        width = float(data.get("width") or 0)
        height = float(data.get("height") or 0)
        thickness = float(data.get("web_thickness") or data.get("thickness") or 0)
        _ensure_positive(width, "width")
        _ensure_positive(height, "height")
        _ensure_positive(thickness, "thickness")
        dimensions = {"width": width, "height": height, "thickness": thickness}
        section = VSection(
            section_id=str(uuid4()),
            name=name,
            dimensions=dimensions,
            rotation_angle_deg=rotation_angle_deg,
            note=note,
        )

    elif section_type == "INVERTED_V_SECTION":
        width = float(data.get("width") or 0)
        height = float(data.get("height") or 0)
        thickness = float(data.get("web_thickness") or data.get("thickness") or 0)
        _ensure_positive(width, "width")
        _ensure_positive(height, "height")
        _ensure_positive(thickness, "thickness")
        dimensions = {"width": width, "height": height, "thickness": thickness}
        section = InvertedVSection(
            section_id=str(uuid4()),
            name=name,
            dimensions=dimensions,
            rotation_angle_deg=rotation_angle_deg,
            note=note,
        )

    else:
        raise ValueError(f"Tipo di sezione non riconosciuto: {section_type}")

    # Gestisci valori shear persistiti
    k_y = _safe_float(data, "kappa_y")
    k_z = _safe_float(data, "kappa_z")
    A_y_csv = _safe_float(data, "A_y")
    A_z_csv = _safe_float(data, "A_z")

    # Imposta fattori shear se presenti
    if k_y is not None:
        # Nota: nella nuova architettura, i kappa sono gestiti automaticamente
        # Qui potremmo estendere Section per supportare override se necessario
        pass
    if k_z is not None:
        pass

    # Deriva kappa da A_y/area se necessario per compatibilità
    area_csv = _safe_float(data, "area")
    if k_y is None and A_y_csv is not None and area_csv and area_csv > 0:
        # Potrebbe essere necessario aggiungere supporto per override shear
        pass
    if k_z is None and A_z_csv is not None and area_csv and area_csv > 0:
        pass

    # Imposta ID se presente
    section_id = (data.get("id") or "").strip()
    if section_id:
        section.id = section_id
    else:
        section.id = str(uuid4())

    return section


def _safe_float(data: dict[str, str], key: str) -> float | None:
    """Converte in float in modo sicuro."""
    v = data.get(key)
    if v is None or v == "":
        return None
    try:
        return float(v)
    except Exception:
        logger.debug("Valore float non valido per %s: %r", key, v)
        return None


def _ensure_positive(value: float, label: str) -> None:
    """Assicura che il valore sia positivo."""
    if value <= 0:
        raise ValueError(f"{label} deve essere positivo")


def export_sections_to_csv(sections: list[Section], filepath: str) -> None:
    """Esporta una lista di sezioni in un file CSV.

    Args:
        sections: Lista delle sezioni da esportare
        filepath: Percorso del file CSV di destinazione
    """
    with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=CSV_HEADERS)
        writer.writeheader()

        for section in sections:
            row = section.to_dict()
            # Converte i valori in stringhe per CSV
            csv_row = {}
            for key, value in row.items():
                if value is None:
                    csv_row[key] = ""
                elif isinstance(value, float):
                    csv_row[key] = f"{value:.6g}"
                else:
                    csv_row[key] = str(value)
            writer.writerow(csv_row)


def import_sections_from_csv(filepath: str) -> list[Section]:
    """Importa sezioni da un file CSV.

    Args:
        filepath: Percorso del file CSV da leggere

    Returns:
        Lista delle sezioni importate
    """
    sections = []
    with open(filepath, encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                section = create_section_from_dict(row)
                sections.append(section)
            except Exception as e:
                logger.error("Errore nell'importazione della riga: %s", e)
                continue
    return sections
