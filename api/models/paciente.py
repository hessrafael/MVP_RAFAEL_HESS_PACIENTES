from sqlalchemy import Column, String, DateTime, Boolean, Enum
from datetime import datetime
import enum
import uuid

from  models import Base

class PacienteParams(enum.Enum):
    ID = 'id'
    NOME = 'nome'
    DATA_NASC = 'data_nasc'
    SEXO = 'sexo'
    QUEIXA_PRINCIPAL = 'queixa_principal'
    UF = 'uf'
    CIDADE = 'cidade'

class SexOptions(enum.Enum):
    MASCULINO = 'M'
    FEMININO = 'F'
    def __str__(self) -> str:
        return self.value

class Paciente(Base):
    __tablename__ = 'pacients'

    pacient_id = Column(String(36), primary_key =True)
    name = Column(String(50))
    sex = Column(Enum(SexOptions))
    birthdate = Column(DateTime)
    main_complaint = Column(String(280))
    uf = Column(String(2))
    city = Column(String(50))

    created_at = Column(DateTime, default=datetime.now())
    is_active = Column(Boolean, default=True)

    def __init__(self,name: String,sex:SexOptions,birthdate:datetime,main_complaint: String, uf: String, city: String):
        self.pacient_id = uuid.uuid4().__str__()
        self.name = name
        self.sex = sex
        self.birthdate = birthdate
        self.main_complaint = main_complaint
        self.uf = uf
        self.city = city