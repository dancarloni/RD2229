from src.rd2229 import logging_bridge, plugin_registry


def test_logging_and_plugin_registry():
    # plugin registry basic
    def dummy():
        return "ok"

    plugin_registry.register("d", dummy)
    assert "d" in plugin_registry.list_plugins()
    assert plugin_registry.get("d")() == "ok"

    # logging bridge exists (no assertions on output)
    logging_bridge.log_info("test message")
