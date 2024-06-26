from PIL import Image
from transformers import pipeline

vqa_pipeline = pipeline("visual-question-answering", model="dandelin/vilt-b32-finetuned-vqa")

image = Image.open("../test_images/lightpole.jpg") # change the image
question = "Is there a path to the door?"

result = vqa_pipeline(image, question, top_k=1)
print(result)
