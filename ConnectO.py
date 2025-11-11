import oracledb
import sqlite3

usuario = "BE"
clave = "BE"
host = "localhost"
puerto = 1521
servicio = "xepdb1"
dsn = f"{host}:{puerto}/{servicio}"


def conexion():
    return oracledb.connect(user=usuario, password=clave, dsn=dsn)

#Función que hace conexión con la base de datos y ejecuta la función para verificar un inicio de sesión
def verificar_usuario(correo, contraseña):
    try:
        conn = conexion()  
        with conn.cursor() as cur:
            nombre_usuario = cur.callfunc("get_user_name", oracledb.DB_TYPE_VARCHAR, [correo, contraseña])
        return nombre_usuario 
    except oracledb.Error as e:
        int(f"Error al verificar usuario: {e}")
        return None

#Función para registrar un usuario nuevo
def registrar_usuario(nombre, correo, contraseña):
    try:
        conn = conexion()  
        with conn.cursor() as cur:
            cur.callproc("add_user", [nombre, correo, contraseña])
        print("Usuario registrado exitosamente.")
        conn.commit()
        return True
    except oracledb.Error as e:
        error_obj = e.args[0]
        if hasattr(error_obj, 'code') and error_obj.code == 20101:
            print("Error: El usuario ya existe.")
        else:
            print(f"Error inesperado: {e}")
        return False

#Función para cambiar contraseña
def cambiar_contraseña(correo, nueva_contraseña):
    try:
        db = conexion()
        result = db.Users.update_one(
            {"email": correo},
            {"$set": {"password": nueva_contraseña}}
        )
        if result.modified_count == 0:
            print("Usuario no encontrado o contraseña no actualizada.")
            return False

        print("Contraseña actualizada exitosamente.")
        return True
    except Exception as e:
        print(f"Error al cambiar contraseña: {e}")
        return False

#Función para obtener email
def obtener_correo_por_nombre(nombre):
    try:
        conn = conexion() 
        with conn.cursor() as cur:
            correo = cur.callfunc("get_user_email", oracledb.DB_TYPE_VARCHAR, [nombre])
        return correo  
    except oracledb.Error as e:
        print(f"Error al obtener correo: {e}")
        return None

#Función para eliminar un usuario
def eliminar_usuario(nombre):
    try:
        db = conexion()
        result = db.Users.delete_one({"name": nombre})
        if result.deleted_count == 0:
            print("Error: Usuario no encontrado.")
            return False
        print("Usuario eliminado exitosamente.")
        return True
    except Exception as e:
        print(f"Error al eliminar usuario: {e}")
        return False

    
#Mostrar todas las categorías existentes
def obtener_todas_las_categorias():
    try:
        conn = conexion()  # Tu función personalizada de conexión
        with conn.cursor() as cur:
            cursor_resultado = cur.callfunc("get_all_categories", oracledb.DB_TYPE_CURSOR, [])
            categorias = cursor_resultado.fetchall() 
        return [cat[0] for cat in categorias]  
    except oracledb.Error as e:
        print(f"Error al obtener categorías: {e}")
        return []

#Tags de un articulo
def obtener_tags_por_articulo(article_id):
    try:
        conn = conexion()
        with conn.cursor() as cur:
            cursor_resultado = cur.callfunc("get_tags_by_article", oracledb.DB_TYPE_CURSOR, [article_id])
            tags = cursor_resultado.fetchall() 
        return [t[0] for t in tags] 
    except oracledb.Error as e:
        print(f"Error al obtener tags: {e}")
        return []

#Función para encontrar todos los articulos de una categoría
def buscar_por_categoria(categoria):
    try:
        conn = conexion()
        with conn.cursor() as cur:
            cur.callfunc("get_articles_by_category", oracledb.DB_TYPE_CURSOR, [categoria])
            ref_cursor = cur.callfunc(
                "get_articles_by_category",
                oracledb.DB_TYPE_CURSOR,
                [categoria]
            )  
        return ref_cursor
    except oracledb.Error as e:
        print(f"Error al obtener artículos: {e}")
        return []


