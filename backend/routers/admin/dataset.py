from fastapi import APIRouter
from typing import List

from db import limiter
from model.datasets import Datasets


router = APIRouter()


@router.get("/dataset/list")
@limiter.exempt
async def dataset_list() -> List[Datasets]:
    return await Datasets.list()
