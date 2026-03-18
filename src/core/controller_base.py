"""
ControllerBase — base controller per moduli dell'applicazione

Fornisce funzionalità di base per il pattern controller: lifecycle,
registrazione listener, dispatch di eventi, e storage di stato.
Questo modulo deve essere utilizzato come base per tutti i controller
nei vari moduli dell'app.
"""
from typing import Callable, Dict, Any, List

class ControllerBase:
    def __init__(self):
        self._listeners: Dict[str, List[Callable[..., None]]] = {}
        self.state: Dict[str, Any] = {}
        self.running: bool = False

    def start(self) -> None:
        """Avvia il controller (lifecycle)."""
        self.running = True

    def stop(self) -> None:
        """Ferma il controller."""
        self.running = False

    def on(self, event: str, callback: Callable[..., None]) -> None:
        """Registra un listener per l'evento specificato."""
        if event not in self._listeners:
            self._listeners[event] = []
        self._listeners[event].append(callback)

    def off(self, event: str, callback: Callable[..., None]) -> None:
        """Rimuove un listener registrato."""
        if event in self._listeners and callback in self._listeners[event]:
            self._listeners[event].remove(callback)

    def emit(self, event: str, *args, **kwargs) -> None:
        """Notifica tutti i listener dell'evento."""
        for cb in list(self._listeners.get(event, [])):
            try:
                cb(*args, **kwargs)
            except Exception:
                # non propagare eccezioni dei listener
                pass

    def set_state(self, key: str, value: Any) -> None:
        self.state[key] = value
        self.emit('state_changed', key, value)

    def get_state(self, key: str, default: Any = None) -> Any:
        return self.state.get(key, default)
