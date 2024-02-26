from fastapi import APIRouter

from model.datasets import Datasets


router = APIRouter()


@router.get("/dataset/list")
async def dataset_list():
    return await Datasets.list()
