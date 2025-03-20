import os
import mysql.connector
from pymongo import MongoClient
import datetime
import random
import sys
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Obtener las variables de entorno
mysql_host = os.getenv("MYSQL_HOST")
mysql_port = int(os.getenv("MYSQL_PORT"))
mysql_user = os.getenv("MYSQL_USER")
mysql_password = os.getenv("MYSQL_PASSWORD")
mysql_database = os.getenv("MYSQL_DATABASE")

mongo_uri = os.getenv("MONGO_URI")
mongo_db_name = os.getenv("MONGO_DB")

# Conexión a MySQL
mysql_conn = mysql.connector.connect(
    host=mysql_host,
    port=mysql_port,
    user=mysql_user,
    password=mysql_password,
    database=mysql_database
)
cursor = mysql_conn.cursor(dictionary=True)

# Consulta para obtener datos de la tabla de medicamentos
query_meds = """
    SELECT ID, Nombre_comercial, Nombre_generico, Via_administracion, Presentacion, Tipo, Cantidad
    FROM tbc_medicamentos
"""
cursor.execute(query_meds)
medicamentos = cursor.fetchall()

# Consulta para obtener IDs de usuarios con rol 'Paciente'
query_patients = """
    SELECT u.ID AS userId
    FROM tbb_usuarios u
    JOIN tbd_usuarios_roles ur ON u.ID = ur.Usuario_ID
    JOIN tbc_roles r ON ur.Rol_ID = r.ID
    WHERE r.Nombre = 'Paciente'
"""
cursor.execute(query_patients)
patient_rows = cursor.fetchall()
patient_ids = [row['userId'] for row in patient_rows]

if not patient_ids:
    print("No se encontraron usuarios con rol 'Paciente'.")
    sys.exit()

# Consultas para obtener IDs de doctores
query_doc_general = """
    SELECT u.ID AS userId
    FROM tbb_usuarios u
    JOIN tbd_usuarios_roles ur ON u.ID = ur.Usuario_ID
    JOIN tbc_roles r ON ur.Rol_ID = r.ID
    WHERE r.Nombre = 'Médico General'
"""
cursor.execute(query_doc_general)
doc_general_rows = cursor.fetchall()
doctor_general_ids = [row['userId'] for row in doc_general_rows]

query_doc_especialista = """
    SELECT u.ID AS userId
    FROM tbb_usuarios u
    JOIN tbd_usuarios_roles ur ON u.ID = ur.Usuario_ID
    JOIN tbc_roles r ON ur.Rol_ID = r.ID
    WHERE r.Nombre = 'Médico Especialista'
"""
cursor.execute(query_doc_especialista)
doc_especialista_rows = cursor.fetchall()
doctor_especialista_ids = [row['userId'] for row in doc_especialista_rows]

# Verificar que existan doctores
if not doctor_general_ids and not doctor_especialista_ids:
    print("No se encontraron doctores en la base de datos.")
    sys.exit()

# Conexión a MongoDB
mongo_client = MongoClient(mongo_uri)
mongo_db = mongo_client[mongo_db_name]
notas_medicas = mongo_db["notas_medicas"]

# Lista ampliada de síntomas realistas
sintomas_lista = [
    "fiebre alta", "tos seca", "dolor de cabeza intenso", "fatiga extrema", "dolor muscular", "escalofríos",
    "dolor de garganta", "dificultad para respirar", "dolor en el pecho", "náuseas", "vómitos",
    "diarrea", "mareo", "confusión", "dolor abdominal", "erupción cutánea", "dolor articular",
    "sibilancias", "dolor de espalda", "pérdida del olfato", "pérdida del gusto", "secreción nasal",
    "congestión nasal", "dolor de oído", "inflamación localizada", "sudoración excesiva", "visión borrosa",
    "sensación de desmayo", "dolor intenso", "dolor en las extremidades", "ansiedad", "palpitaciones"
]

# Lista de diagnósticos realistas y variados
diagnosticos_lista = [
    "Infección respiratoria aguda", "Neumonía", "Bronquitis", "Gastroenteritis viral", "Migraña crónica",
    "Sinusitis aguda", "Faringitis estreptocócica", "Alergia estacional", "COVID-19 leve", "COVID-19 moderado",
    "Infección urinaria", "Artritis reumatoide", "Hipertensión arterial", "Diabetes tipo 2",
    "EPOC (Enfermedad Pulmonar Obstructiva Crónica)", "Asma", "Fibromialgia", "Lumbalgia crónica",
    "Cistitis aguda", "Conjuntivitis bacteriana", "Otitis media", "Esguince de tobillo", "Fractura menor",
    "Gastritis erosiva", "Colitis ulcerativa", "Infección de vías respiratorias superiores"
]

