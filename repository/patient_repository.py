from typing import Optional, List
import json
import os
from dto.patient_dto import PatientDTO

class PatientRepository:
    def __init__(self, folder="db_data"):
        self.folder = folder
        if not os.path.exists(folder): os.makedirs(folder)

    def guardar(self, paciente: PatientDTO):
        path = os.path.join(self.folder, f"{paciente.dni}.json")
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(paciente.to_dict(), f, indent=4, ensure_ascii=False)

    def buscar_por_dni(self, dni: str) -> Optional[PatientDTO]:
        path = os.path.join(self.folder, f"{dni}.json")
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return PatientDTO.from_dict(data) # ¡Magia pura!
        return None