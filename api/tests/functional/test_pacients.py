import os
import json
from conftest import ValueStorage1, ValueStorage2



def test_home_page(test_client): 
    response = test_client.get('/')
    assert response.status_code == 302

def test_add_paciente_sucesso(test_client):    
    response = test_client.post('/paciente',data={
        "nome":"Ornella Hess",
        "data_nascimento":"18/01/1931",
        "queixa_principal":"Dor no punho",
        "sexo":"F",
        "CEP": "90470230",
    })
    assert response.status_code == 200
    response_data = json.loads(response.data.decode('utf-8'))    
    assert response_data["cidade"] == "Porto Alegre"
    assert response_data["UF"] == "RS"
    assert response_data["data_nascimento"] == 'Sun, 18 Jan 1931 00:00:00 GMT'
    assert response_data["queixa_principal"] == "Dor no punho"
    assert response_data["sexo"] == "F"
    assert response_data["nome"] == "Ornella Hess"
    ValueStorage1.id = response_data["id"]

def test_add_paciente_data_errada(test_client):
    response = test_client.post('/paciente',data={
        "nome":"Ornella Hess",
        "data_nascimento":"1801/1931",
        "queixa_principal":"Dor no punho",
        "sexo":"F",
        "CEP": "90470230",
    })
    assert response.status_code == 400

def test_add_paciente_cep_errada(test_client):
    response = test_client.post('/paciente',data={
        "nome":"Ornella Hess",
        "data_nascimento":"1801/1931",
        "queixa_principal":"Dor no punho",
        "sexo":"F",
        "CEP": "90",
    })
    assert response.status_code == 400

def test_add_paciente_cep_inexistente(test_client):
    response = test_client.post('/paciente',data={
        "nome":"Ornella Hess",
        "data_nascimento":"1801/1931",
        "queixa_principal":"Dor no punho",
        "sexo":"F",
        "CEP": "99999999",
    })
    assert response.status_code == 400

def test_get_paciente_id(test_client):
    response = test_client.get(f'/paciente?id={ValueStorage1.id}')
    assert response.status_code == 200
    response_data = json.loads(response.data.decode('utf-8'))    
    assert response_data["cidade"] == "Porto Alegre"
    assert response_data["UF"] == "RS"
    assert response_data["data_nascimento"] == 'Sun, 18 Jan 1931 00:00:00 GMT'
    assert response_data["queixa_principal"] == "Dor no punho"
    assert response_data["sexo"] == "F"
    assert response_data["nome"] == "Ornella Hess"

def test_get_paciente_nome(test_client):
    searched_param = 'nome'
    param = 'orNella Hess'
    response = test_client.get(f'/pacientes?searched_param={searched_param}&param={param}')
    assert response.status_code == 200

def test_change_complaint(test_client):
    response = test_client.put('/change_complaint',data={
        "id":ValueStorage1.id,
        "new_complaint":"nova queixa"
    })
    assert response.status_code == 200
    response_data = json.loads(response.data.decode('utf-8'))
    assert response_data["id"] == ValueStorage1.id
    assert response_data["queixa_principal"] == "nova queixa"
    assert response_data["cidade"] == "Porto Alegre"
    assert response_data["UF"] == "RS"
    assert response_data["data_nascimento"] == 'Sun, 18 Jan 1931 00:00:00 GMT'
    assert response_data["sexo"] == "F"
    assert response_data["nome"] == "Ornella Hess"

def test_add_segundo_paciente_sucesso(test_client):    
    response = test_client.post('/paciente',data={
        "nome":"Carla Hess",
        "data_nascimento":"17/12/1963",
        "queixa_principal":"Dermatite",
        "sexo":"F",
        "CEP": "90470230",
    })
    assert response.status_code == 200
    response_data = json.loads(response.data.decode('utf-8'))    
    assert response_data["cidade"] == "Porto Alegre"
    assert response_data["UF"] == "RS"
    assert response_data["data_nascimento"] == 'Tue, 17 Dec 1963 00:00:00 GMT'
    assert response_data["queixa_principal"] == "Dermatite"
    assert response_data["sexo"] == "F"
    assert response_data["nome"] == "Carla Hess"
    ValueStorage2.id = response_data["id"]

def test_get_all_pacientes(test_client):
    response = test_client.get(f'/all_pacientes')
    assert response.status_code == 200
    response_data = json.loads(response.data.decode('utf-8'))    
    assert len(response_data["pacientes"]) == 2
    assert response_data["pacientes"][0]["id"] == ValueStorage1.id
    assert response_data["pacientes"][0]["queixa_principal"] == "nova queixa"
    assert response_data["pacientes"][0]["cidade"] == "Porto Alegre"
    assert response_data["pacientes"][0]["UF"] == "RS"
    assert response_data["pacientes"][0]["data_nascimento"] == 'Sun, 18 Jan 1931 00:00:00 GMT'
    assert response_data["pacientes"][0]["sexo"] == "F"
    assert response_data["pacientes"][0]["nome"] == "Ornella Hess"
    assert response_data["pacientes"][1]["cidade"] == "Porto Alegre"
    assert response_data["pacientes"][1]["UF"] == "RS"
    assert response_data["pacientes"][1]["data_nascimento"] == 'Tue, 17 Dec 1963 00:00:00 GMT'
    assert response_data["pacientes"][1]["queixa_principal"] == "Dermatite"
    assert response_data["pacientes"][1]["sexo"] == "F"
    assert response_data["pacientes"][1]["nome"] == "Carla Hess"
    assert response_data["pacientes"][1]["id"] == ValueStorage2.id

    