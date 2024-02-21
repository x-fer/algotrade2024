import pytest
from unittest.mock import AsyncMock, patch
from model import Datasets
from model.dataset_data import DatasetData
from fastapi import HTTPException

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
    with patch.object(DatasetData, 'count', AsyncMock(return_value=11)):
        result = await Datasets.validate_ticks(dataset_id, min_ticks)

    assert result == dataset_id


@pytest.mark.asyncio
async def test_ensure_ticks_not_enough_ticks():
    dataset_id = 1
    min_ticks = 10
    with patch.object(DatasetData, 'count', AsyncMock(return_value=9)):
        with pytest.raises(HTTPException) as e:
            await Datasets.validate_ticks(dataset_id, min_ticks)
        assert e.value.status_code == 400
