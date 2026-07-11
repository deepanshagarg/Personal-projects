"""Run: conda run -n face python face_cuda_smoke.py"""
import sys
import onnxruntime as ort

print("python:", sys.executable)
providers = ort.get_available_providers()
print("providers:", providers)
if "CUDAExecutionProvider" not in providers:
    raise SystemExit("CUDAExecutionProvider missing - install onnxruntime-gpu[cuda,cudnn]")

from insightface.app import FaceAnalysis
app = FaceAnalysis("buffalo_l")
app.prepare(ctx_id=0, det_size=(640, 640))
print("detection provider:", app.models["detection"].session.get_providers()[0])
print("OK: CUDAExecutionProvider available")
