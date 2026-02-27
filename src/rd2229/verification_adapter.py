"""Adapter between UI VM and verification engine (skeleton).

This adapter will later translate viewmodels into engine inputs.
"""

from __future__ import annotations

from .viewmodels.verification_vm import VerificationViewModel


class VerificationAdapter:
    def __init__(self, vm: VerificationViewModel) -> None:
        self.vm = vm

    def prepare(self) -> dict:
        # minimal adapter behaviour for tests
        return {"prepared_name": self.vm.model.name}
