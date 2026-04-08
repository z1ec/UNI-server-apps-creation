from fastapi import Depends, FastAPI

from basic_auth import verify_basic_credentials


app = FastAPI(title="KR-3 Task 6.1")


@app.get("/login")
def login(_: str = Depends(verify_basic_credentials)) -> dict[str, str]:
    return {"message": "You got my secret, welcome"}
