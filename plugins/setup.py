""
Setup for dockevOS Plugins
"""

from setuptools import setup, find_packages

setup(
    name="dockevos-plugins",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'docker>=6.0.0',
        'psutil>=5.9.0',
        'requests>=2.26.0',
        'python-dotenv>=0.19.0',
    ],
    extras_require={
        'voice': [
            'pyaudio>=0.2.11',
            'vosk>=0.3.32',
        ],
        'dev': [
            'pytest>=6.2.5',
            'pytest-cov>=2.12.1',
            'mypy>=0.910',
            'flake8>=3.9.2',
            'black>=21.7b0',
        ],
    },
    author="DockevOS Team",
    author_email="support@dockevos.io",
    description="Plugin system for dockevOS",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/wronai/dockevos",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
    python_requires='>=3.8',
)
