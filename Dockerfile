FROM mcr.microsoft.com/azure-functions/python:4-python3.9

RUN apt-get update && apt-get install -y ffmpeg
ENV PYTHONUNBUFFERED=1

COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt

COPY . /home/site/wwwroot