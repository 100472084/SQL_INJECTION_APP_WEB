import pymysql
from pymysql.constants import CLIENT
import bcrypt

def connect_mydb():
    mydb = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='tfg_db')
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
            hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            query = ("INSERT INTO usuarios (username, password, email, dni, telefono, nombre_completo, fecha_nacimiento, direccion) "
                     "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")
            mycursor.execute(query, (username, hashed_pw, email, dni, telefono, nombre, nacimiento, direccion))
            mydb.commit()
            return True

        except Exception:
            print("Error al registrar nuevo usuario")
            return False

def iniciar_sesion(params):
    mydb = connect_mydb()
    with mydb.cursor() as mycursor:
        try:
            user = params['username']
            passwd = params['password']

            query = "SELECT * FROM usuarios WHERE username = %s"
            mycursor.execute(query, (user,))
            result = mycursor.fetchone()

            if result and bcrypt.checkpw(passwd.encode('utf-8'), result[2].encode('utf-8')):
                return result
            else:
                return None

        except Exception:
            print("Error durante el inicio de sesión")
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
                if post_id not in feed_dict:
                    feed_dict[post_id] = {
                        'contenido': contenido,
                        'fecha': fecha,
                        'autor': autor,
                        'comentarios': []
                    }

                if comentario:
                    feed_dict[post_id]['comentarios'].append({
                        'autor': autor_coment,
                        'texto': comentario,
                        'fecha': fecha_com
                    })

            return feed_dict.items()

        except Exception:
            print("Error en el feed")
            return

def generar_comentario(params, usuario, post):
    mydb = connect_mydb()
    with mydb.cursor() as mycursor:
        try:
            comentario = params['comentario']
            query = "INSERT INTO comentarios (post_id, usuario_id, comentario) VALUES (%s, %s, %s)"
            mycursor.execute(query, (post, usuario, comentario))
            mydb.commit()
            return True
        except Exception:
            print("Error al generar comentario")
            return

def publicar_post(params, usuario):
    mydb = connect_mydb()
    with mydb.cursor() as mycursor:
        try:
            contenido = params['contenido']
            query = "INSERT INTO posts (usuario_id, contenido) VALUES (%s, %s)"
            mycursor.execute(query, (usuario, contenido))
            mydb.commit()
            return True
        except Exception:
            print("Error al publicar post")
            return False

def buscar_usuario(params):
    mydb = connect_mydb()
    with mydb.cursor() as mycursor:
        try:
            termino = params['termino']
            query = "SELECT username, nombre_completo, fecha_nacimiento, telefono FROM usuarios WHERE username LIKE %s"
            mycursor.execute(query, (f"%{termino}%",))
            resultados = mycursor.fetchall()
            return resultados

        except Exception:
            print("Error al buscar usuario")
            return

def mensajes_recibidos(usuario):
    mydb = connect_mydb()
    with mydb.cursor() as mycursor:
        try:
            query = ("SELECT m.mensaje, m.fecha_envio, u.username AS remitente FROM mensajes m JOIN usuarios u ON "
                     "m.remitente_id = u.id WHERE m.destinatario_id = %s ORDER BY m.fecha_envio DESC")

            mycursor.execute(query, (usuario,))
            mensajes_recibidos = mycursor.fetchall()
            return mensajes_recibidos

        except Exception:
            print("Error al acceder a mensajes")
            return False

def enviar_mensaje_directo(params, usuario):
    mydb = connect_mydb()
    with mydb.cursor() as mycursor:
        try:
            destinatario = params['destinatario']
            mensaje = params['mensaje']
            mycursor.execute("SELECT id FROM usuarios WHERE username = %s", (destinatario,))
            resultado = mycursor.fetchone()

            if resultado:
                destinatario_id = resultado[0]
                mycursor.execute("INSERT INTO mensajes (remitente_id, destinatario_id, mensaje) VALUES (%s, %s, %s)",
                                 (usuario, destinatario_id, mensaje))
                mydb.commit()
                return True
            else:
                return False

        except Exception:
            print("Error al enviar mensajes")
            return False
