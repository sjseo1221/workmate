FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY mock_workmate ./mock_workmate
RUN mkdir -p /app/results
EXPOSE 8010
CMD ["uvicorn", "mock_workmate.app:app", "--host", "0.0.0.0", "--port", "8010"]
