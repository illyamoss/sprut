from setuptools import setup


setup(
   name='Sprut',
   version='0.0.1',
   description='Securely and simply transfer files \
                from one computer to another 📦',
   author='Illya Mosiychuk',
   author_email='illya08mosiychuk@gmail.com',
   packages=['Sprut'],
   install_requires=['cryptography==36.0.1', 'requests==2.27.1'],
)
