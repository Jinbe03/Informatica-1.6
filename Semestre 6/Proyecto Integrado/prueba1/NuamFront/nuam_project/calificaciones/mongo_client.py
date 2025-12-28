from pymongo import MongoClient

# Conexión
client = MongoClient('mongodb://localhost:27017/')
db = client['nuam_mongo']  # Nombre de la base de datos
collection = db['auditoria']  # Colección donde guardaremos logs de auditoría

# Insertar un log
collection.insert_one({
    "usuario": "admin",
    "accion": "Creó calificación",
    "empresa": "Empresa XYZ",
    "fecha": "2025-10-09T22:50:00"
})

# Consultar logs
logs = collection.find().sort("fecha", -1)
for log in logs:
    print(log)
