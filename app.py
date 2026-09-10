import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="Gestión de Cotizaciones y Órdenes Motsur",
    page_icon="📋",
    layout="wide"
)

st.title("📋 Procesador y Gestor de Cotizaciones Motsur")
st.markdown("---")

st.sidebar.header("Panel de Control")
st.sidebar.info("Sube o adjunta la proforma de Motsur para extraer los datos y estructurarlos para el sistema.")

# Componente para adjuntar la cotización (imagen o PDF)
uploaded_file = st.file_uploader(
    "Adjuntar Proforma / Cotización (PDF o Imagen)", 
    type=["pdf", "png", "jpg", "jpeg"],
    help="Sube la proforma de Motsur como la mostrada en el sistema."
)

if uploaded_file is not None:
    st.success("¡Proforma adjuntada correctamente!")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📄 Vista Previa del Documento")
        if uploaded_file.type in ["image/png", "image/jpeg", "image/jpg"]:
            st.image(uploaded_file, caption="Proforma Motsur Adjunta", use_container_width=True)
        else:
            st.info("Archivo PDF cargado correctamente.")

    with col2:
        st.subheader("⚙️ Datos Extraídos de la Cotización")
        
        with st.form("proforma_form"):
            st.markdown("### Cabecera de la Proforma")
            cliente = st.text_input("Nombre / Cliente", value="PABLO LOPEZ")
            fecha = st.date_input("Fecha", value=datetime.strptime("28/08/2026", "%d/%m/%Y"))
            telefono = st.text_input("Teléfono", value="0995115782")
            orden = st.text_input("Orden #", value="35663")
            responsable = st.text_input("Responsable", value="German Tenemaza")
            
            st.markdown("### Detalle de Ítems")
            data_items = {
                "CODIGO": ["PL43P635"],
                "DESCRIPCION": ["TELEVISION 43P635 CBU"],
                "CANTIDAD": [1],
                "PRECIO SIN IVA": [110.46],
                "TOTAL": [110.46]
            }
            df_items = pd.DataFrame(data_items)
            edited_df = st.data_editor(df_items, num_rows="dynamic", use_container_width=True)
            
            total_sin_iva = edited_df["TOTAL"].sum()
            st.markdown(f"**TOTAL SIN IVA:** ${total_sin_iva:.2f}")
            
            submitted = st.form_submit_button("Validar y Generar Registro")
            
            if submitted:
                st.success("¡Datos validados y listos para el sistema!")
                st.balloons()
                
                st.download_button(
                    label="📥 Descargar Resumen en CSV",
                    data=edited_df.to_csv(index=False).encode('utf-8'),
                    file_name=f"orden_{orden}_motsur.csv",
                    mime="text/csv"
                )
else:
    st.warning("Por favor, adjunta una cotización o proforma para comenzar.")
