from types import SimpleNamespace

from src.utils.background import BackgroundExecutor


def test_background_executor_callbacks_are_scheduled():
    called = SimpleNamespace(value=None)

    class DummyRoot:
        def __init__(self):
            self.scheduled = []

        def after(self, _ms, cb):
            # immediate call for unit test determinism
            cb()

    root = DummyRoot()

    def work(x):
        return x * 2

    def cb(res):
        called.value = res

    bg = BackgroundExecutor(max_workers=2)
    fut = bg.submit(work, 3, callback=cb, tk_root=root)
    fut.result(timeout=3)
    assert called.value == 6
    bg.shutdown()
