from fastapi import FastAPI
from model import ChatbotModel
from pydantic import BaseModel
import logging
from fastapi.exceptions import RequestValidationError
from fastapi.responses import PlainTextResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
import yaml

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(thread)d:%(threadName)s:%(process)d:%(message)s")
logger.addHandler(logging.StreamHandler())


app = FastAPI()

class RequestItem(BaseModel):
    """
    Request model for user query
    text : user query
    """

    text: str


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    
    return PlainTextResponse(f"Unexpected error: {exc.detail}", status_code=500)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):

    return PlainTextResponse(str(exc), status_code=400)

class ModelLoaderReq(BaseModel):
    model_name: str


chatbot = ChatbotModel()


@app.post("/llm-chatbot/")
async def generate_chatbot_response(request_item: RequestItem):
    """
    Generates a response from the LLM Chatbot based on the user's input.

    Args:
        request_item (RequestItem): An object containing the user's input.

    Returns:
        dict: A dictionary containing the generated chatbot response.
    """

    try:
        query = request_item.text
        chatbot_output = chatbot.predict_query(query)
        return {"output": chatbot_output}, 200

    except Exception as exception:
        print(f"Error while generating response: {exception}")
        return exception, 500


@app.post("/load-model/")
async def load_chatbot_model(request: ModelLoaderReq):
    model_name = request.model_name
    chatbot.load_model(model_name)



if __name__ == "__main__":
    print("Running chatbot API")
