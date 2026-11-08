
from collections import deque
from statistics import median
from threading import Lock, Thread
from time import monotonic, sleep

from flask import Flask, jsonify, render_template_string
from gpiozero import LED, Buzzer, DistanceSensor

# ===================
# FLOODSAFE 
# ===================

# CONFIGURACION DE PINES GPIO
PIN_VERDE = 17
PIN_AMARILLO = 27
PIN_ROJO = 22
PIN_BUZZER = 18
PIN_TRIG = 23
PIN_ECHO = 24

# CONFIGURACION DE LA NEVERITA
DISTANCIA_FONDO_CM = 34.7

# Distancia minima 
DISTANCIA_MINIMA_CM = 25.0

# Rango util de demostracion
ALTURA_UTIL_CM = 9.7

# ALERTAS POR ALTURA DEL AGUA
NIVEL_ADVERTENCIA_CM = 7.0
NIVEL_CRITICO_CM = 9.0

# Velocidad de referencia 
VELOCIDAD_ALERTA_CM_MIN = 1.0

app = Flask(__name__)
lock = Lock()

# COMPONENTES
led_verde = LED(PIN_VERDE)
led_amarillo = LED(PIN_AMARILLO)
led_rojo = LED(PIN_ROJO)
buzzer = Buzzer(PIN_BUZZER)

sensor = DistanceSensor(
    echo=PIN_ECHO,
    trigger=PIN_TRIG,
    max_distance=2.0,
    queue_len=5
)

estado = {
    "nivel": None,
    "porcentaje": None,
    "velocidad": None,
    "tiempo": None,
    "alerta": "INICIANDO"
}

historial = deque()


def activar_alerta(alerta):
    led_verde.off()
    led_amarillo.off()
    led_rojo.off()
    buzzer.off()

    if alerta == "VERDE":
        led_verde.on()

    elif alerta == "AMARILLO":
        led_amarillo.on()

    elif alerta == "ROJO":
        led_rojo.on()
        buzzer.on()

    elif alerta == "ERROR":
        led_rojo.blink(
            on_time=0.2,
            off_time=0.8,
            background=True
        )


def medir_distancia():
    lecturas = []

    for i in range(5):
        distancia = sensor.distance * 100

        if distancia <= 0 or distancia >= 200:
            raise ValueError("Lectura fuera de rango")

        lecturas.append(distancia)
        sleep(0.12)

    distancia = median(lecturas)

    # Evitar lecturas fuera de la calibracion
    if distancia > DISTANCIA_FONDO_CM + 3:
        raise ValueError(
            "Revisar calibracion del sensor"
        )

    # Evitar la zona cercana no confiable
    if distancia < DISTANCIA_MINIMA_CM:
        raise ValueError(
            "Agua demasiado cerca del sensor"
        )

    return distancia


def monitorear():
    while True:
        try:
            distancia = medir_distancia()

            # Calcular altura del agua
            nivel = DISTANCIA_FONDO_CM - distancia
            nivel = max(
                0,
                min(ALTURA_UTIL_CM, nivel)
            )

            # Calcular porcentaje
            porcentaje = (
                nivel / ALTURA_UTIL_CM
            ) * 100

            # Historial para velocidad de subida
            ahora = monotonic()
            historial.append((ahora, nivel))

            while (
                historial
                and ahora - historial[0][0] > 60
            ):
                historial.popleft()

            velocidad = 0

            if len(historial) >= 2:
                tiempo_inicial, nivel_inicial = historial[0]
                segundos = ahora - tiempo_inicial

                if segundos >= 10:
                    velocidad = (
                        (nivel - nivel_inicial)
                        * 60 / segundos
                    )

            # Tiempo estimado hasta nivel critico
            tiempo_estimado = None

            if (
                velocidad > 0.05
                and nivel < NIVEL_CRITICO_CM
            ):
                tiempo_estimado = (
                    (NIVEL_CRITICO_CM - nivel)
                    / velocidad
                )

            # ==================================
            # ALERTAS SOLO POR NIVEL DE AGUA
            # ==================================
            if nivel >= NIVEL_CRITICO_CM:
                alerta = "ROJO"

            elif nivel >= NIVEL_ADVERTENCIA_CM:
                alerta = "AMARILLO"

            else:
                alerta = "VERDE"

            activar_alerta(alerta)

            with lock:
                estado.update({
                    "nivel": round(nivel, 1),
                    "porcentaje": round(porcentaje, 1),
                    "velocidad": round(velocidad, 2),
                    "tiempo": (
                        round(tiempo_estimado, 1)
                        if tiempo_estimado is not None
                        else None
                    ),
                    "alerta": alerta
                })

            print(
                f"Nivel: {nivel:.1f} cm | "
                f"Llenado: {porcentaje:.1f}% | "
                f"Velocidad: {velocidad:.2f} cm/min | "
                f"Alerta: {alerta}",
                flush=True
            )

        except Exception as error:
            historial.clear()
            activar_alerta("ERROR")

            with lock:
                estado.update({
                    "nivel": None,
                    "porcentaje": None,
                    "velocidad": None,
                    "tiempo": None,
                    "alerta": "ERROR"
                })

            print("Error:", error, flush=True)

        sleep(2)


