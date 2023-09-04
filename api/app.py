from flask_openapi3 import OpenAPI, Info, Tag
from flask import redirect
from urllib.parse import unquote
import requests
import json

from sqlalchemy.exc import IntegrityError

from models import Session, Paciente, PacienteParams 
#from logger import logger
from schemas import *
from flask_cors import CORS
import datetime

info = Info(title="API gestão de Pacientes", version="1.0.0")
app = OpenAPI(__name__, info=info)
CORS(app)

# definindo tags
home_tag = Tag(name="Documentação", description="Seleção de documentação: Swagger, Redoc ou RapiDoc")
paciente_tag = Tag(name="Paciente", description="Adição, visualização e remoção de Pacientes à base")


@app.get('/', tags=[home_tag])
def home():
    """Redireciona para /openapi, tela que permite a escolha do estilo de documentação.
    """
    return redirect('/openapi')

@app.post('/paciente',tags=[paciente_tag],
          responses={"200":PacienteViewSchema,"400":ErrorSchema, "409":ErrorSchema})
def add_paciente(form: PacienteSchema):
    """Adiciona um novo paciente à base
    """
    
    try:        
        parsed_birthdate = datetime.datetime.strptime(form.data_nascimento, '%d/%m/%Y')
    except:
        error_msg = "Valor inválido para data. Insira uma data no formato dd/mm/aaaa"
        return {"message": error_msg}, 400
    
    try:
        response = requests.get(f'https://viacep.com.br/ws/{form.cep}/json/')
    except Exception as e:
        error_msg = "Sistema de consulta CEP inacessível"
        return {"message": error_msg}, 400
    
    
    if response.status_code != 200:
        error_msg = "Valor inválido para o CEP. Insira apenas números"
        return {"message": error_msg}, 400
    else:
        response = response.json()
        if 'uf' in response:
            uf = response['uf']
            city = response['localidade']
        else:
            error_msg = "CEP não encontrado na base de dados"
            return {"message": error_msg}, 400

    try:
        paciente = Paciente(
            name=form.nome,
            sex= SexOptions(form.sexo),
            birthdate=parsed_birthdate,
            main_complaint=form.queixa_principal,
            uf=uf,
            city=city
        )
    except:
        error_msg = "Valores inválidos de parametros para nova instância de Paciente"
        return {"message": error_msg}, 400

    try:
        # criando conexão com a base
        session = Session()
        # adicionando instancia
        session.add(paciente)
        # efetivando o camando de adição de instancia
        session.commit()
        return apresenta_paciente(paciente), 200

    except IntegrityError as e:
        error_msg = "Paciente com mesmo id já salvo na base :/"
        return {"message": error_msg}, 409   
    
    
    except Exception as e:
        # caso um erro fora do previsto
        error_msg = "Não foi possível salvar novo paciente :/"
        print(e.__str__())
        print(type(e))
        return {"message": error_msg}, 400

@app.get('/all_pacientes',tags=[paciente_tag],
         responses={"200":PacienteListViewSchema,"400":ErrorSchema, "404":ErrorSchema})
def get_all_pacientes():
    """Retorna todos os pacientes cadastrados no banco
    """
    try:
        # criando conexão com o banco
        session = Session()
        # buscando todas as instâncias ativas
        pacientes = session.query(Paciente).filter(Paciente.is_active == True).all()

        if not pacientes:
            error_msg = 'Nenhum paciente encontrado'
            return {"message": error_msg},404
        else:
            #retorna os pacientes
            return apresenta_pacientes(pacientes), 200
    except Exception as e:
        error_msg = "Não foi possível realizar a consulta de Pacientes"
        print(e.__str__())
        return {"message": error_msg}, 400

@app.get('/paciente',tags=[paciente_tag],
         responses={"200":PacienteViewSchema,"400":ErrorSchema, "404":ErrorSchema})
def get_paciente(query: PacienteBuscaIDSchema):
    """Retorna um paciente com base no seu ID
    """
    paciente_id = query.id
    try:
        # criando conexão com o banco
        session = Session()
        # buscando todas as instâncias ativas
        paciente = session.query(Paciente).filter(Paciente.is_active == True, Paciente.pacient_id == paciente_id).first()
        if not paciente:
            error_msg = 'Nenhum paciente encontrado com o id'
            return {"message": error_msg},404
        else:
            #retorna o paciente
            return apresenta_paciente(paciente), 200
    except Exception as e:
        print(e.__str__())
        error_msg = "Não foi possível realizar a consulta de Pacientes"
        return {"message": error_msg}, 400

@app.get('/pacientes',tags=[paciente_tag],
         responses={"200":PacienteListViewSchema,"400":ErrorSchema, "404":ErrorSchema})
