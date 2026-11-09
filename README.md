# FloodSafe-IoT
Sistema IoT de monitoreo y alertas de nivel de agua

Descripción del problema

FloodSafe es un proyecto que desarrollamos para ayudar a prevenir desbordamientos y desperdicios de agua en cisternas o depósitos. Muchas personas no tienen una manera fácil de conocer el nivel del agua, por lo que decidimos crear un sistema que permita monitorearlo y recibir alertas.

Nuestra solución

Utilizamos una Raspberry Pi 4 y un sensor ultrasónico JSN-SR04T para medir el nivel del agua. El programa procesa las mediciones y utiliza tres luces LED para identificar el estado del depósito:

Verde: Nivel normal.

Amarillo: Nivel de advertencia.

Rojo: Nivel crítico.

También incorporamos un buzzer para las alertas de sonido y una página web creada con Flask para visualizar las mediciones, la velocidad de subida del agua y el tiempo estimado para alcanzar el nivel crítico.

Componentes utilizados

Raspberry Pi 4

Sensor ultrasónico JSN-SR04T

Tres luces LED (verde, amarillo y rojo)

Buzzer

Resistencias

Breadboard

Cables jumper

Tarjeta microSD

Fuente de alimentación

Recipiente para las pruebas

Costo estimado

Componente

Raspberry Pi 4 $67.50

Sensor JSN-SR04T $12.00

Buzzer $3.00

Tres LED $1.50

Resistencias $2.00

Breadboard $6.00

Cables jumper $4.00

Tarjeta microSD $10.00

Fuente de alimentación $10.00

Recipiente $2.00

Total estimado $118.00

Los costos son aproximados e incluyen componentes que ya teníamos disponibles.

Instrucciones para poner en funcionamiento el prototipo

Instalar Raspberry Pi OS en la Raspberry Pi 4.

Conectar el sensor ultrasónico, las luces LED y el buzzer utilizando una breadboard.

Realizar las conexiones GPIO:

LED verde: GPIO 17

LED amarillo: GPIO 27

LED rojo: GPIO 22

Buzzer: GPIO 18

TRIG del sensor: GPIO 23

ECHO del sensor: GPIO 24, utilizando un divisor de voltaje para proteger la Raspberry Pi.

Instalar las bibliotecas necesarias desde la terminal:

sudo apt install python3-gpiozero python3-flask

Descargar el archivo Flood_Safe.py del repositorio.

Revisar y ajustar las medidas del recipiente en el código.

Ejecutar el programa desde la terminal:

python3 Flood_Safe_Neverita.py

Abrir la dirección web indicada por Flask desde un navegador conectado a la misma red.

Funcionamiento

El sensor mide la distancia hasta la superficie del agua y envía la información a la Raspberry Pi. El programa calcula el nivel y determina cuál alerta corresponde. Además, muestra la información en una página web para facilitar el monitoreo.

Durante nuestras pruebas realizamos varios ajustes en las medidas del recipiente y la posición del sensor para mejorar las lecturas.

FloodSafe todavía es un prototipo educativo y necesita más pruebas antes de instalarse permanentemente en una cisterna real.

Documentación

En este repositorio también incluimos el código del proyecto, el diagrama del sistema, las evidencias de las pruebas, las referencias utilizadas y la presentación grupal.
