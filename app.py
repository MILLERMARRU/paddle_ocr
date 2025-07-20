# app.py

from paddleocr import PaddleOCR
from PIL import Image, UnidentifiedImageError
import streamlit as st
import numpy as np
from docx import Document
from io import BytesIO
import os

@st.cache_resource
def load_ocr():
    return PaddleOCR(
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False
    )

def generar_docx(texto):
    doc = Document()
    doc.add_paragraph(texto)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

ocr = load_ocr()

st.set_page_config(page_title="OCR con PaddleOCR", layout="wide")
st.title("📄 OCR con PaddleOCR")

if "descargado" not in st.session_state:
    st.session_state.descargado = False

uploaded_file = st.file_uploader("📤 Sube una imagen", type=["png", "jpg", "jpeg"])

col1, col2 = st.columns([2, 3])  # 40% imagen, 60% texto

if uploaded_file:
    try:
        image = Image.open(uploaded_file).convert("RGB")

        if image.size[0] < 50 or image.size[1] < 50:
            st.error("⚠️ La imagen es demasiado pequeña para procesar texto.")
        else:
            image.save("input.jpg")

            with st.spinner("🔍 Procesando imagen..."):
                result = ocr.predict(input="input.jpg")[0]

            textos_detectados = result['rec_texts']
            result.save_to_img("resultado_ocr.jpg")

            with col1:
                st.image("resultado_ocr.jpg", caption="🖼️ Imagen con cuadros", use_container_width=True)

            with col2:
                st.markdown("📝 **Texto reconocido (editable)**")
                texto_completo = "\n".join(textos_detectados)
                texto_editado = st.text_area("Resultado OCR:", texto_completo, height=400)

                buffer = generar_docx(texto_editado)

                downloaded = st.download_button(
                    label="📥 Descargar como .docx",
                    data=buffer,
                    file_name="resultado_ocr.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

                if downloaded:
                    st.success("✅ Documento descargado. Reinicia para procesar otra imagen.")
                    st.session_state.descargado = True
                    st.experimental_rerun()

    except UnidentifiedImageError:
        st.error("❌ La imagen no pudo ser reconocida. Asegúrate de subir un archivo válido.")
    except Exception as e:
        st.error(f"❌ Error procesando la imagen.\n\n{e}")

else:
    st.info("👆 Por favor, sube una imagen para empezar.")

if st.session_state.descargado:
    st.session_state.clear()
    st.experimental_rerun()
