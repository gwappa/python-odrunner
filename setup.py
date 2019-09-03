import setuptools
from odrunner import VERSION_STR

setuptools.setup(
    name='odrunner',
    version=VERSION_STR,
    description='A python-based tool for helping data logging in an open-data style',
    url='https://github.com/gwappa/python-odrunner',
    author='Keisuke Sehara',
    author_email='keisuke.sehara@gmail.com',
    license='MIT',
    install_requires=['qtpy'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        ],
    packages=setuptools.find_packages(),
    include_package_data=True,
    entry_points={
        # 'console_scripts': [
        #     '%module% =%module%.__main__:run'
        # ]
    }
)
