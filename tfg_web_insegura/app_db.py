import pymysql
from pymysql.constants import CLIENT

def connect_mydb():
    mydb = pymysql.connect(
        host= 'localhost',
        user= 'root',
        password='',
        database='tfg_db',
        client_flag=pymysql.constants.CLIENT.MULTI_STATEMENTS)
    return mydb

def registrar_usuario(params):

    mydb = connect_mydb()

    with mydb.cursor() as mycursor:
        username = params['username']
        password = params['password']
        email = params['email']
        dni = params['dni']
        telefono = params['telefono']
        nombre = params['nombre']
        nacimiento = params['nacimiento']
        direccion = params['direccion']

        try:
            query = (f"INSERT INTO usuarios (username, password, email, dni, telefono, nombre_completo, fecha_nacimiento, direccion)"
                     f" VALUES ('{username}', '{password}', '{email}', '{dni}', '{telefono}', '{nombre}', '{nacimiento}', '{direccion}')")

            mycursor.execute(query)
            mydb.commit()
            return True

        except Exception as e:
            print(e)
            return False

def iniciar_sesion(params):
    mydb = connect_mydb()
    with mydb.cursor() as mycursor:
        try:
            user = params['username']
            passwd = params['password']

            query = f"SELECT * FROM usuarios WHERE username = '{user}' AND password = '{passwd}'"
            print("QUERY:", query)

            mycursor.execute(query)
            while mycursor.nextset():  # Procesa las múltiples sentencias
                pass

            mydb.commit()

            result = mycursor.fetchone()
            return result
        except Exception as e:
            print(e)
            return

def generar_feed():
    mydb = connect_mydb()
    with mydb.cursor() as mycursor:
        try:
            query = ("SELECT p.id AS post_id, p.contenido, p.fecha_publicacion, u.username AS autor_post, "
                     "cu.username AS autor_comentario, c.comentario, c.fecha_comentario FROM posts p JOIN "
                     "usuarios u ON p.usuario_id = u.id LEFT JOIN comentarios c ON p.id = c.post_id LEFT JOIN usuarios cu "
                     "ON c.usuario_id = cu.id ORDER BY p.fecha_publicacion DESC")

            mycursor.execute(query)
            result = mycursor.fetchall()

            feed_dict = {}

            for post_id, contenido, fecha, autor, autor_coment, comentario, fecha_com in result:
                # Si es la primera vez que vemos este post_id
                if post_id not in feed_dict:
                    feed_dict[post_id] = {
                        'contenido': contenido,
                        'fecha': fecha,
                        'autor': autor,
                        'comentarios': []
                    }

                # Añadimos el comentario si hay
                if comentario:
                    feed_dict[post_id]['comentarios'].append({
                        'autor': autor_coment,
                        'texto': comentario,
                        'fecha': fecha_com
                    })

            return feed_dict.items()

        except Exception as e:
            print(e)
            return

def generar_comentario(params, usuario, post):
    mydb = connect_mydb()
    with mydb.cursor() as mycursor:
        try:
            comentario = params['comentario']
            query = f"INSERT INTO comentarios (post_id, usuario_id, comentario) VALUES ({post}, {usuario}, '{comentario}')"
            mycursor.execute(query)
            mydb.commit()
            return True
        except Exception as e:
            print(e)
            return

def publicar_post(params, usuario):
    mydb = connect_mydb()
    with mydb.cursor() as mycursor:
        try:
            contenido = params['contenido']
            query = f"INSERT INTO posts (usuario_id, contenido) VALUES ({usuario}, '{contenido}')"
            mycursor.execute(query)
            mydb.commit()
            return True
        except Exception as e:
            print(e)
            return False

def buscar_usuario(params):
    mydb = connect_mydb()
    with mydb.cursor() as mycursor:
        try:
            termino = params['termino']
            query = f"SELECT username, nombre_completo, fecha_nacimiento, telefono FROM usuarios WHERE username LIKE '%{termino}%'"
            print("QUERY:", query)
            mycursor.execute(query)
            resultados = mycursor.fetchall()
            return resultados

        except Exception as e:
            print(e)
            return

def mensajes_recibidos(usuario):
    mydb = connect_mydb()
    with mydb.cursor() as mycursor:
        try:
            query = (f"SELECT m.mensaje, m.fecha_envio, u.username AS remitente FROM mensajes m JOIN usuarios u ON "
                     f"m.remitente_id = u.id WHERE m.destinatario_id = {usuario} ORDER BY m.fecha_envio DESC")

            mycursor.execute(query)
            mensajes_recibidos = mycursor.fetchall()
            return mensajes_recibidos

        except Exception as e:
            print(e)
            return False

def enviar_mensaje_directo(params, usuario):
    mydb = connect_mydb()
    with mydb.cursor() as mycursor:
        try:
            destinatario = params['destinatario']
            mensaje = params['mensaje']
            mycursor.execute(f"SELECT id FROM usuarios WHERE username = '{destinatario}'")
            resultado = mycursor.fetchone()

            if resultado:
                destinatario_id = resultado[0]
                mycursor.execute(f"INSERT INTO mensajes (remitente_id, destinatario_id, mensaje) VALUES ({usuario}, {destinatario_id}, '{mensaje}')")
                mydb.commit()
                return True
            else:
                return False

        except Exception as e:
            print(e)
            return False
