from pydantic import BaseModel
from typing import List, Optional


# Modelo de entrada (sem o ID)
class TarefaCreate(BaseModel):
    titulo: str
    descricao: Optional[str] = None
    concluida: bool = False


# Modelo de saída (com ID)
class Tarefa(TarefaCreate):
    id: int