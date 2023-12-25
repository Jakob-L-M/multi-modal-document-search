import open_clip
from PIL import Image, ImageOps
import io
from sentence_transformers import SentenceTransformer
import pytesseract

class ImageProcessor:

    def __init__(self):
        self.device = 'mps' # use torch apple silicon backend, change to 'cuda' for nvidia gpu or 'cpu'
        print('Loading image model...', end='', flush=True)
        self.image_model, _, self.preprocess = open_clip.create_model_and_transforms('ViT-g-14', pretrained='laion2b_s12b_b42k')
        self.image_model.to(self.device) 
        print('\b\b\b ☑️ ', flush=True)

        print('Loading OCR model...', end='', flush=True)
        self.text_model = SentenceTransformer('embaas/sentence-transformers-e5-large-v2')
        self.text_model.to(self.device)
        print('\b\b\b ☑️ ', flush=True)

    def encode(self, img, is_path = False):
        if is_path:
            img = Image.open(img).convert('RGB')
        else:
            img = Image.open(io.BytesIO(img)).convert('RGB')
        text = pytesseract.image_to_string(img)
        if img.width < img.height:
            img = img.rotate(90)
        img = ImageOps.contain(img, (1920, 1080))
        chunks = self.get_chunks(img)

        embeddings = [self.image_model.encode_image(self.preprocess(c).unsqueeze(0).to(self.device))[0].tolist() for c in chunks]

        flatten_img_embedding = [item for sublist in embeddings for item in sublist]
        text_embedding = self.text_model.encode(text)

        return flatten_img_embedding, [float(j) for j in text_embedding]

    def get_chunks(self, img):
        img_chunks = []
        for w in range(0, 2):
            img_chunks.append(
                img.crop(
                    (w*960, 0, (w+1)*960, 1080)
                ))

        return img_chunks