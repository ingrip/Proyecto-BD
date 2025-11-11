#este es el de mongo
#funcion para q borre cuando estan mal las credenciales
#boton para ver contraseña
import pymongo
from datetime import datetime
from bson.objectid import ObjectId
def conexion():
    from pymongo import MongoClient
    try:
        uri = "mongodb://localhost:27017"
        client = MongoClient(uri)
        database = client["Blog"]
        ColeccionUsers = database["Users"]
        ColeccionArticles = database["Articles"]
        ColeccionComments = database["Comments"]
        ColeccionCategories = database["Categories"]
        ColeccionTags = database["Tags"]

        # start example code here
        # end example code here
        return database
        #client.close()
    except Exception as e:
        raise Exception(
            "Ocuurio el sig error: ", e)

#Función que hace conexión con la base de datos y ejecuta la función para verificar un inicio de sesión
#probada
def verificar_usuario(correo, contraseña):
    try:
        db = conexion()
        users = db["Users"]

        # Busca un documento que coincida con el correo y la contraseña
        usuario = users.find_one({"email": correo, "password": contraseña})

        if usuario:
            return usuario["name"] if "name" in usuario else usuario["email"]
        else:
            print("Usuario o contraseña incorrectos.")
            return None

    except Exception as e:
        print(f"Error al verificar usuario: {e}")
        return None
    
    #Función para registrar un usuario nuevo
    #probada

def registrar_usuario(nombre, correo, contraseña):
    try:
        db = conexion()
        users = db["Users"]

        # Verifica si el correo ya existe
        if users.find_one({"email": correo}):
            print("Error: El usuario ya existe.")
            return False

        # Inserta un nuevo usuario
        nuevo_usuario = {
            "name": nombre,
            "email": correo,
            "password": contraseña
        }
        users.insert_one(nuevo_usuario)
        print("Usuario registrado exitosamente.")
        return True

    except Exception as e:
        print(f"Error inesperado: {e}")
        return False
    
    #Función para cambiar contraseña 

def cambiar_contraseña(correo, nueva):
    try:
        db = conexion()
        users = db["Users"]

        # Actualiza el documento con el email indicado
        resultado = users.update_one(
            {"email": correo}, 
            {"$set": {"password": nueva}}
        )

        if resultado.modified_count > 0:
            print(f"Contraseña actualizada para {correo}")
            return True
        else:
            print(f"No se encontró el usuario con correo {correo} o la contraseña ya era igual.")
            return False

    except Exception as e:
        print(f"Error al cambiar contraseña: {e}")
        return False

#Función para obtener email
def obtener_nombre_por_email(email):
    try:
        db = conexion()
        usuarios = db["Users"]

        usuario = usuarios.find_one({"email": email}, {"name": 1, "_id": 0})

        if usuario:
            return usuario["name"]
        else:
            print("Usuario no encontrado")
            return None

    except Exception as e:
        print(f"Error al obtener nombre: {e}")
        return None
    
def obtener_correo_por_nombre(nombre):
    try:
        db = conexion()
        usuarios = db["Users"]

        # Buscar documento por nombre
        usuario = usuarios.find_one({"name": nombre}, {"email": 1, "_id": 0})

        if usuario:
            return usuario["email"]
        else:
            print("Usuario no encontrado")
            return None

    except Exception as e:
        print(f"Error al obtener correo: {e}")
        return None
    
    #Función para eliminar un usuario

def eliminar_usuario(email):
    try:
        db = conexion()
        users = db["Users"]
        articles = db["Articles"]
        comments = db["Comments"]

        # Buscar el usuario por email
        usuario = users.find_one({"email": email})
        if not usuario:
            print(f"No se encontró el usuario con email '{email}'.")
            return False

        nombre_usuario = usuario["name"]
        print(f"Eliminando usuario: {nombre_usuario} ({email})")

        # 1️⃣ Eliminar los comentarios HECHOS por el usuario
        resultado_comments_user = comments.delete_many({"author_email": email})
        print(f"Comentarios del usuario eliminados: {resultado_comments_user.deleted_count}")

        # 2️⃣ Obtener los artículos creados por el usuario
        articulos_del_usuario = list(articles.find({"email": email}))
        ids_articulos = [articulo["_id"] for articulo in articulos_del_usuario]

        # 3️⃣ Eliminar comentarios en esos artículos (de cualquier autor)
        if ids_articulos:
            resultado_comments_articles = comments.delete_many({"_idArt": {"$in": ids_articulos}})
            print(f"Comentarios asociados a los artículos del usuario eliminados: {resultado_comments_articles.deleted_count}")

        # 4️⃣ Eliminar los artículos del usuario
        resultado_articles = articles.delete_many({"email": email})
        print(f"Artículos del usuario eliminados: {resultado_articles.deleted_count}")

        # 5️⃣ Finalmente eliminar el usuario
        resultado_user = users.delete_one({"email": email})
        if resultado_user.deleted_count > 0:
            print(f"Usuario '{nombre_usuario}' ({email}) eliminado exitosamente.")
            return True
        else:
            print(f"No se pudo eliminar el usuario con email '{email}'.")
            return False

    except Exception as e:
        print(f"Ocurrió un error al eliminar el usuario: {e}")
        return False

    #Tags de un articulo

