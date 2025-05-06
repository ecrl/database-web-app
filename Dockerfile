FROM python:3.13.3-slim-bookworm
COPY . .
RUN pip3 install -r requirements.txt
EXPOSE 8000
CMD ["gunicorn", "--config", "src/gunicorn.py", "src.app:app"]