# Función para generar opciones de tratamiento realistas en función del medicamento y síntomas
def generar_tratamientos(med, sintomas):
    tratamientos = []
    # Siempre se incluye el tratamiento con medicamento
    tratamiento_med = f"Medicamento: {med['Nombre_comercial']} - {med['Presentacion']} ({med['Cantidad']})"
    tratamientos.append(tratamiento_med)
    
    opciones = []
    # Opción: Reposo
    dias_reposo = random.randint(1, 7)
    opciones.append(f"Reposo: se recomienda reposo absoluto por {dias_reposo} días.")
    
    # Opción: Terapia física
    sesiones_terapia = random.randint(3, 10)
    opciones.append(f"Terapia física: se recomiendan {sesiones_terapia} sesiones de terapia física.")
    
    # Opción: Dieta especial
    opciones.append("Dieta: se recomienda una dieta baja en grasas y sal.")
    
    # Opción: Tratamiento integral
    opciones.append("Tratamiento integral: combinación de medicación, reposo y terapia física.")
    
    # Opciones adicionales según síntomas:
    if any(s in sintomas for s in ["dolor de cabeza intenso", "dolor muscular", "dolor articular", "dolor de espalda", "dolor en las extremidades"]):
        opciones.append("Analgésicos: se recomienda el uso de analgésicos para aliviar el dolor.")
        opciones.append("Antiinflamatorios: se prescriben antiinflamatorios para reducir la inflamación.")
    if any(s in sintomas for s in ["fiebre alta", "escalofríos", "dolor en el pecho"]):
        opciones.append("Compresas frías: aplicar compresas frías para ayudar a reducir la fiebre y la inflamación.")
    if any(s in sintomas for s in ["fatiga extrema", "confusión", "mareo", "ansiedad"]):
        opciones.append("Terapia ocupacional: sesiones para mejorar la funcionalidad y reducir la fatiga.")
    if any(s in sintomas for s in ["náuseas", "vómitos", "diarrea"]):
        opciones.append("Hidratación y electrolitos: se recomienda mantener una correcta hidratación y reposición de electrolitos.")
    
    # Seleccionar aleatoriamente entre 1 y 3 de estas opciones adicionales
    num_opciones = random.randint(1, 3)
    opciones_seleccionadas = random.sample(opciones, num_opciones)
    tratamientos.extend(opciones_seleccionadas)
    
    return tratamientos

# Solicitar al usuario el número de documentos a insertar
try:
    num_documentos = int(input("Ingrese el número de documentos a insertar: "))
except ValueError:
    print("El valor ingresado no es un número válido.")
    sys.exit()

# Insertar notas médicas
for _ in range(num_documentos):
    # Seleccionar aleatoriamente un medicamento
    med = random.choice(medicamentos)
    
    # Seleccionar aleatoriamente entre 3 y 6 síntomas
    num_sintomas = random.randint(3, 6)
    sintomas_seleccionados = random.sample(sintomas_lista, num_sintomas)
    
    # Seleccionar un diagnóstico aleatorio
    diagnostico = random.choice(diagnosticos_lista)
    
    # Asignar doctor basado en síntomas:
    # Si se detecta alguno de los síntomas graves, se asigna un especialista; de lo contrario, general.
    if any(s in sintomas_seleccionados for s in ["dificultad para respirar", "dolor en el pecho", "fiebre alta", "dolor intenso"]):
        if doctor_especialista_ids:
            doctor_id = random.choice(doctor_especialista_ids)
        else:
            doctor_id = random.choice(doctor_general_ids)
    else:
        if doctor_general_ids:
            doctor_id = random.choice(doctor_general_ids)
        else:
            doctor_id = random.choice(doctor_especialista_ids)
    
    # Seleccionar un paciente aleatorio
    patient_id = random.choice(patient_ids)
    
    # Generar tratamientos basados en el medicamento y síntomas
    tratamientos = generar_tratamientos(med, sintomas_seleccionados)
    
    nota = {
        "patientId": patient_id,      # ID del usuario con rol 'Paciente'
        "doctorId": doctor_id,          # ID del doctor asignado desde MySQL
        "fechaNota": datetime.datetime.now(),
        "sintomas": sintomas_seleccionados,
        "diagnostico": diagnostico,
        "tratamiento": tratamientos,
        "observaciones": "Nota médica generada a partir de datos de MySQL y tratamiento simulado.",
        "fechaSeguimiento": datetime.datetime.now() + datetime.timedelta(days=random.randint(5, 10)),
        "createdAt": datetime.datetime.now(),
        "updatedAt": datetime.datetime.now()
    }
    
    # Insertar la nota médica en la colección de MongoDB
    notas_medicas.insert_one(nota)

# Cerrar conexiones
cursor.close()
mysql_conn.close()
mongo_client.close()
