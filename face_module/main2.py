import os
import cv2
import torch
import numpy as np
from PIL import Image
from facenet_pytorch import MTCNN, InceptionResnetV1
from numpy.linalg import norm


class FaceStreamClassifier:
    def __init__(self, dataset_path):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.mtcnn = MTCNN(image_size=160, margin=20, keep_all=True, device=self.device)
        self.facenet = InceptionResnetV1(pretrained="vggface2").eval().to(self.device)

        # Numeric class database
        self.database = {
            0: [],  # ALLY
            2: []   # THREAT
        }

        self.load_dataset(dataset_path)

    # ------------------------
    def cosine_similarity(self, a, b):
        return np.dot(a, b) / (norm(a) * norm(b))

    # ------------------------
    def get_embedding(self, img):
        face = self.mtcnn(img)
        if face is None:
            return None

        face = face.to(self.device)
        with torch.no_grad():
            emb = self.facenet(face)

        return emb[0].cpu().numpy()

    # ------------------------
    def load_dataset(self, dataset_path):
        print("[INFO] Loading dataset...")

        label_map = {
            "ally": 0,
            "threat": 2
        }

        for folder, label in label_map.items():
            path = os.path.join(dataset_path, folder)
            if not os.path.exists(path):
                continue

            for person in os.listdir(path):
                person_path = os.path.join(path, person)

                for img_name in os.listdir(person_path):
                    img_path = os.path.join(person_path, img_name)
                    img = Image.open(img_path).convert("RGB")

                    emb = self.get_embedding(img)
                    if emb is not None:
                        self.database[label].append(emb)

        print("[INFO] Dataset Loaded")
        print("ALLY:", len(self.database[0]))
        print("THREAT:", len(self.database[2]))

    # ------------------------
    def classify(self, emb, threshold=0.7):
        best_class = 1  # UNKNOWN
        best_score = 0

        for label in [0, 2]:
            for ref in self.database[label]:
                score = self.cosine_similarity(emb, ref)
                if score > best_score:
                    best_score = score
                    best_class = label

        if best_score < threshold:
            return 1  # UNKNOWN

        return best_class

    # ------------------------
    def run_stream(self):
        cap = cv2.VideoCapture(0)
        print("[INFO] Streaming started (Press Q to quit)")

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            boxes, _ = self.mtcnn.detect(rgb)

            if boxes is not None:
                for box in boxes:
                    x1, y1, x2, y2 = map(int, box)
                    face_img = Image.fromarray(rgb[y1:y2, x1:x2])

                    emb = self.get_embedding(face_img)
                    if emb is None:
                        continue

                    cls = self.classify(emb)

                    # Per-frame numeric stream output
                    print(cls, end=" ", flush=True)

                    if cls == 0:
                        color = (0, 255, 0)
                        text = "ALLY (0)"
                    elif cls == 2:
                        color = (0, 0, 255)
                        text = "THREAT (2)"
                    else:
                        color = (0, 255, 255)
                        text = "UNKNOWN (1)"

                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(frame, text, (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

            cv2.imshow("Face Stream Classifier", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    system = FaceStreamClassifier("dataset")
    system.run_stream()
