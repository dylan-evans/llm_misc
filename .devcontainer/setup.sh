#!/bin/bash

# required for pydantic
curl https://sh.rustup.rs -sSf | sh -- -y

PATH="/root/.cargo/bin:${PATH}"

pip install chromadb openai panel

