#!/bin/bash

mkdir -p chatbot/model \
    && wget https://huggingface.co/dnato/ggml-gpt4all-j-v1.3-groovy.bin/resolve/main/ggml-gpt4all-j-v1.3-groovy.bin \
    && mv ggml-gpt4all-j-v1.3-groovy.bin chatbot/model/


docker-compose build

docker-compose up -d

gradio web/app.py # Use URL http://127.0.0.1:8200/ on your browser to view the UI