def buscar_por_tag(tag):
    try:
        conn = conexion()  
        with conn.cursor() as cur:
            cursor_resultado = cur.callfunc("get_articles_by_tag", oracledb.DB_TYPE_CURSOR, [tag])
            articulos = cursor_resultado.fetchall() 
        return articulos
    except oracledb.Error as e:
        print(f"Error al obtener artículos por tag: {e}")
        return []


def obtener_comentarios(id_articulo):
    try:
        conn = conexion()
        with conn.cursor() as cur:
            cursor_resultado = cur.callfunc("get_comments_by_article", oracledb.DB_TYPE_CURSOR, [id_articulo])
            comentarios = cursor_resultado.fetchall()  
        return comentarios
    except oracledb.Error as e:
        print(f"Error al obtener comentarios: {e}")
        return []


def comentar(id_articulo, autor, contenido):
    try:
        conn = conexion()  # Tu función personalizada de conexión
        with conn.cursor() as cur:
            mensaje = cur.callfunc("add_comment", oracledb.DB_TYPE_VARCHAR, [id_articulo, autor, contenido])
        print(mensaje)
        conn.commit()
        return mensaje
    except oracledb.Error as e:
        print(f"Error al agregar comentario: {e}")
        return None

def obtener_articulos_por_autor(nombre):
    try:
        conn = conexion()
        with conn.cursor() as cur:
            cursor_resultado = cur.callfunc("get_articles_by_author", oracledb.DB_TYPE_CURSOR, [nombre])
            articulos = cursor_resultado.fetchall() 
        return articulos
    except oracledb.Error as e:
        print(f"Error al obtener artículos del autor: {e}")
        return []


def eliminar_articulo(id_articulo):
    try:
        conn = conexion()  # Tu función personalizada de conexión
        with conn.cursor() as cur:
            cur.callproc("delete_article", [id_articulo])
        print("Artículo eliminado exitosamente.")
        conn.commit()
        return True
    except oracledb.Error as e:
        error_obj = e.args[0]
        if hasattr(error_obj, 'code') and error_obj.code == 20203:
            print("Error: Artículo no encontrado.")
        else:
            print(f"Error inesperado: {e}")
        return False


def crear_articulo(nombre, titulo, contenido, categorias, tags):
    try:
        conn = conexion()
        with conn.cursor() as cur:
            article_id = cur.callfunc("add_article", oracledb.DB_TYPE_NUMBER, [titulo, nombre, contenido])
            
            if not article_id:
                print("Error al crear el artículo.")
                return None

            print(f"Artículo creado con ID: {article_id}")

            for cat in categorias:
                mensaje_cat = cur.callfunc("add_article_category", oracledb.DB_TYPE_VARCHAR, [article_id, cat])
                print(f"Categoría '{cat}': {mensaje_cat}")

            for tag in tags:
                mensaje_insert_tag = cur.callfunc("insert_tag_if_not_exists", oracledb.DB_TYPE_VARCHAR, [tag])
                print(f"Insertar tag '{tag}': {mensaje_insert_tag}")

                mensaje_tag = cur.callfunc("add_article_tag", oracledb.DB_TYPE_VARCHAR, [article_id, tag])
                print(f"Tag '{tag}': {mensaje_tag}")

            conn.commit()

            return article_id

    except oracledb.Error as e:
        print(f"Error al crear artículo completo: {e}")
        return None

def obtener_articulo_por_id(article_id):
    try:
        conn = conexion()
        with conn.cursor() as cur:
            cursor_resultado = cur.callfunc("get_article_by_id", oracledb.DB_TYPE_CURSOR, [article_id])
            resultado = cursor_resultado.fetchone() 
        return list(resultado) if resultado else []
    except oracledb.Error as e:
        print(f"Error al obtener artículo: {e}")
        return []

#Categorias de un articulo
def obtener_cat_por_articulo(article_id):
    try:
        conn = conexion()
        with conn.cursor() as cur:
            cursor_resultado = cur.callfunc("get_cat_by_article", oracledb.DB_TYPE_CURSOR, [article_id])
            tags = cursor_resultado.fetchall() 
            cursor_resultado.close()
        return [t[0] for t in tags] 
    except oracledb.Error as e:
        print(f"Error al obtener categorias: {e}")
        return []
