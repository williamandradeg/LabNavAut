#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TransformStamped
from visualization_msgs.msg import Marker, MarkerArray
import tf2_ros

class PublicadorEntornoLocal(Node):
    def __init__(self):
        super().__init__('publicador_tf_local')
        self.subscription = self.create_subscription(Odometry, '/odom', self.odom_callback, 10)
        self.tf_broadcaster = tf2_ros.TransformBroadcaster(self)
        self.marker_pub = self.create_publisher(MarkerArray, '/visual_obstacles', 10)
        self.timer = self.create_timer(0.5, self.publish_obstacles)
        self.get_logger().info('Nodo de Consistencia Espacial TF y Mapa Estático Activado.')

    def odom_callback(self, msg):
        t = TransformStamped()
        t.header.stamp = msg.header.stamp  # Sincronización temporal forzada
        t.header.frame_id = 'odom'
        t.child_frame_id = 'base_footprint'
        t.transform.translation.x = msg.pose.pose.position.x
        t.transform.translation.y = msg.pose.pose.position.y
        t.transform.translation.z = msg.pose.pose.position.z
        t.transform.rotation = msg.pose.pose.orientation
        self.tf_broadcaster.sendTransform(t)

    def publish_obstacles(self):
        ma = MarkerArray()
        
        # Coordenadas globales fijas idénticas al entorno matemático de la simulación
        obstacles_data = [
            {"id": 1, "type": Marker.CYLINDER, "x": 1.5,  "y": 2.0,  "scale": [0.8, 0.8, 1.0], "color": [1.0, 0.0, 0.0]},
            {"id": 2, "type": Marker.CUBE,     "x": -1.5, "y": 2.0,  "scale": [0.8, 0.8, 1.0], "color": [0.0, 0.0, 1.0]},
            {"id": 3, "type": Marker.CYLINDER, "x": 1.8,  "y": 0.0,  "scale": [0.6, 0.6, 1.0], "color": [0.0, 1.0, 0.0]},
            {"id": 4, "type": Marker.CUBE,     "x": -1.5, "y": -1.5, "scale": [1.2, 0.3, 1.0], "color": [1.0, 0.5, 0.0]},
            {"id": 5, "type": Marker.CUBE,     "x": 1.5,  "y": -1.5, "scale": [0.5, 0.5, 1.0], "color": [0.5, 0.0, 0.5]}
        ]
        
        for obs in obstacles_data:
            m = Marker()
            m.header.frame_id = "odom"  # Anclado estrictamente al marco estático global del mapa
            m.header.stamp = self.get_clock().now().to_msg()
            m.id = obs["id"]
            m.type = obs["type"]
            m.action = Marker.ADD
            
            m.pose.position.x = obs["x"]
            m.pose.position.y = obs["y"]
            m.pose.position.z = 0.5
            
            m.scale.x, m.scale.y, m.scale.z = obs["scale"]
            m.color.r, m.color.g, m.color.b = obs["color"]
            m.color.a = 0.8
            ma.markers.append(m)
            
        self.marker_pub.publish(ma)

def main(args=None):
    rclpy.init(args=args)
    node = PublicadorEntornoLocal()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
