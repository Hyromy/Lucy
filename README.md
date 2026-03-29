# Lucy

Discord bot de propósito general

![Discord.py](https://img.shields.io/badge/Discord.py-2.6.4-blue?logo=discord)
![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![Docker](https://img.shields.io/badge/Docker-Container-blue?logo=docker)

## Índice
- [Lucy](#lucy)
  - [Índice](#índice)
  - [Estructura del proyecto](#estructura-del-proyecto)
  - [Variables de entorno](#variables-de-entorno)
  - [Despliegue](#despliegue)
    - [Local](#local)
    - [Docker](#docker)

## Estructura del proyecto

Se posee una estructura modular

```sh
components/         # componentes UI
modules/            # cogs
utils/              # utilidades
├── Lucy.py         # clase Bot
└── *               # otras utilidades

main.py             # Punto de entrada del Bot
requirements.txt    # Dependencias
```

## Variables de entorno

Para configurar las variables de entorno, copia el archivo `.env.example` como `.env` en la raíz del proyecto y completa los valores necesarios según tu entorno.

En el archivo `.env.example` encontrarás la plantilla y la descripción de todas las variables disponibles.

Puedes obtener el token de tu bot de Discord en el [Discord Developer Portal](https://discord.com/developers/applications).

## Despliegue

### Local

1. Entorno virtual
   
   Crea un entorno virtual, como ejemplo se usa el módulo `venv`.
   ```sh
   py -m venv env
   ```

   Activa el entorno virtual.
   ```sh
   .\env\Scripts\activate     # Windows
   ```

2. Dependencias
   
   Instala las [dependencias](requirements.txt).
   ```sh
   pip install -r requirements.txt
   ```

3. Iniciar el bot
   ```sh
   python main.py
   ```

### Docker

Puedes construir una imagen y contenedor con el [Dockerfile](Dockerfile).
```sh
docker build -t app_image .

# Linux/macOS:
docker run --name app_container -d \
    -e PRODUCTION=True \
    -e DISCORD_BOT_TOKEN=your_token_here \
    app_image

# Windows PowerShell:
docker run --name app_container -d `
    -e PRODUCTION=True `
    -e DISCORD_BOT_TOKEN=your_token_here `
    app_image
```
