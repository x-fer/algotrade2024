import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from db.table import Table
from model import Datasets
from model.dataset_data import DatasetData

# @classmethod
# async def ensure_ticks(cls, dataset_id, min_ticks):

#     row = await DatasetData.list(dataset_id=dataset_id)

#     if len(row) < min_ticks:
#         raise Exception("Dataset does not have enough ticks")

#     return dataset_id


@pytest.mark.asyncio
async def test_ensure_ticks_enough_ticks():
    dataset_id = 1
    min_ticks = 10
    mock_dataset_data_list = AsyncMock(
        return_value=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
    with patch.object(DatasetData, 'list', mock_dataset_data_list):
        result = await Datasets.ensure_ticks(dataset_id, min_ticks)

    assert result == dataset_id


@pytest.mark.asyncio
async def test_ensure_ticks_not_enough_ticks():
    dataset_id = 1
    min_ticks = 10
    mock_dataset_data_list = AsyncMock(
        return_value=[1, 2, 3, 4, 5, 6, 7, 8, 9])
    with patch.object(DatasetData, 'list', mock_dataset_data_list):
        with pytest.raises(Exception) as e:
            await Datasets.ensure_ticks(dataset_id, min_ticks)
    assert str(e.value) == "Dataset does not have enough ticks"
