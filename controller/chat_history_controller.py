from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from repository.chat_history_repository import ChatHistoryRepository
from utils.responses import Responses

# Se crea el blueprint
chat_history_bp = Blueprint('chat_history', __name__, url_prefix='/api/chat_history')
chatHistoryRepository = ChatHistoryRepository()


import os
import re
from openai import OpenAI
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

template = """
Eres un asistente experto en leyes de tránsito. Responde con base en las normas, leyes, codigos de transito, infracciones, sanciones
y decretos supremos proporcionados.
Tu tarea es:
1. Analizar el contexto proporcionado en español
2. Entender la pregunta en español incluso si está mal formulada
3. Generar una respuesta clara y concisa en español

El usuario puede usar palabras y terminos diferentes a los que se encuentran en el contexto, asi que cuando no halles alguna similitud,
puedes buscar algún sinónimo. Como en los siguientes ejemplos:
- Manejar borracho = Manejar en estado de ebriedad = Manejar ebrio
- Mal estacionado = Mal parqueado
- Multa = Sanción
- Tipo de licencia = Categoría de licencia
- Choque = Accidente

Si no encuentras la respuesta en el contexto, puedes responder con informacion similar.

Pregunta : {question}
Contexto : {context}
Respuesta: 
"""

# Configuración de API DeepSeek
DEEPSEEK_API_KEY = "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"
client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://openrouter.ai/api/v1")

# Directorios
TEXTS_DIR = "documents/"
DB_DIR = "vector_db/"

os.makedirs(TEXTS_DIR, exist_ok=True)
os.makedirs(DB_DIR, exist_ok=True)

# Inicializar embeddings y base de datos vectorial
embeddings = OllamaEmbeddings(model="nomic-embed-text")
vector_store = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)


@chat_history_bp.route('/get_all', methods = ['GET'])
#@jwt_required()
def get_all_chats():
    chats = chatHistoryRepository.get_all()
    response = Responses.success(
        code = 0,
        data = chats,
        description = 'Chats obtenidos correctamente'
    )
    return jsonify(response)

@chat_history_bp.route('/load/<int:user_id>', methods=['GET'])
# @jwt_required()
def get_by_user_id(user_id):
    user_chat = chatHistoryRepository.get_by_user_id(user_id)
    if user_chat:
        response = Responses.success(
            code = 0,
            data = user_chat,
            description = 'Chat del usuario encontrado'
        )
        return jsonify(response)
    else:
        response = Responses.error(
            code = 1,
            description = f'Chat del usuario con ID {user_id} no encontrado'
        )
        return jsonify(response)
    
@chat_history_bp.route('/get_last/<int:user_id>', methods=['GET'])
# @jwt_required()
def get_by_user_id_last_message(user_id):
    user_chat = chatHistoryRepository.get_by_user_id_last_message(user_id, 1)
    if user_chat:
        response = Responses.success(
            code = 0,
            data = user_chat,
            description = 'Ultimo mensaje encontrado'
        )
        return jsonify(response)
    else:
        response = Responses.error(
            code = 1,
            description = f'Chat del usuario con ID {user_id} no encontrado'
        )
        return jsonify(response)

# Cargar y procesar archivos de texto
@chat_history_bp.route('/procesar-texto', methods=['GET'])
def process_text_files():
    docs = []
    for file_name in os.listdir(TEXTS_DIR):
        file_path = os.path.join(TEXTS_DIR, file_name)
        #loader = TextLoader(file_path, encoding="utf8")
        loader = TextLoader(file_path, encoding="utf-8")
        documents = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
        chunks = text_splitter.split_documents(documents)
        docs.extend(chunks)

    vector_store.add_documents(docs)
    print("documentos cargados: ", len(docs))
    return jsonify({"message": "Archivos procesados correctamente", "docs_count": len(docs)})

# API para subir archivos de texto
@chat_history_bp.route('/upload_docs', methods=['POST'])
def upload_docs():
    if 'file' not in request.files:
        return jsonify({"error": "No se proporcionó archivo"}), 400
    
    file = request.files['file']
    file_path = os.path.join(TEXTS_DIR, file.filename)
    file.save(file_path)

    response = process_text_files()
    return jsonify({"message": response})

def clean_response(text):
    # Eliminar contenido entre etiquetas <think> y </think>
    cleaned = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    # Eliminar lineas vacias extras que puedan quedar
    cleaned = re.sub(r'\n\s\*n', '\n\n', cleaned)
    return cleaned.strip()



