from flask import Flask, request, render_template, redirect, url_for, session
from app_db import registrar_usuario, iniciar_sesion, generar_feed, publicar_post, buscar_usuario, mensajes_recibidos, enviar_mensaje_directo, generar_comentario

app = Flask(__name__)
app.secret_key = 'clave_prueba'

@app.route('/')
def inicio():
    return render_template('inicio.html')


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        result = registrar_usuario(request.form)
        if result:
            return redirect(url_for('login'))

    return render_template('registro.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        result = iniciar_sesion(request.form)

        if result:
            session['usuario_id'] = result[0]
            session['username'] = result[1]
            return redirect(url_for('feed'))
        else:
            return render_template('login.html', error='Credenciales inválidas')

    return render_template('login.html')

@app.route('/feed')
def feed():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    
    posts = generar_feed()

    if posts:
        # print(posts)
        return render_template('feed.html', posts=posts, usuario=session['username'])
    else:
        return redirect(url_for('login'))

@app.route('/seleccionar_post/<int:post_id>')
def seleccionar_post(post_id):
    session['post_id'] = post_id
    return redirect(url_for('comentar_post', post_id=post_id))

@app.route('/comentario', methods=['GET', 'POST'])
def comentar_post():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        result = generar_comentario(request.form, session['usuario_id'], session['post_id'])
        if result:
            return redirect(url_for('feed'))

    return render_template('comentario.html', usuario=session['username'], post_id=session['post_id'])

@app.route('/publicar', methods=['GET', 'POST'])
def publicar():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        result = publicar_post(request.form, session['usuario_id'])
        if result:
            return redirect(url_for('feed'))

    return render_template('publicar.html', usuario=session['username'])


@app.route('/buscar', methods=['GET', 'POST'])
def buscar():
    if request.method == 'POST':
        result = buscar_usuario(request.form)
        # print(result)
        return render_template('search.html', resultados=result)
    
    return render_template('search.html')

@app.route('/mensajes')
def mensajes():
    usuario_id = session['usuario_id']
    mens = mensajes_recibidos(usuario_id)

    if mens == False:
        return render_template('mensajes.html', mensajes=[], mensaje="Error al recuperar los mensajes.")
    elif len(mens) == 0:
        return render_template('mensajes.html', mensajes=[], mensaje="No tienes mensajes.")
    else:
        return render_template('mensajes.html', mensajes=mens)

@app.route('/enviar_mensaje', methods=['GET', 'POST'])
def enviar_mensaje():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        result = enviar_mensaje_directo(request.form, session['usuario_id'])

        if result:
            return redirect(url_for('feed'))
        else:
            return render_template('enviar_mensaje.html', mensaje="Destinatario no encontrado.")

    return render_template('enviar_mensaje.html')


if __name__ == '__main__':
    app.run(debug=True)
