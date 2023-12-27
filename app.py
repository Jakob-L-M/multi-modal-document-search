import streamlit as st
import image_processing
from glob import glob
import db

IMAGE_PATH = 'images/'

if __name__ == '__main__':
    st.set_page_config(
     page_title='Multi Modal Search',
     layout="wide",
     initial_sidebar_state="expanded",
    )

    #### Main view
    st.session_state['res_col'], st.session_state['detail_col'] = st.columns(2)
    # col1: document selection
    # col2: detail view of selected document

    st.session_state['res_col'].header('Results')
    st.session_state['res_container'] = st.session_state['res_col'].container()

    st.session_state['detail_col'].header('Documents')
    st.session_state['detail_container'] = st.session_state['detail_col'].container()

    #### Sidebar
    st.session_state['sidebar'] = st.sidebar
    st.session_state['sidebar'].header('Input')
    st.session_state['img_upload'] = st.session_state['sidebar'].file_uploader('Upload Screenshot', ['jpg', 'png'])
    #### Sidebar end

if 'models' not in st.session_state:
    st.session_state['models'] = True
    st.session_state['image_processor'] = image_processing.ImageProcessor()

    st.session_state['image_storage'] = glob(IMAGE_PATH + '*.jpg')
    st.session_state['curr_file_id'] = 'none'
    st.session_state['database'] = db.VectorStore()

def update_result(res):
    res = [r.payload for r in res]
    st.session_state['detail_container'].empty()
    with st.session_state['res_container'].container():
        for r in res:
            file = r['filename']
            img_path = IMAGE_PATH + file + '_' + str(r['page']).zfill(5) + '.jpg'
            container = st.container()
            file_name, download, details = container.columns([8,1,1])
            file_name.markdown('##### ' + file + ' | Page: ' + str(r['page']+1))
            with open('pdfs/' + file + '.pdf', 'rb') as f:
                download.download_button('⇩', data=f, file_name=file + '.pdf',key='dl_' + file + str(r['page']).zfill(5))
            details.button('🔍', on_click=load_document, args=[file], key='dt_' + file + str(r['page']).zfill(5))
            container.image(img_path)
            container.markdown("""---""")

css='''
<style>
    .main>.block-container>div>[data-testid="stVerticalBlock"]>[data-testid="stHorizontalBlock"]>[data-testid="column"]>div>[data-testid="stVerticalBlock"]>div>[data-testid="stVerticalBlock"] {
        overflow-x: hidden;
        max-height: 79vh;
        overflow-y: scroll;
        padding-right: 1vw;
    }
    .block-container {
        padding-bottom: 2vh !important;
        padding-top: 3vh !important;
    }
</style>
'''
st.markdown(css, unsafe_allow_html=True)

def load_document(name: str):
    pages = sorted([i for i in st.session_state['image_storage'] if name in i])

    with st.session_state['detail_container']:
        for p in pages:
            st.image(p)   

#### Logic handling
if st.session_state['img_upload'] is not None and st.session_state['img_upload'].file_id != st.session_state['curr_file_id']:
    st.session_state['curr_file_id'] = st.session_state['img_upload'].file_id
    byte_data = st.session_state['img_upload'].getvalue()
    img_embedding, text_embedding = st.session_state['image_processor'].encode(byte_data)
    
    # find topK matches
    res = st.session_state['database'].query(img_embedding, text_embedding, 5)
    # load images
    update_result(res)

