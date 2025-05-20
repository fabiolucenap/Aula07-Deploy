from fastapi import FastAPI, HTTPException
from typing import List
from Tarefa import TarefaCreate, Tarefa
from fastapi.middleware.cors import CORSMiddleware
import oracledb
import os
from dotenv import load_dotenv


# Carrega as variáveis do .env
load_dotenv()


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Pode colocar domínios específicos aqui no futuro
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_SID = os.getenv("DB_SID")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")


proximo_id: int = 0  # contador de ID automático


# Rota para criar uma nova tarefa (ID gerado automaticamente no backend Python)
@app.post("/tarefas", response_model=Tarefa)
def criar_tarefa(tarefa: TarefaCreate):
    global proximo_id
    proximo_id += 1
    nova_tarefa = Tarefa(id=proximo_id, **tarefa.dict())


    dsn = oracledb.makedsn(host=DB_HOST, port=DB_PORT, sid=DB_SID)
    conn = oracledb.connect(user=DB_USER, password=DB_PASS, dsn=dsn)


    cursor = conn.cursor()


    cursor.execute("INSERT INTO TB_TAREFA (ID, TITULO, DESCRICAO, CONCLUIDA) VALUES (:valor1, :valor2, :valor3, :valor4)", valor1=nova_tarefa.id, valor2=nova_tarefa.titulo, valor3=nova_tarefa.descricao, valor4=nova_tarefa.concluida)
    conn.commit()


    cursor.close()
    conn.close()


    return nova_tarefa    
   


# Rota para listar todas as tarefas
@app.get("/tarefas", response_model=List[Tarefa])
def listar_tarefas():


    dsn = oracledb.makedsn(host=DB_HOST, port=DB_PORT, sid=DB_SID)
    conn = oracledb.connect(user=DB_USER, password=DB_PASS, dsn=dsn)


    cursor = conn.cursor()


    cursor.execute('SELECT * FROM TB_TAREFA')


    rows = cursor.fetchall()


    cursor.close()
    conn.close()


    return [
    {
        "id": row[0],
        "titulo": row[1],
        "descricao": row[2],
        "concluida": row[3] == 'S'
    }
    for row in rows
]


# Rota para obter uma tarefa específica
@app.get("/tarefas/{tarefa_id}", response_model=Tarefa)
def obter_tarefa(tarefa_id: int):
    dsn = oracledb.makedsn(host=DB_HOST, port=DB_PORT, sid=DB_SID)
    conn = oracledb.connect(user=DB_USER, password=DB_PASS, dsn=dsn)


    cursor = conn.cursor()


    cursor.execute('SELECT * FROM TB_TAREFA WHERE ID = :valor1', valor1=tarefa_id)


    row = cursor.fetchone()
   
    if row:
        return {
            "id": row[0],
            "titulo": row[1],
            "descricao": row[2],
            "concluida": row[3] == 'S'
        }
    raise HTTPException(status_code=404, detail="Tarefa não encontrada.")




# Rota para atualizar uma tarefa completa
@app.put("/tarefas/{tarefa_id}")
def atualizar_tarefa(tarefa_id: int, tarefa_atualizada: TarefaCreate):
    dsn = oracledb.makedsn(host=DB_HOST, port=DB_PORT, sid=DB_SID)
    conn = oracledb.connect(user=DB_USER, password=DB_PASS, dsn=dsn)


    cursor = conn.cursor()


    cursor.execute("UPDATE TB_TAREFA SET TITULO=:valor2, DESCRICAO=:valor3 WHERE ID=:valor1", valor1=tarefa_id, valor2=tarefa_atualizada.titulo, valor3=tarefa_atualizada.descricao)
    conn.commit()


    cursor.close()
    conn.close()


    return {"mensagem": "Tarefa atualizada com sucesso"}




# Rota para atualizar apenas o status da tarefa
@app.patch("/tarefas/{tarefa_id}/status")
def atualizar_status_tarefa(tarefa_id: int, concluida: bool):
    dsn = oracledb.makedsn(host=DB_HOST, port=DB_PORT, sid=DB_SID)
    conn = oracledb.connect(user=DB_USER, password=DB_PASS, dsn=dsn)


    cursor = conn.cursor()


    cursor.execute("UPDATE TB_TAREFA SET CONCLUIDA=:valor2 WHERE ID=:valor1", valor1=tarefa_id, valor2='S' if concluida else 'N')
    conn.commit()


    cursor.close()
    conn.close()


    return {"mensagem": "Tarefa concluída com sucesso"}



# Rota para excluir uma tarefa
@app.delete("/tarefas/{tarefa_id}")
def deletar_tarefa(tarefa_id: int):
    dsn = oracledb.makedsn(host=DB_HOST, port=DB_PORT, sid=DB_SID)
    conn = oracledb.connect(user=DB_USER, password=DB_PASS, dsn=dsn)


    cursor = conn.cursor()


    cursor.execute("DELETE FROM TB_TAREFA WHERE ID=:valor1", valor1=tarefa_id)
    conn.commit()


    cursor.close()
    conn.close()


    return {"mensagem": "Tarefa excluída com sucesso"}