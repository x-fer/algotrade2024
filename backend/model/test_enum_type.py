import pytest
from enum import Enum

from model.enum_type import get_enum


class ExampleEnum(Enum):
    VALUE1 = "VALUE1"
    VALUE2 = "VALUE2"


class AnotherEnum(Enum):
    OPTION1 = 'Option 1'
    OPTION2 = 'Option 2'


def test_enum_type_default():
    instance = get_enum("VALUE1", ExampleEnum)

    assert instance == ExampleEnum.VALUE1

    instance = get_enum("Option 1", ExampleEnum, AnotherEnum)

    assert instance == AnotherEnum.OPTION1

    instance = get_enum(ExampleEnum.VALUE1, ExampleEnum)

    assert instance == ExampleEnum.VALUE1

    with pytest.raises(ValueError):
        instance = get_enum(AnotherEnum.OPTION1, ExampleEnum)
    
    with pytest.raises(ValueError):
        instance = get_enum("blabla", ExampleEnum)