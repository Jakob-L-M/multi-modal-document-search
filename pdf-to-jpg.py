from pdf2image import convert_from_path
from glob import glob
from tqdm.auto import tqdm
import os
# Store Pdf with convert_from_path function
image_path = 'images/'
for pdf in tqdm(glob('pdfs/*.pdf')):
    images = convert_from_path(pdf)
    
    name = pdf[pdf.rindex('/')+1:-4]

    if os.path.exists(image_path + name + '_001.jpg'):
        continue

    for i in range(len(images)):
        # Save pages as images in the pdf
        images[i].save(image_path + name + '_' + str(i+1).zfill(5) +'.jpg', 'JPEG')