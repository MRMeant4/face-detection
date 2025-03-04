# Face Detection

Simple Django based application for detecting faces in images via OpenCV's Haar Cascade classifier. After detection, application generates new images with bounding boxes around detected faces and sends notification via WebSockets to all connected clients in real-time.

# Usage

## Prerequisites

- Python >= 3.11
- Docker

## Run application
### via Docker

The easiest way to run the application is via `docker compose` tool
```
docker compose up --build
```

### Manually
Project is setup with [`poetry`](https://python-poetry.org/docs/#installing-with-pipx) as dependency management tool.  It allows you to declare the libraries your project depends on and it manages them. Poetry offers a lockfile to ensure repeatable installs, and can build your project for distribution.

1. Install recommended poetry version
   ```
   pipx install poetry==1.8.4
   ```
   alternatively
   ```
   curl -sSL https://install.python-poetry.org | python3 -
   ```
2. Create virtual environment and install all necessary dependencies
   ```
   poetry install --without dev --no-root
   ```
3. Run the face detection server
   ```
   poetry run python manage.py runserver 0.0.0.0:8282
   ```
4. Run redis database for WebSocket messages
   ```
   docker run --rm -p 6379:6379 redis:7
   ```

## Connect to WebSocket

Assuming you have `node` installed, [`wscat`](https://github.com/websockets/wscat) is recommended as simple and intuitive tool for connecting to running app WebSocket endpoint.

```
npm install -g wscat
```

Then, connect to the endpoint of running application

```
wscat -c "ws://0.0.0.0:8282/faces"
```

## Face detection

Running application accepts image uploads via POST requests to the /image endpoint. Prepare some test image with faces and send it in request. 

```
curl -X POST -F "image=@face1.jpg" http://localhost:8282/image
```

The JSON repsonse will contain the link to the image with detected faces marked with boxes.

# TODOs
- unit tests coverage
- CI/CD workflows setup with Github Actions
  - packaging
  - linting/formatting
  - testing
  - test covarage
- [`pre-commit`](https://github.com/pre-commit/pre-commit) configuration
- basic UI
- migrate to [`ruff`](https://github.com/astral-sh/ruff)