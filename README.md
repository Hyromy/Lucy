# Lucy

Discord bot de propósito general

![Discord.py](https://img.shields.io/badge/Discord.py-2.6.4-blue?logo=discord)
![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![Docker](https://img.shields.io/badge/Docker-Container-blue?logo=docker)

## Índice
- [Lucy](#lucy)
  - [Índice](#índice)
  - [Variables de entorno](#variables-de-entorno)
  - [Instalación](#instalación)
    - [pip](#pip)
    - [poetry](#poetry)

## Variables de entorno

Para configurar las variables de entorno, copia el archivo `.env.example` como `.env` en la raíz del proyecto y configura los valores según lo necesites.

Es necesario que dispongas de un token de bot de discord para ejecutar el proyecto. Puedes obtener tu token en [Discord Developer Portal](https://discord.com/developers/applications).

## Instalación

### pip

1. Crea un entorno virtual:
   ```sh
   python -m venv env
   ```

2. Activa el entorno virtual:
   ```sh
   env\Scripts\activate    # Windows
   ```
   
   ```sh
   source env/bin/activate    # Linux / macOS
   ```

3. Instala las dependencias:
   ```sh
   pip install -r requirements.txt
   ```

### poetry

1. Instala las dependencias:
   ```sh
   poetry install
   ```

2. Activa el entorno virtual:
   ```sh
   poetry shell
   ```

Posterior a la instalación ejecuta el proyecto:
```sh
python main.py
```
