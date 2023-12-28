from pdf2image import convert_from_path
from glob import glob
from tqdm.auto import tqdm
import image_processing
import db
import os
# Store Pdf with convert_from_path function
image_path = 'images/'
image_processor = image_processing.ImageProcessor()
database = db.VectorStore()
c = 1
for pdf in tqdm(glob('pdfs/*.pdf')):
    images = convert_from_path(pdf)
    
    name = pdf[pdf.rindex('/')+1:-4]

    if os.path.exists(image_path + name + '_00001.jpg'):
        continue

    for i in range(len(images)):
        # Save pages as images in the pdf
        images[i].save(image_path + name + '_' + str(i+1).zfill(5) +'.jpg', 'JPEG')
        img_emb, text_emb = image_processor.encode(image_path + name + '_' + str(i+1).zfill(5) +'.jpg', is_path=True)
        database.insert(c, img_emb, name, i, 'image')
        database.insert(c, [float(j) for j in text_emb], name, i, 'text')
        c += 1
    
    if c > 100:
        break
