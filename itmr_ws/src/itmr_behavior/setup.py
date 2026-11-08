from setuptools import setup

package_name = 'itmr_behavior'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Zeynep Sude',
    maintainer_email='zeynepsudeakyuz@gmail.com',
    description='LiDAR tabanli engelden kacinma davranisi (/scan -> /cmd_vel)',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'obstacle_avoider = itmr_behavior.obstacle_avoider:main',
            'color_detector = itmr_behavior.color_detector:main',
        ],
    },
)
