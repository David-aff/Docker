
import os
import psycopg2
import html
from flask import Flask, request, redirect

app = Flask(__name__)


def conectar_db():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "db"),
        database=os.getenv("POSTGRES_DB", "stock"),
        user=os.getenv("POSTGRES_USER", "salazar"),
        password=os.getenv("POSTGRES_PASSWORD"),
        port=os.getenv("DB_PORT", "5432"),
        connect_timeout=5
    )


@app.route("/", methods=["GET", "POST"])
def inicio():

    estado = "PostgreSQL conectado correctamente"
    color = "#28a745"
    mensaje_estado = ""

    try:
        conexion = conectar_db()
        cursor = conexion.cursor()

        if request.method == "POST":

            nombre = request.form.get("nombre", "").strip()
            correo = request.form.get("correo", "").strip()
            mensaje = request.form.get("mensaje", "").strip()

            if nombre and correo and mensaje:
                cursor.execute(
                    """
                    INSERT INTO mensajes (nombre, correo, mensaje)
                    VALUES (%s, %s, %s)
                    """,
                    (nombre, correo, mensaje)
                )

                conexion.commit()
                mensaje_estado = "¡Mensaje guardado correctamente!"

            else:
                mensaje_estado = "Completa todos los campos."

        cursor.execute("""
            SELECT id, nombre, correo, mensaje, fecha
            FROM mensajes
            ORDER BY fecha DESC
        """)

        mensajes = cursor.fetchall()

        cursor.close()
        conexion.close()

    except Exception as error:
        estado = "Error de conexion con PostgreSQL"
        color = "#dc3545"
        mensaje_estado = str(error)
        mensajes = []

    lista_mensajes = ""

    for id, nombre, correo, mensaje, fecha in mensajes:
        lista_mensajes += f"""
        <div class="mensaje">
            <strong>{html.escape(nombre)}</strong>
            ({html.escape(correo)})
            - {fecha.strftime('%d/%m/%Y %H:%M')}

            <p>{html.escape(mensaje)}</p>
        </div>
        """

    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">

        <title>David Ricardo Salazar Bastidas</title>

        <style>
            body {{
                font-family: 'Segoe UI', sans-serif;
                background-color: #f4f6f9;
                padding: 30px;
                color: #333;
            }}

            .card {{
                background: white;
                max-width: 850px;
                margin: 30px auto;
                padding: 35px;
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            }}

            h1 {{
                color: #0db7ed;
                text-align: center;
            }}

            h2 {{
                color: #333;
            }}

            label {{
                display: block;
                margin-top: 18px;
                margin-bottom: 6px;
            }}

            input, textarea {{
                width: 100%;
                padding: 12px;
                border: 1px solid #ccc;
                border-radius: 6px;
                box-sizing: border-box;
                font-size: 15px;
            }}

            textarea {{
                height: 100px;
                resize: vertical;
            }}

            button {{
                margin-top: 20px;
                padding: 12px 25px;
                background: #0db7ed;
                color: white;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-size: 16px;
            }}

            button:hover {{
                background: #0796c5;
            }}

            .database {{
                background: {color};
                color: white;
                padding: 12px;
                border-radius: 8px;
                text-align: center;
                margin-bottom: 20px;
            }}

            .aviso {{
                text-align: center;
                color: #16803b;
                font-weight: bold;
            }}

            .mensaje {{
                background: #f4f6f9;
                padding: 15px;
                margin-top: 12px;
                border-radius: 8px;
                overflow-wrap: anywhere;
            }}

            .mensaje p {{
                margin-bottom: 0;
            }}
        </style>
    </head>

    <body>

        <div class="card">

            <h1>David Ricardo Salazar Bastidas</h1>

            <h2>Yo estudio en Yavirac</h2>

            <div class="database">{estado}</div>

            <form method="POST">

                <label>Nombre</label>
                <input type="text" name="nombre"
                       placeholder="Escribe tu nombre" required>

                <label>Correo</label>
                <input type="email" name="correo"
                       placeholder="ejemplo@gmail.com" required>

                <label>Mensaje</label>
                <textarea name="mensaje"
                          placeholder="Escribe tu mensaje"
                          required></textarea>

                <button type="submit">Enviar</button>

            </form>

            <p class="aviso">{html.escape(mensaje_estado)}</p>

            <h2>Mensajes guardados ({len(mensajes)})</h2>

            {lista_mensajes if lista_mensajes else
            '<p>Todavía no hay mensajes guardados.</p>'}

        </div>

    </body>
    </html>
    """


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

