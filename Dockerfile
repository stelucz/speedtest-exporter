FROM python:3.7.5-alpine
COPY requirements.txt /
COPY main.py /
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python", "./main.py"]
CMD []
