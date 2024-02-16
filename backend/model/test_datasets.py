import pytest
from unittest.mock import MagicMock, patch
from db.table import Table
from model import Datasets


@pytest.mark.asyncio
async def test_exists_dataset_exists():
    dataset_id = 1
    mock_datasets_get = MagicMock()
    mock_datasets_get.return_value = {'dataset_id': dataset_id}
    with patch.object(Table, 'get', mock_datasets_get):
        exists = await Datasets.exists(dataset_id)

    assert exists


@pytest.mark.asyncio
async def test_exists_dataset_not_exists():
    dataset_id = 1
    mock_datasets_get = MagicMock(side_effect=Exception())
    with patch.object(Table, 'get', mock_datasets_get):
        exists = await Datasets.exists(dataset_id)

    assert not exists


@pytest.mark.asyncio
async def test_validate_string_valid_dataset():
    dataset_string = "valid_dataset"
    mock_datasets_exists = MagicMock(return_value=True)
    with patch.object(Datasets, 'exists', mock_datasets_exists):
        validated_string = await Datasets.validate_string(dataset_string)

    assert validated_string == dataset_string


@pytest.mark.asyncio
async def test_validate_string_invalid_dataset():
    dataset_string = "invalid_dataset"
    mock_datasets_exists = MagicMock(return_value=False)
    with patch.object(Datasets, 'exists', mock_datasets_exists):
        with pytest.raises(Exception):
            await Datasets.validate_string(dataset_string)


@pytest.mark.asyncio
async def test_ensure_ticks_enough_ticks():
    dataset_string = "valid_dataset"
    min_ticks = 10
    mock_datasets_count = MagicMock(return_value=12)
    with patch.object(Datasets, 'count', mock_datasets_count):
        result = await Datasets.ensure_ticks(dataset_string, min_ticks)

    assert result == dataset_string


@pytest.mark.asyncio
async def test_ensure_ticks_not_enough_ticks():
    dataset_string = "valid_dataset"
    min_ticks = 10
    mock_datasets_count = MagicMock(return_value=8)
    with patch.object(Datasets, 'count', mock_datasets_count):
        with pytest.raises(Exception):
            await Datasets.ensure_ticks(dataset_string, min_ticks)
