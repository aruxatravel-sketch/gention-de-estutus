import streamlit as st
import pandas as pd
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Control de Calidad - Gabinetes", layout="wide")

# Inicializar base de datos en la sesión (en una app real, esto iría a SQL o Google Sheets)
if 'db' not in st.session_state:
    st.session_state.db = pd.DataFrame(columns=[
        "ID", "Numero de Parte", "Sales Order", "Descripción", "Cantidad", "Estatus", "Inspector", "Sello", "Motivo Retrabajo", "Fecha"
    ])

st.title("🏭 Sistema de Control: Producción & Calidad")

# --- BARRA LATERAL: ENTRADA DE PRODUCCIÓN ---
with st.sidebar:
    st.header("Entrada de Gabinete (Producción)")
    with st.form("nuevo_gabinete"):
        np = st.text_input("Número de Parte")
        so = st.text_input("Sales Order")
        desc = st.text_area("Descripción")
        cant = st.number_input("Cantidad", min_value=1, value=1)
        if st.form_submit_button("Registrar en Pasillo"):
            nuevo_id = len(st.session_state.db) + 1
            nueva_fila = {
                "ID": nuevo_id, "Numero de Parte": np, "Sales Order": so,
                "Descripción": desc, "Cantidad": cant, "Estatus": "En Pasillo",
                "Inspector": "", "Sello": "", "Motivo Retrabajo": "", "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([nueva_fila])], ignore_index=True)
            st.success(f"Gabinete {so} registrado en Pasillo")

# --- CUERPO PRINCIPAL: GESTIÓN DE ESTATUS ---
tab1, tab2 = st.tabs(["📋 Tablero de Control", "📜 Bitácora Diaria"])

with tab1:
    st.subheader("Gabinetes en Proceso")
    
    if st.session_state.db.empty:
        st.info("No hay gabinetes en el sistema.")
    else:
        # Filtro por estatus
        for index, row in st.session_state.db.iterrows():
            if row['Estatus'] != "Liberado":
                with st.expander(f"📦 SO: {row['Sales Order']} - {row['Numero de Parte']} ({row['Estatus']})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Descripción:** {row['Descripción']}")
                        st.write(f"**Cantidad:** {row['Cantidad']}")
                    
                    with col2:
                        # Lógica de transición de estados
                        if row['Estatus'] == "En Pasillo":
                            if st.button(f"Iniciar Inspección #{row['ID']}"):
                                st.session_state.db.at[index, 'Estatus'] = "En Inspección"
                                st.rerun()
                        
                        elif row['Estatus'] in ["En Inspección", "Retrabajo"]:
                            st.markdown("---")
                            st.write("**Panel del Inspector**")
                            insp_nombre = st.text_input(f"Firma (Nombre)", key=f"f_{row['ID']}")
                            insp_sello = st.text_input(f"Sello (Código)", key=f"s_{row['ID']}")
                            
                            c1, c2 = st.columns(2)
                            with c1:
                                if st.button("✅ LIBERAR", key=f"lib_{row['ID']}"):
                                    if insp_nombre and insp_sello:
                                        st.session_state.db.at[index, 'Estatus'] = "Liberado"
                                        st.session_state.db.at[index, 'Inspector'] = insp_nombre
                                        st.session_state.db.at[index, 'Sello'] = insp_sello
                                        st.rerun()
                                    else:
                                        st.error("Firma y Sello requeridos")
                            
                            with c2:
                                motivo = st.text_input("Motivo de Retrabajo", key=f"mot_{row['ID']}")
                                if st.button("❌ RETRABAJO", key=f"ret_{row['ID']}"):
                                    if motivo:
                                        st.session_state.db.at[index, 'Estatus'] = "Retrabajo"
                                        st.session_state.db.at[index, 'Motivo Retrabajo'] = motivo
                                        st.rerun()
                                    else:
                                        st.error("Escribe el motivo")

with tab2:
    st.subheader("Historial de Inspección")
    # Mostrar solo Liberados o Retrabajos para la bitácora
    bitacora = st.session_state.db[st.session_state.db['Estatus'].isin(["Liberado", "Retrabajo"])]
    st.dataframe(bitacora, use_container_width=True)
    
    if not bitacora.empty:
        st.download_button("Descargar Reporte Excel", data=bitacora.to_csv().encode('utf-8'), file_name="bitacora_calidad.csv")