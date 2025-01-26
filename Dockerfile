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
RUN pip3 install -r requirements.txt
EXPOSE 8881