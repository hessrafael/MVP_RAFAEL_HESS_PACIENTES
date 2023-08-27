from pydantic import BaseModel
from typing import List
from models.paciente import Paciente, SexOptions



class PacienteSchema(BaseModel):
    """ Define como um Paciente novo deve ser adicionado
    """
    nome: str = 'Fulano de Tal'
    sexo: str = 'M'
    data_nascimento: str = 'dd/mm/aaaa'
    queixa_principal: str = 'A queixa principal do paciente'

class PacienteViewSchema(BaseModel):
    """ Define como um Paciente deve ser retornado
    """
    id: str = '206b887e-5465-4e47-b239-17ccc6ebcefa'
    nome: str = 'Fulano de Tal'
    sexo: SexOptions = 'MALE'
    data_nascimento: str = 'dd/mm/aaaa'    
    queixa_principal: str = 'A queixa principal do paciente'

class PacienteListViewSchema(BaseModel):
    """Define como uma Lista de Paciente deve ser retornada
    """
    pacientes: List[PacienteViewSchema]

class PacienteBuscaIDSchema(BaseModel):
    id: str = '206b887e-5465-4e47-b239-17ccc6ebcefa'

class PacienteAlteraQueixaSchema(BaseModel):
    id: str = '206b887e-5465-4e47-b239-17ccc6ebcefa'
    new_complaint: str = 'Nova queixa principal do paciente'

class PacienteBuscaParameterSchema(BaseModel):
    searched_param: str = 'nome'
    param: str = 'José'

def apresenta_paciente(paciente: Paciente):
    """Retorna uma visualização do paciente conforme definido em PacienteViewSchema
    """
    return{
        "id": paciente.pacient_id,
        "nome": paciente.name,
        "sexo": paciente.sex.__str__(),
        "data_nascimento": paciente.birthdate,
        "queixa_principal": paciente.main_complaint
    }

def apresenta_pacientes(pacientes: List[Paciente]):
    """Retorna uma visualização em lista conforme definido em PacienteListViewSchema
    """
    paciente_lista = []
    for paciente in pacientes:
        paciente_lista.append(apresenta_paciente(paciente))
    return {"pacientes": paciente_lista}