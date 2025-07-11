from setuptools import setup, find_packages
import pathlib

# Read the contents of README.md
here = pathlib.Path(__file__).parent
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="dockevos",
    version="0.1.0",
    description="A container-based OS with voice control and plugin system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wronai/dockevo",
    author="WRONA AI Team",
    author_email="contact@wron.ai",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Operating System",
        "License :: OSI Approved :: Apache-2.0 License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="container, voice-control, docker, plugin-system, tts, stt",
    packages=find_packages(include=['dockevos', 'dockevos.*']),
    include_package_data=True,
    python_requires=">=3.8, <4",
    install_requires=[
        "docker>=6.0.0",
        "python-dotenv>=0.19.0",
        "psutil>=5.9.0",
    ],
    extras_require={
        "stt": [
            "vosk>=0.3.32; platform_system != 'Windows'",
            "openai-whisper>=20230314; python_version >= '3.8' and platform_system != 'Windows'",
            "pocketsphinx>=0.1.15; platform_system != 'Windows'",
        ],
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.8.0",
            "black>=21.5b2",
            "flake8>=3.9.0",
        ],
    },
    entry_points={
        'console_scripts': [
            'dockevos=dockevos.__main__:main',
        ],
    },
    package_data={
        'dockevos': ['*.py'],
    },
    project_urls={
        "Bug Reports": "https://github.com/wronai/dockevo/issues",
        "Source": "https://github.com/wronai/dockevo",
    },
)