# =====================================
# PAGINA WEB FLOODSAFE
# =====================================

PAGINA = """
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport"
content="width=device-width, initial-scale=1">

<title>FloodSafe - Monitoreo de Cisternas</title>

<style>
body {
    background: #0f172a;
    color: white;
    font-family: Arial, sans-serif;
    text-align: center;
    padding: 25px;
}

.panel {
    background: #1e293b;
    max-width: 500px;
    margin: auto;
    padding: 25px;
    border-radius: 18px;
}

.valor {
    font-size: 30px;
    font-weight: bold;
    margin: 12px;
}

.barra {
    background: #475569;
    height: 20px;
    border-radius: 10px;
    overflow: hidden;
}

#llenado {
    width: 0%;
    height: 100%;
    background: green;
}

#alerta {
    padding: 18px;
    margin-top: 20px;
    border-radius: 12px;
    font-size: 25px;
    font-weight: bold;
}
</style>
</head>

<body>
<div class="panel">

<h1>FloodSafe</h1>
<h3>Monitoreo Inteligente de Cisternas</h3>

<p>Nivel del agua</p>
<div class="valor" id="nivel">--</div>

<p>Capacidad utilizada</p>
<div class="valor" id="porcentaje">--</div>

<div class="barra">
<div id="llenado"></div>
</div>

<p>Velocidad de aumento</p>
<div class="valor" id="velocidad">--</div>

<p>Tiempo estimado hasta nivel critico</p>
<div class="valor" id="tiempo">--</div>

<div id="alerta">INICIANDO</div>

</div>

<script>
async function actualizar() {
    try {
        const respuesta = await fetch("/datos");

        if (!respuesta.ok) {
            throw new Error("Sin respuesta");
        }

        const d = await respuesta.json();

        document.getElementById("nivel").textContent =
            d.nivel === null
            ? "--"
            : d.nivel + " cm";

        document.getElementById("porcentaje").textContent =
            d.porcentaje === null
            ? "--"
            : d.porcentaje + "%";

        document.getElementById("velocidad").textContent =
            d.velocidad === null
            ? "--"
            : d.velocidad + " cm/min";

        document.getElementById("tiempo").textContent =
            d.tiempo === null
            ? "No disponible"
            : d.tiempo + " minutos";

        const colores = {
            VERDE: "#15803d",
            AMARILLO: "#ca8a04",
            ROJO: "#dc2626",
            ERROR: "#64748b",
            INICIANDO: "#64748b"
        };

        const color = colores[d.alerta] || "#64748b";

        const alerta = document.getElementById("alerta");
        alerta.textContent = "ALERTA " + d.alerta;
        alerta.style.background = color;

        const barra = document.getElementById("llenado");

        barra.style.width =
            (d.porcentaje === null
                ? 0
                : d.porcentaje) + "%";

        barra.style.background = color;

    } catch (error) {
        document.getElementById("alerta").textContent =
            "SIN CONEXION";
    }
}

setInterval(actualizar, 2000);
actualizar();
</script>

</body>
</html>
"""


@app.route("/")
def inicio():
    return render_template_string(PAGINA)


@app.route("/datos")
def datos():
    with lock:
        return jsonify(estado.copy())


if __name__ == "__main__":
    try:
        Thread(
            target=monitorear,
            daemon=True
        ).start()

        print("FloodSafe iniciado")
        print("Abre http://127.0.0.1:5000")

        app.run(
            host="0.0.0.0",
            port=5000,
            debug=False,
            use_reloader=False
        )

    finally:
        buzzer.off()
        led_verde.off()
        led_amarillo.off()
        led_rojo.off()

        sensor.close()
        buzzer.close()
        led_verde.close()
        led_amarillo.close()
        led_rojo.close()
