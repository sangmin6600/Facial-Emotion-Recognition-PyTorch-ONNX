import cv2
import torch
import torchvision.transforms as transforms
from PIL import Image
import matplotlib.pyplot as plt
import argparse
import os
from model import *


def load_trained_model(model_path):
    model = Face_Emotion_CNN()
    model.load_state_dict(torch.load(model_path, map_location=lambda storage, loc: storage), strict=False)
    return model

def FER_image(img_path):

    model = load_trained_model()
    
    emotion_dict = {0: 'angry', 1: 'disgust', 2: 'fear', 3: 'happy',
                    4: 'sad', 5: 'surprise', 6: 'neutral'}

    val_transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.507395516207, ),(0.255128989415, ))])


    img = cv2.imread(img_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    face_cascade = cv2.CascadeClassifier('./haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(img)
    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x,y), (x+w, y+h), (255,0,0), 2)
        resize_frame = cv2.resize(gray[y:y + h, x:x + w], (48, 48))
        X = Image.fromarray((resize_frame))
        X = val_transform(X).unsqueeze(0)
        with torch.no_grad():
            model.eval()
            log_ps = model.cpu()(X)
            ps = torch.exp(log_ps)
            top_p, top_class = ps.topk(1, dim=1)
            pred = emotion_dict[int(top_class.numpy())]
        cv2.putText(img, pred, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 1)

    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    plt.show()


if __name__ == "__main__":

    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--path", required=True,
        help="path of image")
    args = vars(ap.parse_args())
    
    if not os.path.isfile(args['path']):
        print('The image path does not exists!!')
    else:
        print(args['path'])

    FER_image(args['path'])