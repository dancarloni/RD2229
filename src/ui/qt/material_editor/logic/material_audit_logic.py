"""
MaterialAuditLogic — Gestione audit trail, logging, conferme
"""

from typing import List, Dict, Any

class MaterialAuditLogic:
    def __init__(self):
        self.log: List[Dict[str, Any]] = []

    def log_action(self, action: str, data: Any):
        self.log.append({'action': action, 'data': data})

    def get_log(self) -> List[Dict[str, Any]]:
        return self.log

    def confirm_action(self, action: str, summary: str) -> bool:
        # Placeholder: implement dialog di conferma
        print(f"Conferma: {action} — {summary}")
        return True

# Per test rapido
if __name__ == "__main__":
    audit = MaterialAuditLogic()
    audit.log_action('delete', {'id': '123'})
    print(audit.get_log())
    audit.confirm_action('reset_layout', 'Ripristina layout predefinito')
