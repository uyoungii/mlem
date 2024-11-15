from typing import Any, ClassVar

import pytest

import mlem
from mlem.core.dataset_type import DatasetType, DatasetWriter
from mlem.core.model import Argument, Signature
from mlem.core.requirements import Requirements
from mlem.runtime import Interface
from mlem.runtime.interface.base import SimpleInterface, expose


class Container(DatasetType):
    type: ClassVar = "test_container"
    field: int

    def serialize(self, instance: Any) -> dict:
        return {}

    def deserialize(self, obj: dict) -> Any:
        pass

    def get_requirements(self) -> Requirements:
        return Requirements.new([])

    def get_writer(self, **kwargs) -> "DatasetWriter":
        raise NotImplementedError()


@pytest.fixture
def interface() -> Interface:
    class MyInterface(SimpleInterface):
        @expose
        def method1(self, arg1: Container(field=5)) -> Container(field=5):  # type: ignore[valid-type]
            self.method2()
            return arg1

        def method2(self):
            pass

    return MyInterface()


def test_interface_descriptor__from_interface(interface: Interface):
    d = interface.get_descriptor()
    assert d.version == mlem.__version__
    sig = Signature(
        name="method1",
        args=[
            Argument(
                key="arg1",
                type=Container(field=5),
            )
        ],
        returns=Container(field=5),
    )
    assert d.methods == {"method1": sig}


def test_interface_descriptor__to_dict(interface: Interface):
    d = interface.get_descriptor()

    assert d.dict() == {
        "version": mlem.__version__,
        "methods": {
            "method1": {
                "name": "method1",
                "args": [
                    {
                        "key": "arg1",
                        "type": {"field": 5, "type": "test_container"},
                    }
                ],
                "returns": {"field": 5, "type": "test_container"},
            }
        },
    }
