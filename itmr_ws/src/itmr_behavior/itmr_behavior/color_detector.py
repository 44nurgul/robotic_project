import cv2
import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String

# HSV araliklari (OpenCV: H 0-179, S 0-255, V 0-255)
# Kirmizi, HSV'de H=0 etrafinda sarildigi icin iki aralik gerekir.
COLOR_RANGES = {
    'RED': [((0, 120, 70), (10, 255, 255)), ((170, 120, 70), (179, 255, 255))],
    'GREEN': [((40, 80, 50), (85, 255, 255))],
    'BLUE': [((100, 120, 50), (130, 255, 255))],
}


class ColorDetector(Node):
    """/camera/image_raw'dan kirmizi, yesil, mavi nesneleri bulur.

    Her saniye gorulen renkler icin mesaj verir ve /detected_color'a yayinlar.
    """

    def __init__(self):
        super().__init__('color_detector')

        # Bir rengin "nesne" sayilmasi icin gereken en az piksel sayisi
        self.declare_parameter('min_area', 500)
        self.declare_parameter('report_period', 1.0)  # saniye

        self.image_sub = self.create_subscription(Image, '/camera/image_raw', self.image_callback, 1)
        self.color_pub = self.create_publisher(String, '/detected_color', 10)
        self.timer = self.create_timer(self.get_parameter('report_period').value, self.report)

        self.seen = set()  # son raporlamadan beri gorulen renkler
        self.counts = {}   # renk -> o rengin kac kez raporlandigi

    def image_callback(self, msg):
        if msg.encoding != 'rgb8':
            self.get_logger().warn(f'Unexpected format: {msg.encoding} (expected rgb8)',
                                   throttle_duration_sec=5.0)
            return

        img = np.frombuffer(msg.data, dtype=np.uint8).reshape(msg.height, msg.width, 3)
        # Hiz icin kucult: renk tespiti icin 1280x720 gereksiz
        img = cv2.resize(img, (msg.width // 4, msg.height // 4), interpolation=cv2.INTER_AREA)
        hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)

        # Esik, kucultme oranina gore (1/16 alan) olceklenir
        min_area = self.get_parameter('min_area').value / 16.0

        for name, ranges in COLOR_RANGES.items():
            mask = None
            for low, high in ranges:
                m = cv2.inRange(hsv, np.array(low), np.array(high))
                mask = m if mask is None else cv2.bitwise_or(mask, m)
            if cv2.countNonZero(mask) >= min_area:
                self.seen.add(name)

    def report(self):
        for name in sorted(self.seen):
            self.counts[name] = self.counts.get(name, 0) + 1
            text = f'{name} object detected ({self.counts[name]})'
            self.get_logger().info(text)
            self.color_pub.publish(String(data=text))
        self.seen.clear()


def main(args=None):
    rclpy.init(args=args)
    node = ColorDetector()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
