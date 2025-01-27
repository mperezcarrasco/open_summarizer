FROM nvcr.io/nvidia/pytorch:22.12-py3
# ==== PIP SETUP ====
RUN python -m pip install --upgrade pip
# INSTALLING IMPORTANT DEPENDENCIES
RUN apt-get update -y
RUN apt-get install -y git
COPY . /tmp/
RUN apt-get update
# ==== BUILDING WORKING DIR ====
WORKDIR /tmp/
ENV PATH=$PATH:~/.local/bin
RUN python -m pip install --upgrade pip
RUN pip3 install -r requirements.txt --default-timeout=100
RUN curl -fsSL https://ollama.com/install.sh | sh
ENV OLLAMA_HOST=0.0.0.0:8001
RUN ollama serve & disown
RUN pip uninstall -y apex
EXPOSE 8881
#ollama pull deepseek-r1:8b
