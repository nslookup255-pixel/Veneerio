from vnr.core.events import Events as E

def test_on_and_emit():
    events = E()
    called = []

    def listener(arg):
        called.append(arg)

    events.on("test_event", listener)
    events.emit("test_event", 42)

    assert called == [42]

def test_off():
    events = E()
    called = []

    def listener(arg):
        called.append(arg)

    events.on("test_event", listener)
    events.off("test_event", listener)
    events.emit("test_event", 42)

    assert called == []

def test_once():
    events = E()
    called = []

    def listener(arg):
        called.append(arg)

    events.once("test_event", listener)
    events.emit("test_event", 42)
    events.emit("test_event", 43)

    assert called == [42]

def test_clear():
    events = E()
    called = []

    def listener(arg):
        called.append(arg)

    events.on("test_event", listener)
    events.clear()
    events.emit("test_event", 42)

    assert called == []

def test_emit_passes_arg():
    events = E()
    called = []

    def listener(arg1, arg2):
        called.append((arg1, arg2))

    events.on("test_event", listener)
    events.emit("test_event", 1, 2)

    assert called == [(1, 2)]

def test_emit_calls_remaining_listeners_when_one_removes_itself():
    events = E()
    called = []

    def first():
        called.append("first")
        events.off("test_event", first)

    def second():
        called.append("second")

    events.on("test_event", first)
    events.on("test_event", second)
    events.emit("test_event")

    assert called == ["first", "second"]

def test_once_listener_is_removed_when_it_raises():
    events = E()
    calls = []

    def listener():
        calls.append("called")
        raise RuntimeError("failure")

    events.once("test_event", listener)

    for _ in range(2):
        try:
            events.emit("test_event")
        except RuntimeError:
            pass

    assert calls == ["called"]

if __name__ == "__main__":
    test_on_and_emit()
    test_off()
    test_once()
    test_clear()
    test_emit_passes_arg()
    print("All tests passed.")