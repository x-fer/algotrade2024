from enum import Enum
import pytest
from dataclasses import dataclass
from model.enum_type import EnumType


class ExampleEnum(Enum):
    VALUE1 = "VALUE1"
    VALUE2 = "VALUE2"


class AnotherEnum(Enum):
    OPTION1 = 'Option 1'
    OPTION2 = 'Option 2'


class ExampleField(EnumType):
    cls = ExampleEnum


class AnotherField(EnumType):
    cls = AnotherEnum


@dataclass
class ExampleClass():
    example_field: ExampleField
    another_field: AnotherField


def test_enum_type_default():
    instance = ExampleClass(example_field='VALUE2', another_field='Option 2')

    assert instance.example_field == 'VALUE2'
    assert instance.another_field == 'Option 2'