def obtener_tags_por_articulo(article_id):
    try:
        db = conexion()
        resultado = list(db["Articles"].aggregate([
            {"$match": {"_id": article_id}},
            {
                "$lookup": {
                    "from": "Tags",
                    "localField": "tags",
                    "foreignField": "_id",
                    "as": "tagNombre"
                }
            },
            {"$project": {"_id": 0, "tagNombre.name": 1}}
        ]))
        
        if resultado:
            # Extraemos los nombres de los tags
            tags = [t["name"] for t in resultado[0]["tagNombre"]]
            return tags
        else:
            return []
    except Exception as e:
        print(f"Error al obtener tags: {e}")
        return []

    #Función para encontrar todos los articulos de una categoría

def buscar_por_categoria(nombre_categoria):
    try:
        db = conexion()
        categorias = db["Categories"]
        articulos = db["Articles"]

        # Buscar la categoría por su nombre
        categoria = categorias.find_one({"name": nombre_categoria})
        if not categoria:
            print(f"No se encontró la categoría '{nombre_categoria}'.")
            return []

        categoria_id = categoria["_id"]

        # Buscar artículos que contengan ese ID en su lista de categorías
        resultados = list(articulos.find({"categories": categoria_id}))

        # Convertir los documentos a tuplas para mantener compatibilidad con tu GUI
        articulos_tuplas = []
        for art in resultados:
            articulos_tuplas.append((
                art.get("_id", ""),
                art.get("title", ""),
                art.get("email", ""),     # autor
                art.get("text", ""),      # contenido
                art.get("date", ""),
                art.get("tags", []),
                art.get("categories", [])
            ))

        return articulos_tuplas

    except Exception as e:
        print(f"Error al obtener artículos por categoría: {e}")
        return []

def buscar_todos_los_articulos():
    try:
        db = conexion()
        articulos_col = db["Articles"]

        resultados = list(articulos_col.find({}))  # todos los documentos

        articulos_lista = []
        for art in resultados:
            articulos_lista.append((
                str(art.get("_id", "")),  # ID
                art.get("title", ""),      # Título
                art.get("email", ""),      # Autor
                art.get("text", ""),       # Contenido
                art.get("date", ""),       # Fecha
                art.get("tags", []),       # Tags
                art.get("categories", [])  # Categorías
            ))

        return articulos_lista

    except Exception as e:
        print(f"Error al obtener todos los artículos: {e}")
        return []
   
def buscar_por_tag(tag_nombre):
    try:
        db = conexion()
        tags_col = db["Tags"]
        articles_col = db["Articles"]

        tag = tags_col.find_one({"name": tag_nombre})
        if not tag:
            print(f"No se encontró el tag '{tag_nombre}'.")
            return []

        tag_id = tag["_id"]

        resultados = list(articles_col.find({"tags": tag_id}))

        articulos_lista = []
        for art in resultados:
            articulos_lista.append((
                str(art.get("_id", "")),      
                art.get("title", ""),        
                art.get("email", ""),        
                art.get("text", ""),          
                art.get("date", ""),           
                art.get("tags", []),          
                art.get("categories", [])      
            ))

        return articulos_lista

    except Exception as e:
        print(f"Error al buscar artículos por tag: {e}")
        return []
    
def obtener_comentarios(id_articulo):
    try:
        db = conexion()  # conexión a MongoDB
        comentarios = list(db["Comments"].find({"_idArt": id_articulo}))
        return comentarios
    except Exception as e:
        print(f"Error al obtener comentarios: {e}")
        return []

def comentar(id_articulo, autor, contenido, email_autor):
    try:
        db = conexion()
        comentarios = db["Comments"]

        if isinstance(id_articulo, str):
            id_articulo = ObjectId(id_articulo)

        nuevo_comentario = {
            "_idArt": id_articulo,
            "autor": autor,
            "author_email": email_autor,  
            "contenido": contenido,
            "fecha": datetime.now()
        }

        comentarios.insert_one(nuevo_comentario)
        print("Comentario agregado correctamente.")
        return True

    except Exception as e:
        print(f"Error al agregar comentario: {e}")
        return False
    
def obtener_articulos_por_email(email):
    try:
        db = conexion()
        articles = db["Articles"]

        print(f"Buscando artículos para el email: '{email}'")

        # Buscar artículos directamente por email
        articulos = list(articles.find({"email": email}))

        if not articulos:
            print(f"El usuario con email '{email}' no tiene artículos publicados.")
            return []

        # Convertir los artículos en tuplas
        articulos_lista = []
        for art in articulos:
            articulos_lista.append((
                str(art.get("_id", "")),       # ID del artículo
                art.get("title", ""),          # Título
                art.get("email", ""),          # Autor (email)
                art.get("text", ""),           # Contenido
                art.get("date", ""),           # Fecha
                art.get("tags", []),           # Tags
                art.get("categories", [])      # Categorías
            ))

        print(f"Se encontraron {len(articulos_lista)} artículos para el email '{email}'")
        return articulos_lista

    except Exception as e:
        print(f"Error al obtener artículos por email: {e}")
        return []
    
