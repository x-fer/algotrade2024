from dataclasses import asdict
from fastapi import APIRouter
from typing import List
from model import DatasetData

from db import limiter
from model import Datasets, DatasetData


router = APIRouter()


@router.get("/dataset/list")
@limiter.exempt
def dataset_list() -> List[Datasets]:
    return [
        {**x.dict(),
         "max_ticks":  DatasetData.find(DatasetData.dataset_id == x.dataset_id).count()
         } for x in Datasets.find().all()
    ]
