#!/bin/bash

# required for pydantic
curl https://sh.rustup.rs -sSf | sh

PATH="/root/.cargo/bin:${PATH}"

pip install chromadb openai panel

