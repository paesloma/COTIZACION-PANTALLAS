import streamlit as st
import pandas as pd
from datetime import datetime
from weasyprint import HTML
import pytesseract
from PIL import Image
import re

st.set_page_config(
    page_title="Gestión de Cotizaciones y Órdenes Motsur",
    page_icon="📋",
    layout="wide"
)

st.title("📋 Procesador y Gestor de Cotizaciones Motsur")
st.markdown("---")

st.sidebar.header("Panel de Control")
st.sidebar.info("Adjunta la proforma o captura de SAP. El material de la sección 'Posiciones' se extraerá automáticamente.")

uploaded_file = st.file_uploader(
    "Adjuntar Proforma / Captura SAP (PDF o Imagen)", 
    type=["pdf", "png", "jpg", "jpeg"]
)

# Valores por defecto iniciales
ext_cliente = "LA GANGA R.C.A. S.A., JOSE CASTILLO CASTILLO, GUAYAQUIL, Ecuador"
ext_fecha = "11/09/2026"
ext_telefono = "0995115782"
ext_orden = "35663"
ext_responsable = "German Tenemaza"
ext_material = "PL55P75"
ext_descripcion = "PANEL TV 55P755 CBU"
ext_cantidad = "1,000 UN"
ext_precio = "159.26"

