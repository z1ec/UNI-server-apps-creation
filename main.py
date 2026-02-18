from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from models import User, Feedback


app = FastAPI()

templates = Jinja2Templates(directory="templates")

# задание 1.1
# @app.get("/")
# async def root():
#     return {"message": "hello world"}


# задание 1.2
# @app.get("/", response_class=HTMLResponse)
# async def read_root(request: Request):
#     return templates.TemplateResponse(
#         "index.html",
#         {
#             "request": request,   # обязательно!
#             "title": "Home Page",
#             "name": "Vladimir"
#         }
#     )


#задание 1.3
# class Numbers(BaseModel):
#     num1: float
#     num2: float


# @app.post("/calculate")
# async def calculate(numbers: Numbers):
#     result = numbers.num1 + numbers.num2
#     return {"result": result}


#задание 1.4
# user = User(
#     name="Фомин Владимир",
#     id=1
# )


# @app.get("/users")
# async def get_user():
#     return user


# #задание 1.5
# @app.post("/user")
# async def create_user(user: User):
#     # Проверка совершеннолетия
#     is_adult = user.age >= 18

#     return {
#         "name": user.name,
#         "age": user.age,
#         "is_adult": is_adult
#     }


#задание 2.1-2.2
# feedbacks: list[Feedback] = []


# @app.post("/feedback")
# async def create_feedback(feedback: Feedback):
#     feedbacks.append(feedback)
#     return {"message": f"Спасибо, {feedback.name}! Ваш отзыв сохранён."}