def get_pacientes(query: PacienteBuscaParameterSchema):
    """Retorna Pacientes com base em um parametro (id, nome, sexo, data_nasc, queixa_principal, uf ou cidade) e o valor de busca
    """
    try:
        # criando conexão com o banco
        session = Session()
        # buscando todas as instâncias ativas conforme o param
        query_param = query.param
        print(query.searched_param)
        if PacienteParams(query.searched_param) == PacienteParams.ID:
            pacientes = session.query(Paciente).filter(Paciente.is_active == True, Paciente.pacient_id == query_param).all()
        elif PacienteParams(query.searched_param) == PacienteParams.NOME:
            pacientes = session.query(Paciente).filter(Paciente.is_active == True, Paciente.name.ilike(f"%{query.param}%")).all()
        elif PacienteParams(query.searched_param) == PacienteParams.DATA_NASC:
            query_param = datetime.datetime.strptime(query.param, '%d/%m/%Y')
            pacientes = session.query(Paciente).filter(Paciente.is_active == True, Paciente.birthdate == query_param).all()
        elif PacienteParams(query.searched_param) == PacienteParams.SEXO:
            pacientes = session.query(Paciente).filter(Paciente.is_active == True, Paciente.sex == SexOptions(query_param)).all()
        elif PacienteParams(query.searched_param) == PacienteParams.QUEIXA_PRINCIPAL:
            pacientes = session.query(Paciente).filter(Paciente.is_active == True, Paciente.main_complaint.ilike(f"%{query.param}%")).all()
        elif PacienteParams(query.searched_param) == PacienteParams.UF:
            pacientes = session.query(Paciente).filter(Paciente.is_active == True, Paciente.uf == query_param.upper()).all()
        elif PacienteParams(query.searched_param) == PacienteParams.CIDADE:
            pacientes = session.query(Paciente).filter(Paciente.is_active == True, Paciente.city == query_param.title()).all()
        else:
            error_msg = 'Parametro inválido para pesquisa'
            return {"message":error_msg}, 400

        if not pacientes:
            error_msg = 'Nenhum paciente encontrado com o parametro'
            return {"message": error_msg},404
        else:
            #retorna o paciente
            return apresenta_pacientes(pacientes), 200
    except Exception as e:
        error_msg = "Não foi possível realizar a consulta de Pacientes"
        print(e)
        return {"message": error_msg}, 400
    
@app.delete('/delete_paciente',tags=[paciente_tag],
            responses={"200":PacienteViewSchema,"400":ErrorSchema, "404":ErrorSchema})
def delete_paciente(form: PacienteBuscaIDSchema):
    """Rota para deletar paciente com base no seu ID
    """
    try:
        # criando conexão com o banco
        session = Session()
        # buscando todas a instância ativas
        paciente = session.query(Paciente).filter(Paciente.is_active == True, Paciente.pacient_id == form.id).first()

        if not paciente:
            error_msg = 'Nenhum paciente encontrado com o id'
            return {"message": error_msg},404
        else:
            #busca os procedimentos do paciente
            try:
                response = requests.get(f'http://127.0.0.1:5002/procedimentos_paciente?id={form.id}')
            except Exception as e:
                error_msg = "Consulta aos procedimentos inacessível"
                return {"message": error_msg}, 400

            if response.status_code == 404:
                #Não há procedimento associado, pode seguir com a deleção do paciente
                paciente.is_active = False
            
            elif response.status_code == 200:
                
                #desativa os procedimentos do paciente (outro servico cuida da lógica)
                procedimentos = response.json().get("procedimentos")
                headers = {'Content-Type': 'application/json'}
                payload = {'ids': [{'id': procedimento['id']} for procedimento in procedimentos]}
                
                try:
                    response = requests.delete('http://127.0.0.1:5002/delete_procedimentos',data=json.dumps(payload),headers=headers)
                except Exception as e:
                    error_msg = "Serviço de deleção dos procedimentos inacessível"
                    return {"message": error_msg}, 400
                
                if response.status_code != 200:
                    error_msg = "Não foi possível realizar a deleção do Paciente por causa dos procedimentos associados"
                    return {"message": error_msg}, 400
                else:
                    #desativa o paciente (soft delete)
                    paciente.is_active = False

            else: 
                #Erro na consulta de procedimentos
                error_msg = "Não foi possível realizar a deleção do Paciente por causa dos procedimentos associados"
                return {"message": error_msg}, 400      

        session.commit()
        return apresenta_paciente(paciente)
    
    except Exception as e:
        print(e.__str__())
        error_msg = "Não foi possível realizar a deleção do Paciente"
        return {"message": error_msg}, 400

@app.put('/change_complaint', tags=[paciente_tag],
         responses={"200":PacienteViewSchema,"400":ErrorSchema, "404":ErrorSchema})
def change_complaint(form: PacienteAlteraQueixaSchema):
    """Rota para alterar a queixa principal do paciente
    """
    try:
        # criando conexão com o banco
        session = Session()
        # buscando todas a instância ativas
        paciente = session.query(Paciente).filter(Paciente.is_active == True, Paciente.pacient_id == form.id).first()

        if not paciente:
            error_msg = 'Nenhum paciente encontrado com o id'
            return {"message": error_msg},404
        else:
            #Altera o paciente             
            paciente.main_complaint = form.new_complaint
        session.commit()
        return apresenta_paciente(paciente)
    
    except Exception as e:
        print(e.__str__())
        error_msg = "Não foi possível realizar a alteração do Paciente"
        return {"message": error_msg}, 400