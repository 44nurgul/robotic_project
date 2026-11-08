import math
import signal

import rclpy
from rclpy.node import Node
from rclpy.signals import SignalHandlerOptions
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist


class ObstacleAvoider(Node):
    """/scan'i okur, onde engel yoksa duz gider, varsa daha acik tarafa doner."""

    def __init__(self):
        super().__init__('obstacle_avoider')

        self.declare_parameter('obstacle_threshold', 1)  # bundan yakinsa donmeye basla (m)
        self.declare_parameter('clear_distance', 1.4)      # on bundan uzaksa tekrar duz git (m)
        self.declare_parameter('forward_speed', 0.25)      # m/s
        self.declare_parameter('turn_speed', 0.8)          # rad/s

        self.scan_sub = self.create_subscription(LaserScan, '/scan', self.scan_callback, 10)
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        self.state = 'FORWARD'  # FORWARD veya TURN
        self.turn_dir = 1.0     # +1 sola, -1 saga

    def sector_min(self, scan, start_deg, end_deg):
        """Verilen aci araligindaki (derece) en yakin gecerli mesafe."""
        values = []
        for i, r in enumerate(scan.ranges):
            angle = math.degrees(scan.angle_min + i * scan.angle_increment)
            if start_deg <= angle <= end_deg:
                if math.isinf(r):
                    r = scan.range_max  # inf = hicbir sey gorulmedi
                if not math.isnan(r) and r >= scan.range_min:
                    values.append(r)
        return min(values) if values else scan.range_max

    def scan_callback(self, scan):
        threshold = self.get_parameter('obstacle_threshold').value
        clear_distance = self.get_parameter('clear_distance').value
        forward_speed = self.get_parameter('forward_speed').value
        turn_speed = self.get_parameter('turn_speed').value

        # 0 derece robotun onu, pozitif aci sol taraf
        front = self.sector_min(scan, -45, 45)
        left = self.sector_min(scan, 45, 90)
        right = self.sector_min(scan, -90, -45)

        # Karar kurali (iki esik kullaniyoruz ki robot sinirda titremesin):
        #   FORWARD iken on < obstacle_threshold  -> daha acik tarafa donmeye basla
        #   TURN iken    on > clear_distance      -> tekrar duz git
        if self.state == 'FORWARD' and front < threshold:
            self.state = 'TURN'
            self.turn_dir = 1.0 if left >= right else -1.0
            side = 'LEFT' if self.turn_dir > 0 else 'RIGHT'
            self.get_logger().info(
                f'Engel! front={front:.2f} m -> TURN {side} (left={left:.2f}, right={right:.2f})')
        elif self.state == 'TURN' and front > clear_distance:
            self.state = 'FORWARD'
            self.get_logger().info(f'Yol acik: front={front:.2f} m -> FORWARD')

        cmd = Twist()
        if self.state == 'FORWARD':
            cmd.linear.x = forward_speed
        else:
            cmd.angular.z = self.turn_dir * turn_speed  # yerinde don
        self.cmd_pub.publish(cmd)

    def stop(self):
        self.cmd_pub.publish(Twist())


def main(args=None):
    # Ctrl+C'yi biz yakaliyoruz ki kapanmadan once robota "dur" gonderebilelim
    rclpy.init(args=args, signal_handler_options=SignalHandlerOptions.NO)
    node = ObstacleAvoider()
    try:
        # spin() yerine kisa zaman asimli dongu: /scan gelmese de Ctrl+C hemen calisir
        while rclpy.ok():
            rclpy.spin_once(node, timeout_sec=0.1)
    except KeyboardInterrupt:
        pass
    finally:
        signal.signal(signal.SIGINT, signal.SIG_IGN)  # ikinci Ctrl+C kapanisi bolmesin
        node.stop()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
