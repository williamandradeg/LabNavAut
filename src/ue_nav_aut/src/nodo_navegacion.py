#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import math
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan

class NodoNavegacionAutonoma(Node):
    def __init__(self):
        super().__init__('nodo_navegacion')
        self.sub_odom = self.create_subscription(Odometry, '/odom', self.callback_odom, 10)
        self.sub_scan = self.create_subscription(LaserScan, '/scan', self.callback_scan, 10)
        self.pub_cmd_vel = self.create_publisher(Twist, '/cmd_vel', 10)

        self.x = 0.0
        self.y = -3.5
        self.yaw = 0.0
        self.target_x = 0.0
        self.target_y = 3.5  # Meta estricta de oro

        self.obstaculo_detectado = False
        self.desvio_sugerido = 0.0  
        self.timer = self.create_timer(0.1, self.bucle_control)
        self.get_logger().info('Cerebro de Navegación con Filtro de Saturación Activo.')

    def callback_odom(self, msg):
        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y
        q = msg.pose.pose.orientation
        siny_cosp = 2 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1 - 2 * (q.y * q.y + q.z * q.z)
        self.yaw = math.atan2(siny_cosp, cosy_cosp)

    def callback_scan(self, msg):
        """ Filtra las muestras frontales del LIDAR controlando el desbordamiento """
        self.obstaculo_detectado = False
        self.desvio_sugerido = 0.0
        
        for i in range(len(msg.ranges)):
            angulo = msg.angle_min + i * msg.angle_increment
            # Acotamos el cono de visión frontal estricto para ignorar el cubo naranja lateral al inicio
            if -0.45 < angulo < 0.45:  # ~ -25 a +25 grados frontales puros
                distancia = msg.ranges[i]
                if msg.range_min < distancia < 1.2:
                    self.obstaculo_detectado = True
                    # FILTRO: Evitamos divisiones por cero agregando un offset de distancia mayor
                    fuerza_evasion = 0.5 / (distancia + 0.1)
                    if angulo > 0:
                        self.desvio_sugerido -= fuerza_evasion
                    else:
                        self.desvio_sugerido += fuerza_evasion

    def bucle_control(self):
        msg_vel = Twist()
        distancia_objetivo = math.sqrt((self.target_x - self.x)**2 + (self.target_y - self.y)**2)
        angulo_objetivo = math.atan2(self.target_y - self.y, self.target_x - self.x)
        error_angular = angulo_objetivo - self.yaw
        error_angular = math.atan2(math.sin(error_angular), math.cos(error_angular))

        if distancia_objetivo < 0.25:
            msg_vel.linear.x = 0.0
            msg_vel.angular.z = 0.0
            self.pub_cmd_vel.publish(msg_vel)
            self.get_logger().info('¡Meta alcanzada con éxito!')
            self.timer.cancel()
            return

        if self.obstaculo_detectado:
            msg_vel.linear.x = 0.05  # Velocidad de seguridad ultra estable
            # FILTRO DE SATURACIÓN EXPLÍCITO: Limita el giro máximo a 0.5 rad/s para eliminar saltos gráficos
            msg_vel.angular.z = max(min(self.desvio_sugerido, 0.5), -0.5)
        else:
            msg_vel.linear.x = 0.20  # Avance progresivo fluido
            msg_vel.angular.z = 1.5 * error_angular

        self.pub_cmd_vel.publish(msg_vel)

def main(args=None):
    rclpy.init(args=args)
    node = NodoNavegacionAutonoma()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
