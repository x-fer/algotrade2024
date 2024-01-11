from fastapi import APIRouter

# DATASET PATHS

# GET	/admin/dataset/list	-	[{"id": [id], "name": [name]}, {}, {}, {}]

router = APIRouter()


@router.get("/dataset/list")
async def dataset_list():
    return {"message": "Hello World"}
