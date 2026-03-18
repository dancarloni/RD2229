"""
MaterialExportLogic — Gestione esportazione, formato selezionabile, copia
"""

from typing import Dict, Any

class MaterialExportLogic:
    @staticmethod
    def export(material: Dict[str, Any], fmt: str = 'HTML') -> str:
        if fmt == 'HTML':
            return '<br>'.join(f'<b>{k}</b>: {v}' for k, v in material.items())
        elif fmt == 'Markdown':
            return '\n'.join(f'**{k}**: {v}' for k, v in material.items())
        elif fmt == 'CSV':
            return ','.join(str(material[k]) for k in material.keys())
        else:
            return '\n'.join(f'{k}: {v}' for k, v in material.items())

# Per test rapido
if __name__ == "__main__":
    mat = {'codice': 'C20/25', 'f_ck': 25.0, 'gamma_c': 1.5}
    for fmt in ['HTML', 'Markdown', 'CSV', 'Testo semplice']:
        print(f"\nFormato {fmt}:\n", MaterialExportLogic.export(mat, fmt))
