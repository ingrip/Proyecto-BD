from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from bson.objectid import ObjectId
from Connect import (
    verificar_usuario,
    registrar_usuario,
    obtener_todas_las_categorias,
    buscar_por_categoria,
    buscar_todos_los_articulos,
    buscar_por_tag,
    obtener_articulo_por_id,
    obtener_tags_por_articulo,
    obtener_cat_por_articulo,
    obtener_comentarios,
    comentar,
    obtener_articulos_por_email,
    eliminar_articulo,
    cambiar_contraseña,
    eliminar_usuario,
    crear_articulo,
    inicializar_collections
)

app = Flask(__name__)
app.secret_key = "supersecreto"

iconos_categorias = {
    "Acción": "fa-bolt",
    "Comedia": "fa-laugh",
    "Drama": "fa-theater-masks",
    "Terror": "fa-ghost",
    "Ciencia Ficción": "fa-rocket",  
    "Romance": "fa-heart",
    "Animación": "fa-film",
    "Documental": "fa-book-open",
    "Aventura": "fa-hat-wizard",
    "Musical": "fa-music"
}

# --- LOGIN Y REGISTRO ---

@app.route("/")
def home():
    if "usuario" not in session:
        return redirect(url_for("login"))

    articulos_destacados = buscar_todos_los_articulos()[:6]
    cats = obtener_todas_las_categorias()

    return render_template(
        "home.html",
        usuario=session["usuario"],
        correo=session["correo"],
        articulos_destacados=articulos_destacados,
        categorias=cats,
        iconos=iconos_categorias
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        nombre = verificar_usuario(email, password)

        if nombre:
            session["usuario"] = nombre  # nombre visible
            session["correo"] = email    # identificador real
            return redirect(url_for("categorias"))
        else:
            return render_template("login.html", error="Credenciales incorrectas")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nombre = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        exito = registrar_usuario(nombre, email, password)
        if exito:
            return redirect(url_for("login"))
        else:
            return render_template("register.html", error="El correo ya está registrado")
    return render_template("register.html")


@app.route("/logout")
def logout():
    session.pop("usuario", None)
    session.pop("correo", None)
    return redirect(url_for("login"))


# --- CATEGORÍAS Y ARTÍCULOS ---

@app.route("/categorias")
def categorias():
    if "usuario" not in session:
        return redirect(url_for("login"))
    cats = obtener_todas_las_categorias()
    return render_template("categorias.html", categorias=cats,
        iconos=iconos_categorias, usuario=session["usuario"])


@app.route("/articulos/", defaults={"categoria": None})
@app.route("/articulos/<categoria>")
def articulos(categoria):
    if "usuario" not in session:
        return redirect(url_for("login"))

    if categoria and categoria.lower() != "todas":
        arts = buscar_por_categoria(categoria)
        categoria_mostrar = categoria
    else:
        arts = buscar_todos_los_articulos()
        categoria_mostrar = "Todas"

    return render_template(
        "articulos.html",
        categoria=categoria_mostrar,
        articulos=arts,
        usuario=session["usuario"]
    )


@app.route("/articulo/<id>", methods=["GET", "POST"])
def articulo(id):
    if "usuario" not in session:
        return redirect(url_for("login"))

    art = obtener_articulo_por_id(ObjectId(id))
    tags = obtener_tags_por_articulo(ObjectId(id))
    categorias = obtener_cat_por_articulo(ObjectId(id))
    comentarios = obtener_comentarios(ObjectId(id))

    if request.method == "POST":
        texto = request.form["comentario"]
        if texto.strip():
            email_autor = session.get("correo")
            if email_autor:
                comentar(ObjectId(id), session["usuario"], texto, email_autor)
            else:
                flash("Error: No se pudo obtener el email del usuario", "error")
        return redirect(url_for("articulo", id=id))

    return render_template(
        "articulo.html",
        articulo=art,
        tags=tags,
        categorias=categorias,
        comentarios=comentarios,
        usuario=session["usuario"],
    )


# --- PERFIL Y GESTIÓN DE USUARIO ---

@app.route("/perfil", methods=["GET", "POST"])
def perfil():
    if "usuario" not in session:
        return redirect(url_for("login"))

    email_usuario = session["correo"]

    if request.method == "POST":
        if "nueva" in request.form:
            nueva = request.form["nueva"]
            if nueva:
                exito = cambiar_contraseña(email_usuario, nueva)
                if exito:
                    flash("Contraseña actualizada correctamente.", "success")
                else:
                    flash("No se pudo actualizar la contraseña.", "danger")

        elif "eliminar" in request.form:
            exito = eliminar_usuario(email_usuario)
            if exito:
                session.clear()
                return redirect(url_for("login"))
            else:
                flash("No se pudo eliminar el usuario.", "danger")

        elif "titulo" in request.form:
            titulo = request.form["titulo"]
            contenido = request.form["contenido"]
            categorias = request.form.getlist("categorias")
            tags = [t.strip() for t in request.form["tags"].split(",") if t.strip()]
            exito = crear_articulo(email_usuario, titulo, contenido, categorias, tags)
            if exito:
                flash("Artículo creado correctamente.", "success")
            else:
                flash("No se pudo crear el artículo.", "danger")
        
        return redirect(url_for("perfil"))

    articulos = obtener_articulos_por_email(email_usuario)
    categorias_disponibles = obtener_todas_las_categorias()
    
    return render_template(
        "perfil.html",
        usuario=session["usuario"],
        articulos=articulos,
        categorias=categorias_disponibles
    )


@app.route("/eliminar_articulo/<id>")
def eliminar_articulo_route(id):
    if "usuario" not in session:
        return redirect(url_for("login"))
    eliminar_articulo(ObjectId(id))
    return redirect(url_for("perfil"))


@app.route("/tags/<tag>")
def articulos_por_tag(tag):
    if "usuario" not in session:
        return redirect(url_for("login"))
    arts = buscar_por_tag(tag)
    return render_template("articulos.html", categoria=f"Tag: {tag}", articulos=arts, usuario=session["usuario"])


if __name__ == "__main__":
    inicializar_collections()
    app.run(debug=True)
