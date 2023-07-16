FROM python:3.9

RUN pip install --upgrade pip

RUN mkdir /code

RUN apt update

RUN apt-get install -y liblzma-dev cmake

RUN git clone --recurse-submodules https://github.com/nomic-ai/gpt4all  \
    && cd gpt4all/gpt4all-backend/ \
    && mkdir build \
    && cd build \
    && cmake .. \
    && cmake --build . --parallel \
    && cd ../../gpt4all-bindings/python && pip3 install -e .

RUN pip install gpt4all==0.3.6

WORKDIR /code

COPY . .

RUN pip3 install --no-cache-dir -r requirements.txt

EXPOSE 8100

WORKDIR src 

CMD uvicorn main:app --port 8100 --reload 