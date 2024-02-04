from setuptools import setup, find_packages

setup(
    name='VerbalDiary Assistant',  # Replace with your package's name
    version='0.1.0',  # Package version
    packages=find_packages(where='src'),  # This tells setuptools to find packages under src directory
    package_dir={'': 'src'},
    author='Joshua Wendland',  # Replace with your name
    author_email='',  # Replace with your email
    description='Your Diary bot.',  # Short description
    long_description=open('README.md').read(),  # Long description from README.md
    long_description_content_type='text/markdown',  # Specifies the content type of the long description
    url='https://github.com/joshuawe/telegram-journal-bot',  # Replace with the URL to your package's repo
    install_requires=[
        # List your project's dependencies here
        # e.g., 'requests>=2.20.0',
    ],
    classifiers=[
        # Choose classifiers from https://pypi.org/classifiers/
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.9',  # Minimum version requirement of the package
)
