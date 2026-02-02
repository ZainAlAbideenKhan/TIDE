import os
import cv2
import torch
import numpy as np
from PIL import Image
from facenet_pytorch import MTCNN, InceptionResnetV1
from numpy.linalg import norm


class FaceCategorizer:
    def __init__(self, dataset_path, device=None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        self.mtcnn = MTCNN(image_size=160, margin=20, device=self.device)
        self.facenet = InceptionResnetV1(
            pretrained="vggface2"
        ).eval().to(self.device)

        self.database = {
            "GOOD": [],
            "BAD": [],
            "UNKNOWN_1": [],
            "UNKNOWN_2": [],
            "UNKNOWN_3": []
        }

        self.load_dataset(dataset_path)

    # ------------------------------
    def cosine_similarity(self, a, b):
        return np.dot(a, b) / (norm(a) * norm(b))

    # ------------------------------
    def get_embedding(self, img):
        face = self.mtcnn(img)
        if face is None:
            return None

        face = face.unsqueeze(0).to(self.device)
        with torch.no_grad():
            emb = self.facenet(face)

        return emb[0].cpu().numpy()

    # ------------------------------
    def load_dataset(self, dataset_path):
        print("[INFO] Loading dataset...")

        for label in ["good", "bad"]:
            label_path = os.path.join(dataset_path, label)
            if not os.path.exists(label_path):
                continue

            for person in os.listdir(label_path):
                person_path = os.path.join(label_path, person)

                for img_name in os.listdir(person_path):
                    img_path = os.path.join(person_path, img_name)

                    img = Image.open(img_path).convert("RGB")
                    emb = self.get_embedding(img)

                    if emb is not None:
                        self.database[label.upper()].append(emb)

        print("[INFO] Dataset loaded")
        print("GOOD:", len(self.database["GOOD"]))
        print("BAD:", len(self.database["BAD"]))

    # ------------------------------
    def categorize(self, emb, match_threshold=0.7, unknown_threshold=0.6):
        best_label = None
        best_score = 0

        # Check GOOD & BAD
        for label in ["GOOD", "BAD"]:
            for ref in self.database[label]:
                score = self.cosine_similarity(emb, ref)
                if score > best_score:
                    best_score = score
                    best_label = label

        if best_score > match_threshold:
            return best_label

        # Handle UNKNOWN groups
        for label in ["UNKNOWN_1", "UNKNOWN_2", "UNKNOWN_3"]:
            if len(self.database[label]) == 0:
                self.database[label].append(emb)
                return label

            score = self.cosine_similarity(emb, self.database[label][0])
            if score > unknown_threshold:
                self.database[label].append(emb)
                return label

        return "UNKNOWN_NEW"

    # ------------------------------
    def run_live(self):
        cap = cv2.VideoCapture(0)

        print("[INFO] Starting live camera... Press Q to quit")

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

                    label = self.categorize(emb)

                    color = (0, 255, 0) if label == "GOOD" else \
                            (0, 0, 255) if label == "BAD" else (255, 255, 0)

                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(
                        frame,
                        label,
                        (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        color,
                        2
                    )

            cv2.imshow("Face Categorizer", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    system = FaceCategorizer(dataset_path="dataset")
    system.run_live()
