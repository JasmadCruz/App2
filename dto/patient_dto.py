from dataclasses import dataclass, field, asdict
from typing import List, Dict

@dataclass
class DosisStatus:
    total_recetado: int
    consumidas: int = 0
    faltantes: int = 0
    historial_fotos: List[int] = field(default_factory=list)

    def actualizar(self, consumidas_detectadas: int):
        self.consumidas = consumidas_detectadas
        self.faltantes = max(0, self.total_recetado - self.consumidas)
        self.historial_fotos.append(consumidas_detectadas)

@dataclass
class PatientDTO:
    dni: str
    nombre: str = "Paciente Nuevo"
    estado_dosis: Dict[str, DosisStatus] = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict):
        paciente = cls(dni=data.get('dni'), nombre=data.get('nombre', 'Paciente'))
        for med, status_data in data.get('estado_dosis', {}).items():
            paciente.estado_dosis[med] = DosisStatus(**status_data)
        return paciente