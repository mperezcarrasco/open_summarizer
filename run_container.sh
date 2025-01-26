#!/usr/bin/env bash
echo 'Looking for GPUs (ETA: 10 seconds)'
gpu=$(lspci | grep -i '.* vga .* nvidia .*')
shopt -s nocasematch
if [[ $gpu == *' nvidia '* ]]; then
  echo GPU found
  docker run -it --rm \
    --privileged=true \
    --mount "type=bind,src=$(pwd),dst=/tmp/" \
    --workdir /tmp/ \
    --gpus all \
    --ipc=host \
    --ulimit memlock=-1 \
    --ulimit stack=67108864 \
    --name summarizer \
    -p 8881:8881 \
    summarizer bash
else
  docker run -it --rm \
    --privileged=true \
    --mount "type=bind,src=$(pwd),dst=/tmp/" \
    --workdir /tmp/ \
    -p 8881:8881 \
    --name summarizer \
    summarizer bash
fi