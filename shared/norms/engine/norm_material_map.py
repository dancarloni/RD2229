"""
Mapping Norma → Materiali Compatibili.

Implementa il filtro di materiali compatibili per ogni norma.
Quando l'utente seleziona una norma (es. NTC2018), il dropdown materiali
mostra SOLO i materiali definiti per quella norma.

Struttura:
    NTC2018 → [C20/25, C25/30, C30/37, B450C, ...]
    RD2229  → [R200, R250, AQ42, ...]
    DM96    → [Cls 300, Cls 350, Acciaio Fe360, ...]
    ecc.

Questo evita combinazioni non normative (es. CLS secondo NTC2018
verificata con DM96).
"""


class NormMaterialMap:
    """
    Mapping centralizzato: norma → materiali compatibili.

    Mantiene mappature hard-coded aggiornate con i cataloghi
    in data/materials/catalogo_*.json
    """

    # Mapping norma → elenco IDs materiali disponibili nel catalogo
    _NORM_TO_MATERIALS: dict[str, set[str]] = {
        # NTC2018 — Normativa vigente
        "NTC2018": {
            # Calcestruzzo
            "C12/15",
            "C16/20",
            "C20/25",
            "C25/30",
            "C28/35",
            "C30/37",
            "C35/45",
            "C40/50",
            "C45/55",
            "C50/60",
            "C55/67",
            "C60/75",
            "C70/85",
            "C80/95",
            "C90/105",
            "C100/115",
            # Acciaio per armature
            "B450C",
            "B500B",
            "B500C",
            # Acciaio strutturale
            "S235",
            "S275",
            "S355",
            "S450",
        },
        # RD2229 — Regio Decreto 1939 (storico, ancora usato)
        "RD2229": {
            "R200",  # Resistenza 200 kg/cm²
            "R250",  # Resistenza 250 kg/cm²
            "R300",  # Resistenza 300 kg/cm²
            "AQ42",  # Acciaio qualità 42
            "AQ50",  # Acciaio qualità 50
        },
        # DM 1972 — D.M. 30/05/1972
        "DM72": {
            "Cls 150",
            "Cls 200",
            "Cls 250",
            "Cls 300",
            "FeB22k",
            "FeB32k",
            "FeB38k",
            "FeB44k",
        },
        # DM 1974 — D.M. 21/01/1974
        "DM74": {
            "Cls 150",
            "Cls 200",
            "Cls 250",
            "Cls 300",
            "Cls 350",
            "FeB22k",
            "FeB32k",
            "FeB38k",
            "FeB44k",
        },
        # DM 1996 — D.M. 09/01/1996
        "DM96": {
            # Calcestruzzo
            "Cls 200",
            "Cls 250",
            "Cls 300",
            "Cls 350",
            "Cls 400",
            "Cls 450",
            # Acciaio
            "Fe360",
            "Fe430",
            "Fe510",
            "FeB38k",
            "FeB44k",
        },
        # DM 1992 — D.M. 14/02/1992
        "DM92": {
            "Cls 250",
            "Cls 300",
            "Cls 350",
            "Cls 400",
            "Fe360",
            "Fe430",
            "Fe510",
        },
        # NTC2008 — Normativa Tecnica Costruzioni 2008
        "NTC2008": {
            "C12/15",
            "C16/20",
            "C20/25",
            "C25/30",
            "C30/37",
            "C35/45",
            "C40/50",
            "C45/55",
            "C50/60",
            "B450C",
            "B500B",
            "S235",
            "S275",
            "S355",
        },
        # Eurocode 2 (EN 1992-1-1:2004)
        "EN1992": {
            "C12/15",
            "C16/20",
            "C20/25",
            "C25/30",
            "C30/37",
            "C35/45",
            "C40/50",
            "C45/55",
            "C50/60",
            "B500B",
            "B500C",
        },
        # Eurocode 3 (EN 1993-1-1:2005)
        "EN1993": {
            "S235",
            "S275",
            "S355",
            "S420",
            "S460",
        },
        # DM Muratura 1987
        "DM87": {
            # Muratura (classi di malta, tipi laterizio)
            "M1",
            "M2",
            "M3",
            "M4",
            "M5",
            "Laterizio",
            "Cls-leggero",
            "Tufo",
        },
    }

    @classmethod
    def get_materials_for_norm(cls, norm_code: str) -> set[str]:
        """
        Restituisce materiali compatibili con una norma.

        Args:
            norm_code: Codice norma (es. "NTC2018", "RD2229")

        Returns:
            Set di IDs materiali disponibili per la norma
        """
        return cls._NORM_TO_MATERIALS.get(norm_code.upper(), set())

    @classmethod
    def is_compatible(cls, norm_code: str, material_id: str) -> bool:
        """
        Verifica se un materiale è compatibile con una norma.

        Args:
            norm_code: Codice norma
            material_id: ID materiale

        Returns:
            True se compatibile, False altrimenti
        """
        materials = cls.get_materials_for_norm(norm_code)
        return material_id in materials

    @classmethod
    def list_norms(cls) -> list[str]:
        """Elenca tutte le norme configurate."""
        return sorted(cls._NORM_TO_MATERIALS.keys())

    @classmethod
    def list_norms_for_material(cls, material_id: str) -> list[str]:
        """
        Restituisce le norme per cui un materiale è disponibile.

        Args:
            material_id: ID materiale

        Returns:
            Lista di codici norma
        """
        result = []
        for norm_code, materials in cls._NORM_TO_MATERIALS.items():
            if material_id in materials:
                result.append(norm_code)
        return sorted(result)


__all__ = ["NormMaterialMap"]
