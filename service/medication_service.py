import os
from fpdf import FPDF
from dto.patient_dto import PatientDTO, DosisStatus
from repository.patient_repository import PatientRepository
from utils.vision_engine import detectar_blister

class MedicationService:
    def __init__(self):
        self.repo = PatientRepository()

    def inicializar_seguimiento_manual(self, paciente: PatientDTO, dict_meds: dict):
        for med, total in dict_meds.items():
            paciente.estado_dosis[med] = DosisStatus(total_recetado=int(total))
        self.repo.guardar(paciente)

    # AQUÍ ESTÁ LA MAGIA: Ahora recibe 'med_seleccionado' como parámetro extra
    def actualizar_por_vision(self, paciente: PatientDTO, med_seleccionado: str, imagen_path: str):
        """Usa Roboflow para contar alvéolos del medicamento seleccionado manualmente."""
        if med_seleccionado in paciente.estado_dosis:
            status = paciente.estado_dosis[med_seleccionado]
            
            # 1. Contamos los vacíos con tu motor Roboflow
            vacios_detectados = detectar_blister(imagen_path)
            
            # 2. Acumulamos
            nueva_cantidad_consumida = status.consumidas + vacios_detectados
            status.actualizar(nueva_cantidad_consumida)
            
            # 3. Guardamos en el JSON
            self.repo.guardar(paciente)
            return True
        return False

    def generar_reporte_pdf(self, paciente: PatientDTO):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, txt=f"Reporte Clinico - Paciente {paciente.dni}", ln=True, align='C')
        pdf.set_font("Arial", size=12)
        pdf.ln(10)
        
        pdf.cell(200, 10, txt="Resumen de Tratamiento:", ln=True)
        pdf.line(10, 30, 200, 30)
        pdf.ln(5)
        
        for med, status in paciente.estado_dosis.items():
            texto = f"Medicamento: {med} | Recetado: {status.total_recetado} | Consumido: {status.consumidas} | Faltante: {status.faltantes}"
            pdf.cell(200, 10, txt=texto, ln=True)
            
        return pdf.output(dest='S').encode('latin-1')

    def finalizar_seguimiento(self, dni: str):
        path = os.path.join(self.repo.folder, f"{dni}.json")
        if os.path.exists(path):
            new_path = path.replace(".json", "_FINALIZADO.json")
            os.rename(path, new_path)