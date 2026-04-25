# app/training/bus.py
# Shared gui_bus singleton — NullBus until init_bus() is called at startup.


class _NullBus:
    def put(self, *_, **__):
        pass


gui_bus = _NullBus()


def init_bus(real_bus) -> None:
    global gui_bus
    gui_bus = real_bus