def eliminar_articulo(id_articulo):
    try:
        db = conexion()
        articulos = db["Articles"]

        from bson.objectid import ObjectId
        if isinstance(id_articulo, str):
            id_articulo = ObjectId(id_articulo)

        resultado = articulos.delete_one({"_id": id_articulo})

        if resultado.deleted_count > 0:
            print(f"Artículo '{id_articulo}' eliminado exitosamente.")
            return True
        else:
            print(f"No se encontró el artículo '{id_articulo}'.")
            return False

    except Exception as e:
        print(f"Ocurrió un error al eliminar el artículo: {e}")
        return False

def crear_articulo(email, titulo, contenido, categorias, tags):
    try:
        db = conexion()
        users = db["Users"]
        articles = db["Articles"]
        cat_collection = db["Categories"]
        tag_collection = db["Tags"]

        # Obtener el nombre del usuario para mostrarlo
        user = users.find_one({"email": email})
        if not user:
            print(f"Usuario con email '{email}' no encontrado")
            return False
        
        nombre = user["name"]

        # Convertir categorías a ObjectId
        cat_ids = []
        for cat in categorias:
            c = cat_collection.find_one({"name": cat})
            if c:
                cat_ids.append(c["_id"])
            else:
                print(f"Advertencia: Categoría '{cat}' no encontrada")

        # Convertir tags a ObjectId, crear si no existen
        tag_ids = []
        for t in tags:
            tag_doc = tag_collection.find_one({"name": t})
            if not tag_doc:
                tag_doc = tag_collection.insert_one({"name": t})
                tag_ids.append(tag_doc.inserted_id)
                print(f"Tag '{t}' creado automáticamente")
            else:
                tag_ids.append(tag_doc["_id"])

        articulo = {
            "title": titulo,
            "text": contenido,
            "email": email,
            "author_name": nombre,
            "categories": cat_ids,
            "tags": tag_ids,
            "date": datetime.now()
        }

        articles.insert_one(articulo)
        print(f"Artículo '{titulo}' creado exitosamente para '{nombre}' ({email})")
        return True

    except Exception as e:
        print(f"Error al crear artículo: {e}")
        return False

def obtener_articulo_por_id(article_id):
    try:
        db = conexion()
        articulos = db["Articles"]

        # Asegúrate de convertir article_id a ObjectId si es string
        if isinstance(article_id, str):
            article_id = ObjectId(article_id)

        articulo = articulos.find_one({"_id": article_id})

        if articulo:
            # Puedes devolverlo tal cual, o convertir _id a string para plantillas
            articulo["_id"] = str(articulo["_id"])
            return articulo
        else:
            print(f"No se encontró el artículo con id {article_id}")
            return None

    except Exception as e:
        print(f"Error al obtener artículo por id: {e}")
        return None
    
def obtener_cat_por_articulo(article_id):
    try:
        db = conexion() 
        resultado = list(db["Articles"].aggregate([
            {"$match": {"_id": article_id}},
            {
                "$lookup": {
                    "from": "Categories",
                    "localField": "categories",
                    "foreignField": "_id",
                    "as": "categorias_info"
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "categorias": "$categorias_info.name"
                }
            }
        ]))

        if resultado:
            return resultado[0].get("categorias", [])
        else:
            return []

    except Exception as e:
        print(f"Error al obtener categorías: {e}")
        return []
    
def inicializar_collections():
    try:
        db = conexion()
        colecciones_necesarias = ["Users", "Articles", "Comments", "Categories", "Tags"]

        colecciones_existentes = db.list_collection_names()
        for coleccion in colecciones_necesarias:
            if coleccion not in colecciones_existentes:
                print(f"Creando colección: {coleccion}")
                temp = db[coleccion].insert_one({"_init": True})
                db[coleccion].delete_one({"_id": temp.inserted_id})

        cat_collection = db["Categories"]
        if cat_collection.count_documents({}) == 0:
            categorias_peliculas = [
                "Acción", "Comedia", "Drama", "Terror", "Animación",
                "Ciencia Ficción", "Romance", "Documental", "Aventura", "Musical"
            ]
            for cat in categorias_peliculas:
                cat_collection.insert_one({"name": cat})
            print("Categorías de películas inicializadas.")

        print("Todas las colecciones necesarias existen o han sido creadas.")

    except Exception as e:
        print(f"Error al inicializar colecciones: {e}")
        
def obtener_todas_las_categorias():
    try:
        db = conexion()
        cat_collection = db["Categories"]

        # Buscar todas las categorías (puedes ajustar el campo)
        categorias = cat_collection.find({}, {"_id": 0, "name": 1})  # Proyecta solo el campo 'nombre'

        # Devuelve una lista con los nombres de las categorías
        return [cat["name"] for cat in categorias]

    except Exception as e:
        print(f"Error al obtener categorías: {e}")
        return []