@chat_history_bp.route('/chat', methods=['POST'])
def chat_generico():
    # Obtener el mensaje del usuario desde la solicitud
    user_message = request.json.get('message')

    if not user_message:
        return jsonify({"error": "No se proporcionó un mensaje"}), 400

    # Crear la solicitud a la API de DeepSeek
    try:
        response = client.chat.completions.create(
            model="deepseek/deepseek-r1:free",
            messages=[
                {
                    "role": "system", 
                    "content": """
                    You are a helpful assistant
                    """
                },
                {
                    "role": "user", 
                    "content": user_message
                },
            ],
        )

        assistant_response = response.choices[0].message.content
        return jsonify({"response": assistant_response})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


SYNONYMS = {
    "auto": "vehículo",
    "carro": "vehículo",
    "vehiculo": "vehículo",
    "moto": "motocicleta",

    "manejo": "conduzco",
    "manejando": "conduciendo",
    "manejaba": "conducía",

    "placa": "matrícula",

    "boleta": "multa",
    "infracción": "sanción",
    "penalización": "sanción",
    "castigo": "sanción",
    "falta": "infracción",

    "multas": "sanciones",
    "licencia vencida": "licencia caducada",
    "manejar": "conducir",

    "paso de cebra": "cruce peatonal",
    "peatón": "persona",


    "chofer": "conductor",
    "policía": "oficial de tránsito",
    "paco": "oficial de tránsito",

    "borracho": "estado de embriaguez",
    "yema": "estado de embriaguez",
    "ebrio": "estado de embriaguez",
    "alcoholizado": "estado de embriaguez",
    "drogado": "bajo influencia de sustancias",
    "pasado de copas": "bebidas alcohólicas",
    "cerveza": "bebida alcohólica",
    "ron": "bebida alcohólica",
    "trago": "bebida alcohólica",
    "alcohol": "bebida alcohólica",

    "rebasar": "adelantar"
}



def normalize_query(text):
    for k, v in SYNONYMS.items():
        pattern = r'\b' + re.escape(k) + r'\b'
        text = re.sub(pattern, v, text, flags=re.IGNORECASE)
    return text


@chat_history_bp.route('/chat_transito', methods=['POST'])
def chat_transito():
    data = request.get_json()
    
    user_message = data.get('message')

    user_id = data.get('user_id')

    chat_history_repository = ChatHistoryRepository()

    if not user_message:
        return jsonify({"error": "No se proporcionó un mensaje"}), 400
    
    # Normalizar mensajes del usuario
    normalized_message = normalize_query(user_message)
    # Buscar fragmentos de texto relevantes
    documents = vector_store.similarity_search(normalized_message)
    context = "\n\n".join([doc.page_content for doc in documents])

    last_message = chat_history_repository.get_by_user_id_last_message(user_id)


    # Crear la solicitud a la API de DeepSeek
    try:
        response = client.chat.completions.create(
            model="deepseek/deepseek-r1:free",
            messages=[
                {
                    "role": "system", 
                    "content": template
                },
                {
                    "role": "user", 
                    "content": f"Pregunta: {user_message}\nContexto: {context}"
                }
            ],
            stream = False
        )
        print(response)
        assistant_response = clean_response(response.choices[0].message.content)

        add_message = chat_history_repository.create(
            user_id = user_id,
            user_message = user_message,
            assistant_response = assistant_response
        )

        if add_message:
            return jsonify(Responses.success(
                code = 0,
                data = add_message,
                description = "Mensajes registrados correctamente"
            ))
        else:
            return jsonify(Responses.error(
                code = 1,
                description = "Error al registrar los mensajes"
            ))

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@chat_history_bp.route('/add_message', methods=['POST'])
# @jwt_required()
def create_chat():
    data = request.json
    
    user_id = data.get('user_id')
    user_message = data.get('user_message')
    assistant_response = data.get('assistant_response')
    
    if user_id and user_message and assistant_response:
        newChatHistory = ChatHistoryRepository.create(
            user_id = user_id,
            user_message = user_message,
            assistant_response = assistant_response
        )
        if newChatHistory:
            response = Responses.success(
                code = 0,
                data = newChatHistory,
                description = 'Mensaje añadido correctamente'
            )   
            return jsonify(response)
    else:
        response = Responses.error(
                code = 1,
                description = 'Error al validar los datos'
            )   
        return jsonify(response)

@chat_history_bp.route('/delete/<int:user_id>', methods=['DELETE'])
#@jwt_required()
def delete_user_per(user_id):
    deleted_chat = chatHistoryRepository.delete(user_id)
    if deleted_chat:
        return jsonify(Responses.success(
            code = 0,
            data = deleted_chat,
            description = "Chat eliminado correctamente"
        ))
    else:
        return jsonify(Responses.error(f'Usuario con ID {user_id} no encontrado'))
    


