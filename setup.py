from setuptools import setup, find_packages  
  
setup(  
    name="bic2200",  
    version="2.3.0",  
    author="Ernie Lin",  
    author_email="ernielin@htbi.com.tw",  
    description="bic2200 drivers",   
    packages=find_packages() ,
    install_requires=[
        'python-can',
        'canalystii',
    ]
)