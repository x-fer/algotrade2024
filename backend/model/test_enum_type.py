from enum import Enum
import pytest
from model.enum_type import enum_type


class ExampleEnum(Enum):
    VALUE1 = 1
    VALUE2 = 2


class AnotherEnum(Enum):
    OPTION1 = 'Option 1'
    OPTION2 = 'Option 2'


@pytest.fixture
def example_class():
    class ExampleClass:
        example_field = enum_type(ExampleEnum)
        another_field = enum_type(AnotherEnum)

        def __init__(self, example_field=None, another_field=None):
            self.example_field = example_field
            self.another_field = another_field

    return ExampleClass


def test_enum_type_default(example_class):
    instance = example_class()

    assert instance.example_field is None
    assert instance.another_field is None

    instance.example_field = 'VALUE1'
    instance.another_field = 'Option 1'

    instance = example_class(example_field='VALUE2', another_field='Option 2')

    assert instance.example_field == 'VALUE2'
    assert instance.another_field == 'Option 2'
