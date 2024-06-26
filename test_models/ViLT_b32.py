from transformers import ViltProcessor, ViltForQuestionAnswering
from PIL import Image

image = Image.open("../test_images/lightpole.jpg") # change the image
question = "Is there a path to the door?"

processor = ViltProcessor.from_pretrained("dandelin/vilt-b32-finetuned-vqa")
model = ViltForQuestionAnswering.from_pretrained("dandelin/vilt-b32-finetuned-vqa")

encoding = processor(image, question, return_tensors="pt")

outputs = model(**encoding)
logits = outputs.logits
idx = logits.argmax(-1).item()

print("Predicted answer: ", model.config.id2label[idx])