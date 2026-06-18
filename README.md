# Proyecto de Navegación Autónoma Reactiva en ROS 2 
**Universidad Europea**  
**Práctica de Laboratorio**  
**William Andrade González**  
**Proyecto: ue_nav_aut**  

Este repositorio contiene el paquete **`ue_nav_aut`**, un sistema de navegación autónoma reactiva desarrollado bajo el ecosistema **ROS 2 Lyrical**. El proyecto integra un robot móvil de tracción diferencial equipado con un sensor LIDAR bidimensional de 360° dentro de un entorno cerrado que cuenta con exactamente 5 obstáculos geométricos fijos (cilindros y prismas cúbicos).

El objetivo principal es desplazar al agente desde una pose inicial controlada en el extremo sur del mapa `(0.0, -3.5)` hasta un punto meta en el extremo norte `(0.0, 3.5)`, garantizando en todo momento la consistencia temporal, una cadena de transformadas espaciales (TF) libre de interrupciones y un lazo cerrado donde la percepción alimenta directamente al control cinemático.

---

## 🛠️ Especificaciones de Arquitectura y Compatibilidad (Apple Silicon M3)

El proyecto está optimizado para ejecutarse en entornos virtualizados de alta restricción gráfica, específicamente en **Ubuntu 26.04 para arquitectura ARM64 sobre Apple Silicon (Mac M3 con UTM)**. 

Para superar los bloqueos de renderizado de OpenGL/Vulkan y los cuellos de botella de la red virtual de UTM, se implementaron tres estrategias de diseño de software:
1. **Desacoplamiento de Simulación:** El motor de física y colisiones de Gazebo se ejecuta en segundo plano en modo **Headless** (servidor matemático puro mediante el flag `-s`), eliminando el consumo gráfico invisible [ue_nav_aut].
2. **Localización Local Autónoma:** Se diseñó un nodo puente de transformadas nativo en Python (`publicador_tf.py`) que suscribe la odometría de simulación de Gazebo e inyecta localmente la transformación fija `odom -> base_footprint`, pintando todo el árbol TF en **verde brillante (OK)** de manera estable y eliminando los saltos estroboscópicos.
3. **Renderizado por Software Seguro:** Se fuerza a RViz2 a utilizar el backend de ventanas X11 clásico (`xcb`) e interpolación por software puro de CPU (`llvmpipe`), garantizando un movimiento 100% fluido y lineal a 60 FPS.

---

## 📂 Organización de Archivos del Espacio de Trabajo

El espacio de trabajo (`ue_nav_workspace`) mantiene la estructura estándar de ROS 2 y distribuye los recursos del paquete de la siguiente manera:

```text
ue_nav_workspace/
├── ejecutar_proyecto.sh          # Script maestro de purga, compilación y arranque automático
└── src/
    └── ue_nav_aut/               # Paquete principal del proyecto de navegación
        ├── CMakeLists.txt        # Configuración de compilación e instalación de binarios
        ├── package.xml           # Declaración de dependencias lógicas del paquete
        ├── config/
        │   └── mi_config.rviz    # Diseño visual de RViz2 (LIDAR configurado en esferas de 15cm)
        ├── launch/
        │   └── simular_todo.launch.py # Orquestador base de nodos de estado y puente de red
        ├── src/
        │   ├── nodo_navegacion.py     # Cerebro de control proporcional y evasión reactiva por LIDAR
        │   └── publicador_tf.py       # Nodo de consistencia espacial y marcadores del mapa
        ├── urdf/
        │   └── mi_robot.urdf     # Modelo físico, uniones y plugins del robot móvil diferencial
        └── worlds/
            └── lab_obstacles.world # Escenario SDF cerrado con las coordenadas de los 5 obstáculos
```

---

## 🚦 Flujo de Percepción y Control

El cerebro del robot (`nodo_navegacion.py`) opera bajo una frecuencia temporal coherente de **10 Hz** y ejecuta una máquina de estados híbrida alimentada por los tópicos de la simulación:
* **Entrada de Percepción:** Se suscribe al tópico `/scan` (`sensor_msgs/msg/LaserScan`) y filtra un cono visual frontal estricto de 25° para anticipar colisiones frontales.
* **Procesamiento Reactivo:** Si detecta un obstáculo a menos de 1.2 metros, activa un comportamiento repulsivo: reduce la velocidad lineal a `0.05 m/s` (frenado dinámico) y aplica una velocidad angular acotada a un máximo de `0.5 rad/s` para evitar derrapes cinemáticos, forzando un esquive amplio y holgado.
* **Salida de Control:** El algoritmo prioriza la persecución de la meta (*Go-to-Goal*) a `0.20 m/s` mediante un control proporcional angular, frenando en seco al cruzar de forma matemática el paralelo norte.

---

## 🚀 Instrucciones de Ejecución Rápida

Para desplegar y evaluar el proyecto completo de forma autónoma, el entorno cuenta con un script automatizado que limpia los procesos zombie acumulados en la memoria RAM, limpia la caché de simulación, compila el espacio de trabajo de forma limpia y arranca secuencialmente los diferentes procesos.

Para la ejecución se debe abrir una terminal en Ubuntu, desplazarse a la carpeta del proyecto y ejecutar el Script maestro:
```bash
cd ~/ue_nav_workspace
./ejecutar_proyecto.sh
```

### 🎯 Qué sucederá en su pantalla:
1. La terminal purgará cualquier hilo invisible de ejecuciones pasadas y vaciará el búfer temporal de colisiones de Gazebo.
2. Se abrirá de forma automática la interfaz gráfica de **RViz2 con todos sus paneles laterales y barras de herramientas completamente visibles**.
3. Observará al robot azul tridimensional perfectamente modelado en **color Verde (Estado: OK)**, estacionado de forma segura abajo en el sur en `(0.0, -3.5)`. Los 5 obstáculos de colores sólidos estarán distribuidos a los lados del mapa estático.
4. Tras un breve temporizador de 8 segundos diseñado para estabilizar la red y permitir la inspección inicial, la terminal despertará el nodo de control autónomo de forma automática.
5. Se Verá al robot avanzar de forma fluida, lineal y continua hacia la meta, proyectando nítidamente una estela de esferas rojas gigantes de 15 cm de su LIDAR, esquivando reactivamente los obstáculos del camino y deteniéndose al cruzar la meta objetivo.
