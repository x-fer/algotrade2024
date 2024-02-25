from fastapi import APIRouter

from model.datasets import Datasets

# DATASET PATHS

# GET	/admin/dataset/list	-	[{"id": [id], "name": [name]}, {}, {}, {}]

router = APIRouter()


@router.get("/dataset/list")
async def dataset_list():
    return await Datasets.list()
