from dataclasses import asdict
from fastapi import APIRouter
from typing import List
from model import DatasetData

from db import limiter
from model.datasets import Datasets


router = APIRouter()


@router.get("/dataset/list")
@limiter.exempt
async def dataset_list() -> List[Datasets]:
    return [
        {**asdict(x),
         "max_ticks": await DatasetData.count(dataset_id=x.dataset_id)
         } for x in await Datasets.list()
    ]
