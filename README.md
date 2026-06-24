# Safe Road Detector

Browser-based road watch detector using a local Flask + ONNX Runtime backend and pretrained YOLO models.

## Model

The app uses two ONNX models:

- `models/wildlife-north-american-yolo26s.onnx`, downloaded from https://huggingface.co/UWyo/wildlife-north-american-wildlife
- `models/trash-detection-yolo11n.onnx`, exported from https://huggingface.co/Alope/trash-detection-yolo11n

The app filters wildlife output to deer-like classes: `Mule Deer`, `Elk / Wapiti`, and `Moose`. It also detects trash classes: `glass`, `paper`, `plastic`, and `trash`.

## Run

Create/install the virtual environment once:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Start the detector server from this folder:

```powershell
.\.venv\Scripts\python.exe server.py
```

Open:

```text
http://localhost:8000
```

Use **Start Webcam** for live camera detection, or use the upload button to test an image/video.

On Windows, you can also double-click:

```text
start_safe_road.bat
```

## GitHub

The target repository is currently empty:

https://github.com/newralknight-pixel/safe_road

After checking the app, push this local project to that repository.
