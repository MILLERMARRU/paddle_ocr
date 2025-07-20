from paddleocr import PaddleOCR, draw_ocr
from PIL import Image, UnidentifiedImageError
import streamlit as st
import numpy as np
from docx import Document
from io import BytesIO
import os

@st.cache_resource
def load_ocr():
    return PaddleOCR(use_angle_cls=False, lang='es')

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

# Si ya se descargó y se quiere volver a empezar
if st.session_state.descargado:
    st.session_state.descargado = False
    st.experimental_rerun()

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
                result = ocr.ocr("input.jpg", cls=False)

            textos_detectados = [line[1][0] for line in result[0]]

            with col1:
                st.image("input.jpg", caption="🖼️ Imagen procesada", use_container_width=True)

            with col2:
                st.markdown("📝 **Texto reconocido (editable)**")
                texto_completo = "\n".join(textos_detectados)
                texto_editado = st.text_area("Resultado OCR:", texto_completo, height=400)

                buffer = generar_docx(texto_editado)

                if st.download_button(
                    label="📥 Descargar como .docx",
                    data=buffer,
                    file_name="resultado_ocr.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                ):
                    st.session_state.descargado = True
                    st.success("✅ Documento descargado. Reiniciando...")
                    st.stop()  # Detiene la ejecución actual, espera al próximo ciclo

    except UnidentifiedImageError:
        st.error("❌ La imagen no pudo ser reconocida. Asegúrate de subir un archivo válido.")
    except Exception as e:
        st.error(f"❌ Error procesando la imagen.\n\n{e}")
else:
    st.info("👆 Por favor, sube una imagen para empezar.")
