import os
import subprocess

import yaml
from langchain import LLMChain, PromptTemplate
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.llms import GPT4All, LlamaCpp, OpenLLM
from starlette.exceptions import HTTPException


CONFIG_PATH = "config.yaml"

# Open the YAML file
with open(CONFIG_PATH, "r") as file:
    CONFIG = yaml.safe_load(file)

MODEL_DIR = CONFIG["model_dir"]


class ChatbotModel:
    def __init__(self):
        self.llm = None
        self.load_model("GPT-J")

    def download_model(self, model_name):

        """
        Downloads the specified model from the given model name.
        
        Args:
            model_name (str): The name of the model to be downloaded.
        """

        model_uri = CONFIG["model"][model_name]
        model_name = model_uri.split("/")[-1]

        _ = subprocess.run(f"mkdir -p {MODEL_DIR}", shell=True)
        _ = subprocess.run(f"wget {model_uri}", shell=True)
        _ = subprocess.run(f"mv {model_name} {MODEL_DIR}", shell=True)

    def get_model_object(self, model_name):

        """
        Returns the appropriate model object and path argument based on the model name.
        
        Args:
            model_name (str): The name of the model.
        
        Returns:
            model_obj: The model object corresponding to the model name.
            path_argument (str): The path argument required for loading the model.
        
        Raises:
            HTTPException: If an invalid model choice is provided.
        """


        if model_name == "LLAMA":
            model_obj = LlamaCpp
            path_argument = "model_path"
        elif model_name == "GPT-J":
            model_obj = GPT4All
            path_argument = "model"
        else:
            raise HTTPException(status_code=400, detail="Invalid model choice. Expected either LLAMA or GPT-J.")

        return model_obj, path_argument

    def load_model(self, model):

        """
        Loads the specified model.
        
        Args:
            model (str): The name of the model to be loaded.
        
        Raises:
            HTTPException: If the model fails to download or load.
        """

        model_file_name = CONFIG["model"][model].split("/")[-1]
        model_path = f"{MODEL_DIR}/{model_file_name}"

        
        if not os.path.isfile(model_path):
            print("Downloading model")
            _ = self.download_model(model)
        if not os.path.isfile(model_path):
            raise HTTPException(status_code=500, detail="Unable to download the model.")


        callbacks = [StreamingStdOutCallbackHandler()]

        model_object, path_argument = self.get_model_object(model)
        args = {path_argument: model_path, "callbacks": callbacks}
        try: 
            self.llm = model_object(**args)
        except Exception as E:
            raise HTTPException(status_code=500, detail=f"Unable to load the model. Got the following error: {E}")



    def get_prompt(self):

        """
        Returns the prompt template used for generating the response.
        
        Returns:
            prompt: The prompt template object.
        """


        template = """
        You are a chatbot assistant that responds in a polite and conversational manner to users questions. 
        Question: "{query}"
        Answer:
        """

        prompt = PromptTemplate(template=template, input_variables=["query"])

        return prompt

    def predict_query(self, query):

        """
        Generates a response to the given query using the loaded model.
        
        Args:
            query (str): The user's query.
        
        Returns:
            response: The generated response to the query.
        
        Raises:
            HTTPException: If there is an error in getting the model prediction.
        """

        prompt = self.get_prompt()

        try:
            llm_chain = LLMChain(prompt=prompt, llm=self.llm)
            response = llm_chain.run(query)
        except Exception as E: 
            raise HTTPException(status_code=500, detail=f"Unable to get model prediction. Got the following error: {E}")
        
        return response
