from setuptools import setup, find_packages

setup(
    name='fably',
    version='1.0.0',
    python_requires='>=3.8',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'requests',
        'click',
        'python-dotenv',
        'pyyaml',
        'numpy',
        'sounddevice',
        'soundfile',
        'vosk',
        'pydub',
        'aiohttp',
        # Platform-specific dependencies for Raspberry Pi
        'apa102-pi; platform_machine=="armv7l" or platform_machine=="aarch64"',
        'gpiozero; platform_machine=="armv7l" or platform_machine=="aarch64"',
        'RPi.GPIO; platform_machine=="armv7l" or platform_machine=="aarch64"',
    ],
    extras_require={
        'dev': [
            'black',
            'pylint',
            'pytest',
        ],
        'web': [
            'gradio',
            'plotly',
            'pandas',
            'markdown',
        ],
        'all': [
            'black',
            'pylint', 
            'pytest',
            'gradio',
            'plotly',
            'pandas',
            'markdown',
        ],
    },
    entry_points={
        'console_scripts': [
            'fably=fably.cli:cli',
        ],
    },
    package_data={
        'fably': [
            'sounds/*.wav',
            'sounds/*.txt', 
            '*.txt',
            'examples/**/*',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Topic :: Education",
    ],
    description="AI storyteller for children - Turkish language optimized for 5-year-old",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Fably Contributors",
    author_email="fably@example.com",
    url="https://github.com/sarpel/fably",
)
