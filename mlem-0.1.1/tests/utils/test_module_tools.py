from typing import ClassVar

import numpy
import pytest
from pydantic import BaseModel

from mlem.utils.importing import import_module
from mlem.utils.module import (
    check_pypi_module,
    get_module_repr,
    get_module_version,
    get_object_module,
    get_object_requirements,
    is_builtin_module,
    is_extension_module,
    is_installable_module,
    is_local_module,
    is_mlem_module,
    is_private_module,
    is_pseudo_module,
)


class Obj:
    pass


# def test_analyze_module_imports(): #TODO: https://github.com/iterative/mlem/issues/44
#     reqs = analyze_module_imports('tests.utils.test_module_tools')
#     assert reqs == {get_module_repr(pytest)}


def test_check_pypi_module():
    assert check_pypi_module("numpy", "1.17.3")
    assert check_pypi_module("pandas")

    assert not check_pypi_module("my-super-module", warn_on_error=False)
    assert not check_pypi_module("pandas", "100.200.300", warn_on_error=False)

    with pytest.raises(ValueError):
        check_pypi_module("my-super-module", raise_on_error=True)

    with pytest.raises(ImportError):
        check_pypi_module("pandas", "100.200.300", raise_on_error=True)


def test_module_representation():
    from setup import setup_args

    for module in setup_args["install_requires"]:
        mod_name = module.split("==")[0]
        try:
            mod = import_module(mod_name)
            repr = get_module_repr(mod)
            if "=" in module:
                assert module == repr
            else:
                assert module == repr.split("==")[0]
        except (ImportError, NameError):
            continue


def test_is_installed_module():
    import builtins
    import pickle

    import opcode
    import requests

    assert not is_installable_module(pickle)
    assert not is_installable_module(builtins)
    assert not is_installable_module(opcode)
    assert is_installable_module(requests), requests.__file__

    mlem_module = get_object_module(get_object_module)
    assert not is_installable_module(mlem_module)


def test_is_builtin_module():
    import builtins
    import pickle

    import opcode
    import requests

    assert is_builtin_module(pickle)
    assert is_builtin_module(builtins)
    assert is_builtin_module(opcode)
    assert not is_builtin_module(requests), requests.__file__

    mlem_module = get_object_module(get_object_module)
    assert not is_builtin_module(mlem_module)


def test_is_private_module():
    import pickle as p

    import _datetime as d

    assert not is_private_module(p)
    assert is_private_module(d)


def test_is_pseudo_module():
    import __future__

    import pickle

    assert not is_pseudo_module(pickle)
    assert is_pseudo_module(__future__)


def test_is_extension_module():
    import pickle

    import _ctypes
    import _datetime

    assert not is_extension_module(pickle)
    assert is_extension_module(_datetime)
    assert is_extension_module(_ctypes)


def test_is_local_module():
    import pickle
    import sys

    import requests

    assert not is_local_module(sys)
    assert not is_local_module(pickle)
    assert not is_local_module(requests)
    # assert is_local_module(sys.modules[__name__])
    # TODO: https://github.com/iterative/mlem/issues/44
    #  explore why it fails
    assert not is_local_module(sys.modules["__future__"])
    assert not is_local_module(sys.modules[is_local_module.__module__])


def test_is_mlem_module():
    import sys

    import requests

    import mlem
    from mlem.utils import module

    assert is_mlem_module(mlem)
    assert is_mlem_module(module)

    assert not is_mlem_module(sys)
    assert not is_mlem_module(requests)


def test_module_version():
    # we do not check for concrete version as they could differ
    assert get_module_version(import_module("numpy")) is not None
    assert get_module_version(import_module("dill")) is not None
    # responses doesn't have __version__ attr, thus heuristics should be applied here
    # assert get_module_version(import_module('responses')) is not None
    # TODO: https://github.com/iterative/mlem/issues/44


class Clazz:
    field: ClassVar = numpy


class ModelClazz(BaseModel):
    field: ClassVar = numpy


def test_get_object_requirements__classvar():
    assert get_object_requirements(Clazz).modules == ["numpy"]
    assert get_object_requirements(Clazz()).modules == ["numpy"]


def test_get_object_requirements__classvar_in_model():
    assert get_object_requirements(ModelClazz).modules == ["numpy"]
    assert get_object_requirements(ModelClazz()).modules == ["numpy"]


# Copyright 2019 Zyfra
# Copyright 2021 Iterative
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
