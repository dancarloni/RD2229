from src.rd2229.verification_adapter import VerificationAdapter
from src.rd2229.viewmodels.verification_vm import VerificationViewModel


def test_verification_vm_and_adapter():
    vm = VerificationViewModel()
    assert vm.run()["status"] == "ok"
    adapter = VerificationAdapter(vm)
    assert adapter.prepare()["prepared_name"] == vm.model.name
