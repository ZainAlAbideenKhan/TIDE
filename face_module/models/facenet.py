# face_module/models/facenet.py
import torch
from facenet_pytorch import InceptionResnetV1
from torchvision import transforms
import cv2

model = InceptionResnetV1(pretrained="vggface2").eval()

transform = transforms.Compose([
  transforms.ToPILImage(),
  transforms.Resize((160, 160)),
  transforms.ToTensor(),
  transforms.Normalize([0.5], [0.5])
])

def get_embedding(face_bgr):
  face_rgb = cv2.cvtColor(face_bgr, cv2.COLOR_BGR2RGB)
  tensor = transform(face_rgb).unsqueeze(0)
  with torch.no_grad():
    emb = model(tensor).numpy()
  return emb
