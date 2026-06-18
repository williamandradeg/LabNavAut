#!/bin/bash

echo "========================================================"
echo " PURGANDO PROCESOS ZOMBIE EN LA MEMORIA RAM..."
echo "========================================================"
# Matar de raíz cualquier rastro oculto antes de iniciar
killall -9 rviz2 gz-sim-server ruby gz parameter_bridge nodo_navegacion.py publicador_tf.py 2>/dev/null
pkill -9 -f gz
pkill -9 -f rviz
pkill -9 -f python
rm -rf ~/.gz/sim/*
sleep 1

# Registrar el entorno
source /opt/ros/lyrical/setup.bash
source install/setup.bash

# Variables de video seguras para UTM en Mac M3
export GDK_BACKEND=x11
export QT_QPA_PLATFORM=xcb
export LIBGL_ALWAYS_SOFTWARE=1
export GALLIUM_DRIVER=llvmpipe
export QT_DISABLE_WINDOW_CONTAINER_X11=1
export GZ_PARTITION=ue_nav_aut_sim

echo "========================================================"
echo " INICIANDO INFRAESTRUCTURA DESDE EL SEGUNDO CERO"
echo "========================================================"

# 1. Arrancar el motor físico base limpio
ros2 launch ue_nav_aut simular_todo.launch.py > /dev/null 2>&1 &
sleep 6

# 2. Arrancar el publicador de transformadas y obstáculos
ros2 run ue_nav_aut publicador_tf.py --ros-args -p use_sim_time:=true > /dev/null 2>&1 &
sleep 3

# 3. Lanzar RViz2 con el diseño de anclaje local blindado
ros2 run rviz2 rviz2 -d src/ue_nav_aut/config/mi_config.rviz --ros-args -p use_sim_time:=true > /dev/null 2>&1 &
echo "Estabilizando chasis en el origen inferior..."
sleep 8

echo "========================================================"
echo " DESPERTANDO EL CEREBRO DE NAVEGACIÓN REACTIVA AUTÓNOMA"
echo "========================================================"

# 4. Lanzar el nodo de navegación en primer plano
ros2 run ue_nav_aut nodo_navegacion.py --ros-args -p use_sim_time:=true

trap 'kill $(jobs -p)' EXIT
