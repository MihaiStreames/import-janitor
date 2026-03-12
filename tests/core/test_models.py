from janitor.models import Import
from janitor.models import ImportKind


def test_import_is_hashable():
    # frozen dataclass must be hashable for use in sets/graph nodes
    imp = Import(kind=ImportKind.FROM, module="os.path", names=("join",))
    assert hash(imp)


def test_cycle_str():
    from janitor.models import Cycle

    c = Cycle(modules=["a", "b", "c"])
    assert str(c) == "a → b → c → a"