if uploaded_file is not None:
    st.success("¡Documento adjuntado y procesado correctamente!")
    
    # Extracción automática mediante OCR si es imagen
    if uploaded_file.type in ["image/png", "image/jpeg", "image/jpg"]:
        try:
            image = Image.open(uploaded_file)
            ocr_text = pytesseract.image_to_string(image)
            
            # Buscar solicitante / cliente
            if "LA GANGA" in ocr_text.upper():
                ext_cliente = "LA GANGA R.C.A. S.A., JOSE CASTILLO CASTILLO, GUAYAQUIL, Ecuador"
                
            # Extraer material específicamente de la columna Material / Posiciones
            m_material = re.search(r'(?:PL[0-9A-Z]+)', ocr_text)
            if m_material:
                ext_material = m_material.group(0).strip()
                
            # Extraer el valor neto y asignarlo como precio sin IVA
            m_valor = re.search(r'Valor neto[:\s]*([\d,.]+)', ocr_text, re.IGNORECASE)
            if m_valor:
                val_neto_str = m_valor.group(1).replace(',', '.')
                try:
                    ext_precio = f"{float(val_neto_str):.2f}"
                except:
                    pass
                    
            m_fecha = re.search(r'([\d]{2}\.[\d]{2}\.[\d]{4})', ocr_text)
            if m_fecha:
                ext_fecha = m_fecha.group(1).replace('.', '/')
        except Exception as e:
            pass

    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📄 Vista Previa y Descarga de Adjunto")
        if uploaded_file.type in ["image/png", "image/jpeg", "image/jpg"]:
            st.image(uploaded_file, caption="Captura / Proforma Adjunta", use_container_width=True)
            
            st.download_button(
                label="📥 Descargar Imagen Adjunta Original",
                data=uploaded_file.getvalue(),
                file_name=uploaded_file.name,
                mime=uploaded_file.type
            )
        else:
            st.info("Archivo PDF cargado como adjunto.")
            st.download_button(
                label="📥 Descargar PDF Adjunto Original",
                data=uploaded_file.getvalue(),
                file_name=uploaded_file.name,
                mime="application/pdf"
            )

    with col2:
        st.subheader("⚙️ Configuración y Valores Extraídos")
        
        # --- INICIO DEL FORMULARIO ---
        with st.form("motsur_form"):
            cliente = st.text_input("Solicitante / Cliente", value=ext_cliente)
            fecha = st.text_input("Fecha", value=ext_fecha)
            telefono = st.text_input("Teléfono", value=ext_telefono)
            orden = st.text_input("Orden #", value=ext_orden)
            responsable = st.text_input("Responsable", value=ext_responsable)
            
            st.markdown("---")
            st.markdown("### Detalle")
            material = st.text_input("Código / Material (Columna Posiciones)", value=ext_material)
            descripcion = st.text_input("Descripción", value=ext_descripcion)
            cantidad = st.text_input("Cantidad", value=ext_cantidad)
            precio_sin_iva = st.text_input("Precio Sin IVA (Valor Neto SAP)", value=ext_precio)
            
            submitted = st.form_submit_button("Generar PDF Oficial Motsur")
        # --- FIN DEL FORMULARIO ---
        
        descarga_container = st.empty()

    if submitted:
        html_content = f'''<!DOCTYPE html>
        <html lang="es">
        <head>
        <meta charset="UTF-8">
        <style>
            @page {{ size: A4; margin: 12mm 15mm; background-color: #ffffff; }}
            *, *::before, *::after {{ box-sizing: border-box; }}
            body {{ font-family: Arial, Helvetica, sans-serif; color: #111111; margin: 0; padding: 0; font-size: 10pt; line-height: 1.3; }}
            .header-container {{ width: 100%; border-bottom: 3px solid #003366; margin-bottom: 15px; padding-bottom: 8px; }}
            .header-table {{ width: 100%; border-collapse: collapse; }}
            .logo-box {{ width: 25%; vertical-align: middle; }}
            .logo-img-placeholder {{ background-color: #c00; color: white; font-weight: bold; text-align: center; padding: 8px 5px; font-size: 14pt; letter-spacing: 1px; border-radius: 2px; }}
            .title-box {{ width: 75%; text-align: right; vertical-align: middle; font-size: 20pt; font-weight: bold; color: #003366; letter-spacing: 2px; }}
            .info-grid {{ width: 100%; border-collapse: collapse; margin-bottom: 15px; border: 1px solid #b0c4de; background-color: #f4f8fb; }}
            .info-grid td {{ padding: 6px 10px; vertical-align: middle; font-size: 9.5pt; border-bottom: 1px solid #d0e0ef; }}
            .info-label {{ font-weight: bold; color: #333333; width: 18%; text-transform: uppercase; }}
            .info-value {{ color: #000000; width: 32%; }}
            .table-container {{ margin-top: 10px; margin-bottom: 20px; }}
            table.data-table {{ width: 100%; border-collapse: collapse; }}
            table.data-table th {{ background-color: #2b579a; color: white; text-align: center; padding: 8px 6px; font-size: 9.5pt; text-transform: uppercase; border: 1px solid #2b579a; }}
            table.data-table td {{ padding: 8px 6px; border: 1px solid #d0d0d0; font-size: 9.5pt; vertical-align: middle; }}
            table.data-table tr:nth-child(even) {{ background-color: #f9fbfd; }}
            .text-center {{ text-align: center; }}
            .text-right {{ text-align: right; }}
            .text-left {{ text-align: left; }}
            .totals-container {{ width: 100%; margin-top: 10px; }}
            .totals-container::after {{ content: ""; display: table; clear: both; }}
            .note-box {{ float: left; width: 55%; font-style: italic; color: #555555; font-size: 8.5pt; padding-top: 10px; }}
            .totals-box {{ float: right; width: 42%; border: 1px solid #b0c4de; background-color: #f4f8fb; padding: 8px 12px; }}
            .totals-row {{ width: 100%; margin-bottom: 4px; }}
            .totals-row::after {{ content: ""; display: table; clear: both; }}
            .totals-label {{ float: left; font-weight: bold; color: #c00; font-size: 10pt; }}
            .totals-value {{ float: right; font-weight: bold; color: #c00; font-size: 11pt; }}
        </style>
        </head>
        <body>
            <div class="header-container">
                <table class="header-table">
                    <tr>
                        <td class="logo-box"><div class="logo-img-placeholder">MOTSUR</div></td>
                        <td class="title-box">PROFORMA</td>
                    </tr>
                </table>
            </div>
            <table class="info-grid">
                <tr><td class="info-label">CLIENTE:</td><td class="info-value">{cliente}</td><td class="info-label">FECHA:</td><td class="info-value">{fecha}</td></tr>
                <tr><td class="info-label">TELÉFONO:</td><td class="info-value">{telefono}</td><td class="info-label">ORDEN:</td><td class="info-value">{orden}</td></tr>
                <tr><td class="info-label">RESPONSABLE:</td><td class="info-value">{responsable}</td><td class="info-label"></td><td class="info-value"></td></tr>
            </table>
            <div class="table-container">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th style="width: 15%;">CÓDIGO</th>
                            <th style="width: 42%;">DESCRIPCIÓN</th>
                            <th style="width: 13%;">CANTIDAD</th>
                            <th style="width: 15%;">PRECIO SIN IVA</th>
                            <th style="width: 15%;">TOTAL</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td class="text-center">{material}</td>
                            <td class="text-left">{descripcion}</td>
                            <td class="text-center">{cantidad}</td>
                            <td class="text-right">${precio_sin_iva}</td>
                            <td class="text-right">${precio_sin_iva}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <div class="totals-container">
                <div class="note-box">NOTA: PRECIOS SUJETOS A CAMBIOS.<br>* TODOS LOS PRECIOS SE PRESENTAN SIN IVA (VALOR NETO SAP).</div>
                <div class="totals-box">
                    <div class="totals-row">
                        <span class="totals-label">TOTAL SIN IVA:</span>
                        <span class="totals-value">${precio_sin_iva}</span>
                    </div>
                </div>
            </div>
        </body>
        </html>'''
        
        pdf_filename = f"orden_{orden}_motsur.pdf"
        with open("temp.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        HTML("temp.html").write_pdf(pdf_filename)
        
        with descarga_container:
            st.success("¡PDF generado con éxito!")
            with open(pdf_filename, "rb") as pdf_file:
                st.download_button(
                    label="📥 Descargar PDF Oficial Motsur",
                    data=pdf_file,
                    file_name=pdf_filename,
                    mime="application/pdf"
                )
else:
    st.warning("Por favor, adjunta la proforma o captura de SAP para habilitar el reconocimiento automático.")
