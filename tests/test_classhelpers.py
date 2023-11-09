import pathlib
import types

import pytest

from mknodes.utils.classhelpers import import_file, to_class, to_dotted_path, to_module


def test_to_module_with_str():
    module = to_module("math")
    assert isinstance(module, types.ModuleType)
    assert module.__name__ == "math"


def test_to_module_with_sequence():
    module = to_module(("importlib", "metadata"))
    assert isinstance(module, types.ModuleType)
    assert module.__name__ == "importlib.metadata"


def test_to_module_with_module():
    import math

    module = to_module(math)
    assert isinstance(module, types.ModuleType)
    assert module.__name__ == "math"


def test_to_module_with_nonexistent_module():
    with pytest.raises(ImportError):
        to_module("nonexistent_module", return_none=False)


def test_to_module_with_nonexistent_module_return_none():
    module = to_module("nonexistent_module", return_none=True)
    assert module is None


def test_to_module_with_invalid_type():
    with pytest.raises(TypeError):
        to_module(123)


def test_to_class_with_type():
    from collections import defaultdict

    klass = to_class(defaultdict)
    assert klass == defaultdict


def test_to_class_with_str_colon():
    klass = to_class("collections:defaultdict")
    from collections import defaultdict

    assert klass == defaultdict


def test_to_class_with_str_dot():
    klass = to_class("collections.defaultdict")
    from collections import defaultdict

    assert klass == defaultdict


def test_to_class_with_sequence():
    klass = to_class(("collections", "defaultdict"))
    from collections import defaultdict

    assert klass == defaultdict


def test_to_class_with_invalid_str():
    with pytest.raises(ImportError):
        to_class("nonexistent_module.nonexistent_class")


def test_to_class_with_invalid_type():
    with pytest.raises(TypeError):
        to_class(123)


def test_to_dotted_path_with_sequence():
    result = to_dotted_path(("collections", "defaultdict"))
    assert result == "collections.defaultdict"


def test_to_dotted_path_with_str():
    result = to_dotted_path("collections.defaultdict")
    assert result == "collections.defaultdict"


def test_to_dotted_path_with_module():
    import math

    result = to_dotted_path(math)
    assert result == "math"


def test_to_dotted_path_with_class():
    from collections import defaultdict

    result = to_dotted_path(defaultdict)
    assert result == "collections.defaultdict"


def test_to_dotted_path_with_callable():
    result = to_dotted_path(to_dotted_path)
    assert result == "mknodes.utils.classhelpers.to_dotted_path"


def test_to_dotted_path_with_invalid_type():
    with pytest.raises(TypeError):
        to_dotted_path(123)


def test_import_file_with_valid_path():
    # Create a temporary python file
    path = pathlib.Path(__file__).parent / "temp.py"
    with path.open("w") as f:
        f.write("def temp_func():\n    return 'Hello, World!'")
    module = import_file(path)
    assert isinstance(module, types.ModuleType)
    assert module.__name__ == "temp"
    assert hasattr(module, "temp_func")
    assert module.temp_func() == "Hello, World!"

    # Clean up the temporary file
    path.unlink()


def test_import_file_with_invalid_path():
    with pytest.raises(FileNotFoundError):
        import_file("nonexistent.py")


def test_import_file_with_non_python_file():
    # Create a temporary text file
    path = pathlib.Path(__file__).parent / "temp.txt"
    with path.open("w") as f:
        f.write("Hello, World!")

    with pytest.raises(RuntimeError):
        import_file("temp.txt")

    # Clean up the temporary file
    path.unlink()


def test_import_file_with_directory():
    with pytest.raises(IsADirectoryError):
        import_file(".")


def test_import_file_with_none():
    with pytest.raises(TypeError):
        import_file(None)


def test_import_file_with_non_string():
    with pytest.raises(TypeError):
        import_file(123)
