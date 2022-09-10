from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import cv2
import time

app = FastAPI()
cap = None

@app.on_event('startup')
async def startup_event():
  global cap
  cap = cv2.VideoCapture(0)
  if not cap.isOpened():
    raise Exception('Camera 0 is not opened')
  cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
  # cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'YUYV'))
  cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1600)
  cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1200)
  cap.set(cv2.CAP_PROP_FPS, 15)

@app.on_event('shutdown')
async def shutdown_event():
  if cap is not None:
    cap.release()

def generate():
  while True:
    ret, frame = cap.read()
    if not ret:
      continue

    ret, frame_binary = cv2.imencode('.jpg', frame)
    if not ret:
      continue
    
    yield b'--frame\nContent-Type: image/jpeg\n\n' + frame_binary.tobytes() + b'\n'
    time.sleep(0.0333 * 2)

@app.get('/')
async def index():
  return StreamingResponse(generate(), media_type='multipart/x-mixed-replace; boundary=frame')

