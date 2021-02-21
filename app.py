from os import environ
from dotenv import load_dotenv, find_dotenv
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from models import db, Chat

load_dotenv(find_dotenv())
app = Flask(__name__)

# Configuracion
app.config['SECRET_KEY'] = environ.get('SECRET_KEY')
app.config['DEBUG'] = True if environ.get('DEBUG') == 'True' else False
app.config['PORT'] = 80

# Socketio
DOMAIN = environ.get('DOMAIN')
socketio = SocketIO(app)

# Base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DATABASE')
db.init_app(app)

# Cargamos la plantilla HTML con el frontend
@app.route('/<username>/')
def open_chat(username):
    my_chat = Chat.query.all()
    return render_template(
        'chat.html',
        domain=DOMAIN,
        chat=my_chat,
        username=username
    )

# Recibirá los nuevos mensajes y los emitirá por socket
@socketio.on('new_message')
def new_message(message):
    # Emitimos el mensaje con el alias y el mensaje del usuario
    emit('new_message', {
        'username': message['username'],
        'text': message['text']
    }, broadcast=True)
    # Salvamos el mensaje en la base de datos
    my_new_chat = Chat(
        username=message['username'],
        text=message['text']
    )
    db.session.add(my_new_chat)
    db.session.commit()


# Iniciamos
if __name__ == '__main__':
    socketio.run(app)