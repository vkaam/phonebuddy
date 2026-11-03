FROM python:3.12-alpine@sha256:e6dae589c1c05976188fd3bd019afd091445fc533ed2ea29001beddc7368a9c8
WORKDIR /app
COPY server.py /app/server.py
USER 65532:65532
EXPOSE 8080
CMD ["python", "-B", "/app/server.py"]
