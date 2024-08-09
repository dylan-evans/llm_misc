FROM mcr.microsoft.com/devcontainers/python:3.12

RUN curl https://sh.rustup.rs -sSf | bash -s -- -y

ENV PATH="/root/.cargo/bin:${PATH}"

RUN pip3.12 install chromadb openai panel litellm
