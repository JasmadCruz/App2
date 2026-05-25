from inference_sdk import InferenceHTTPClient
import streamlit as st # Añadimos streamlit para imprimir en pantalla

CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com", 
    api_key="OCb1UXipZhLKuboj2cMy"
)
MODELO_ID = "cayetano_paracetamol_genfar-2/3"

def detectar_blister(imagen_input):
    """
    imagen_input puede ser la ruta (str) o el objeto de archivo de Streamlit.
    """
    try:
        res = CLIENT.infer(imagen_input, model_id=MODELO_ID)
        
        # --- RAYOS X: MOSTRAR QUÉ DETECTA LA IA ---
        if 'predictions' in res:
            st.warning("Diagnóstico de la IA (Rayos X):")
            st.json(res['predictions']) # Esto imprimirá los datos crudos en tu pantalla
        # ------------------------------------------
        
        if 'predictions' not in res:
            return 0
            
        # Revisa si el nombre de la clase es 'alveolo_vacio' u otro
        vacios = sum(1 for p in res['predictions'] if p['class'] == 'alveolo_vacio')
        return vacios
    except Exception as e:
        st.error(f"Error interno en la conexión con la IA: {e}")
        return 0
