from fpdf import FPDF
from dto.patient_dto import PatientDTO

def generar_reporte_pdf(paciente: PatientDTO):
    pdf = FPDF()
    pdf.add_page()
    
    # Encabezado
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Reporte de Cumplimiento Terapéutico", ln=True, align='C')
    pdf.set_font("Arial", '', 12)
    pdf.cell(200, 10, txt=f"Paciente DNI: {paciente.dni}", ln=True, align='L')
    pdf.ln(10)
    
    # Tabla de Resultados
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(60, 10, "Medicamento", 1)
    pdf.cell(40, 10, "Recetado", 1)
    pdf.cell(40, 10, "Consumido", 1)
    pdf.cell(40, 10, "Faltante", 1, ln=True)
    
    pdf.set_font("Arial", '', 12)
    for med, status in paciente.estado_dosis.items():
        pdf.cell(60, 10, med, 1)
        pdf.cell(40, 10, str(status.total_recetado), 1)
        pdf.cell(40, 10, str(status.consumidas), 1)
        pdf.cell(40, 10, str(status.faltantes), 1, ln=True)
        
    return pdf.output(dest='S').encode('latin-1')