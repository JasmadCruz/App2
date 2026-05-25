import streamlit as st
from service.medication_service import MedicationService
from dto.patient_dto import PatientDTO
import os

st.set_page_config(page_title="Admisión Cayetano PRO", layout="wide")

if 'service' not in st.session_state: st.session_state.service = MedicationService()
if 'pacientes' not in st.session_state: st.session_state.pacientes = {}

# Carga inicial desde repositorio
def cargar_pacientes():
    repo = st.session_state.service.repo
    for file in os.listdir(repo.folder):
        if file.endswith(".json"):
            dni = file.replace(".json", "")
            paciente = repo.buscar_por_dni(dni)
            if paciente: st.session_state.pacientes[dni] = paciente

if not st.session_state.pacientes: cargar_pacientes()

def mostrar_app():
    col_logo, col_titulo = st.columns([1, 6])
    with col_logo: st.image("https://cdn-icons-png.flaticon.com/512/822/822118.png", width=70)
    with col_titulo: st.title("Admisión Cayetano PRO")

    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.auth = False
        st.rerun()

    tab1, tab2 = st.tabs(["📋 Admisión Manual", "🔍 Seguimiento Clínico"])

    with tab1:
        st.header("Gestión de Pacientes")
        dni_del = st.selectbox("Borrar Paciente registrado:", [""] + list(st.session_state.pacientes.keys()))
        if st.button("Eliminar Paciente"):
            if dni_del:
                path = os.path.join(st.session_state.service.repo.folder, f"{dni_del}.json")
                if os.path.exists(path): os.remove(path)
                del st.session_state.pacientes[dni_del]
                st.success("Paciente eliminado.")
                st.rerun()
        
        st.divider()
        st.subheader("Registrar Nuevo Paciente")
        dni = st.text_input("DNI del Paciente:")
        meds_catalogo = ["PARACETAMOL", "IBUPROFENO", "AMOXICILINA", "LORATADINA"]
        sel = st.multiselect("Medicamentos recetados:", meds_catalogo)
        cantidades = {m: st.number_input(f"Cantidad {m}:", 1, 100) for m in sel}

        if st.button("Confirmar e Iniciar Tratamiento"):
            if dni and cantidades:
                paciente = PatientDTO(dni=dni)
                st.session_state.service.inicializar_seguimiento_manual(paciente, cantidades)
                st.session_state.pacientes[dni] = paciente
                st.success(f"Tratamiento iniciado para {dni}.")
                st.rerun()
            else: st.error("Complete DNI y medicamentos.")

    with tab2:
        st.header("Control de Adherencia (Visión)")
        dni_b = st.selectbox("Seleccionar Paciente Activo:", [""] + list(st.session_state.pacientes.keys()))
        
        if dni_b:
            p = st.session_state.pacientes[dni_b]
            st.info(f"📋 **Paciente:** {p.dni}")
            
            # El usuario selecciona manualmente qué medicamento va a procesar en esta captura
            med = st.selectbox("Medicamento a controlar:", list(p.estado_dosis.keys()))
            
            if med:
                status = p.estado_dosis[med]
                
                # --- SECCIÓN: BLÍSTER POR BLÍSTER ---
                st.write("---")
                
                # 1. Historial de blísteres cargados secuencialmente
                if status.historial_fotos:
                    st.write(f"### Historial de procesamiento para {med}")
                    for idx, cantidad in enumerate(status.historial_fotos):
                        # Muestra la cantidad acumulada o el registro por foto de forma limpia
                        st.info(f"✅ **Foto / Blíster #{idx + 1}:** {cantidad} dosis totales registradas hasta este punto.")
                
                # 2. Captura del nuevo blíster enfocado únicamente en el medicamento seleccionado
                nuevo_id = len(status.historial_fotos) + 1
                with st.expander(f"📸 Cargar Foto para Blíster #{nuevo_id} de {med}", expanded=True):
                    metodo = st.radio("¿Cómo desea cargar la foto?", ["Cámara en vivo", "Subir desde almacenamiento"], key=f"radio_{dni_b}_{med}_{nuevo_id}")
                    
                    archivo = None
                    if metodo == "Cámara en vivo":
                        archivo = st.camera_input("Tomar foto", key=f"cam_{dni_b}_{med}_{nuevo_id}")
                    else:
                        archivo = st.file_uploader("Subir foto", type=['jpg', 'jpeg', 'png'], key=f"up_{dni_b}_{med}_{nuevo_id}")
                    
                    if archivo and st.button("Analizar Dosis con Roboflow", key=f"btn_{dni_b}_{med}_{nuevo_id}"):
                        path = "temp_vision.jpg"
                        with open(path, "wb") as f: f.write(archivo.getbuffer())
                        
                        with st.spinner(f"Analizando blíster de {med} con IA..."):
                            # Pasamos el 'med' seleccionado manualmente al servicio para evitar errores de OCR
                            exito = st.session_state.service.actualizar_por_vision(p, med, path)
                        
                        if exito:
                            st.success(f"¡Blíster de {med} procesado e historial actualizado con éxito!")
                        else: 
                            st.error("Hubo un problema al procesar el blíster seleccionado.")
                            
                        if os.path.exists(path): os.remove(path)
                        st.rerun() # Fuerza el refresco clínico para listar el nuevo blíster en el historial

                # Métricas actualizadas en tiempo real del medicamento seleccionado
                st.write("### Estado Actual de Adherencia")
                c1, c2, c3 = st.columns(3)
                c1.metric("Total Recetado", status.total_recetado)
                c2.metric("Total Consumidas (Detecciones)", status.consumidas)
                c3.metric("Faltantes por Consumir", status.faltantes)

            # --- SECCIÓN: FINALIZAR Y GENERAR REPORTE CLINICO ---
            st.write("---")
            st.subheader("Cierre de Tratamiento")
            
            pdf_data = st.session_state.service.generar_reporte_pdf(p)
            
            col_pdf1, col_pdf2 = st.columns(2)
            with col_pdf1:
                # Botón de descarga nativo de Streamlit, no interfiere con estados mutables ni genera bucles
                st.download_button("📄 Descargar Reporte PDF", data=pdf_data, file_name=f"Reporte_{dni_b}.pdf", mime="application/pdf")
            
            with col_pdf2:
                # Archiva de manera definitiva quitando al paciente de la lista de activos
                if st.button("🏁 Archivar Paciente (Finalizar Seguimiento)"):
                    st.session_state.service.finalizar_seguimiento(dni_b)
                    del st.session_state.pacientes[dni_b]
                    st.success("El paciente ha sido archivado correctamente.")
                    st.rerun()

# --- Autenticación (Usuario y Contraseña con persistencia controlada) ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🏥 Acceso Médico - Cayetano")
    usuario = st.text_input("Usuario Médico")
    pwd = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        if usuario == "medico" and pwd == "cayetano2024":
            st.session_state.auth = True
            st.rerun()
        else: 
            st.error("Usuario o contraseña incorrectos")
else: 
    mostrar_app()