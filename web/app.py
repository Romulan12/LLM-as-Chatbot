import json
import time

import gradio as gr
import requests


def process_chat(chat_history, user_input):

    """
    Sends user input to the LLM Chatbot and processes the chat conversation.

    Args:
        chat_history (list): A list of tuples representing the chat conversation history.
        user_input (str): The user's input or message.

    Yields:
        list: A modified chat history after processing the user input.
    """
    
    resp = requests.post(
        "http://127.0.0.1:8100/llm-chatbot/", data=json.dumps({"text": f"{user_input}"})
    )
    data = resp.json()
    response_text = data[0]["output"]
    bot_response = response_text

    response = ""

    for letter in "".join(bot_response):

        response += letter + ""
        time.sleep(0.05)
        yield chat_history + [(user_input, response.strip())]

def load_model(radio):

    """
    Sends a POST request to load the specified model.
    
    Args:
        radio (str): The selected model name.
    """
    _ = requests.post(
        "http://127.0.0.1:8100/load-model/", data=json.dumps({"model_name": radio})
    )

with gr.Blocks() as demo:

    with gr.Tab("Chatbot UI"):

        txt_view = gr.Textbox(
            label="Model Loading Status", value= "Default GPT-J Loaded"
        )
        radio = gr.Radio(
            ["LLAMA", "GPT-J"], label="Select Model"
        )

        radio.input(
            lambda: "Start downloading and loading the model...", None, txt_view
        ).then(load_model, [radio]).then(lambda: "Model Loaded", None, txt_view)

        chatbot = gr.Chatbot(show_label = False)
        message = gr.Textbox(
            show_label=False, placeholder="Enter text and press enter"
        ).style(container=False)
        message.submit(process_chat, [chatbot, message], chatbot).then(
            lambda: None, None, message, queue=False
        )
        message.submit(None, None, message, _js="() => {''}")
        clear = gr.ClearButton([message, chatbot])

demo.queue().launch(debug=True, share=True, server_port=8200)
