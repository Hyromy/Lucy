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
    - [poetry (recomendado)](#poetry-recomendado)
    - [pip](#pip)
  - [Ejecución](#ejecución)
  - [Diagnóstico y recuperación](#diagnóstico-y-recuperación)
    - [Logs](#logs)
    - [Arranque parcial](#arranque-parcial)
    - [Estado](#estado)
    - [Cache](#cache)
    - [Dependencias](#dependencias)

## Variables de entorno

Para configurar las variables de entorno, copia el archivo `.env.example` como `.env` en la raíz del proyecto y configura los valores según lo necesites.

Es necesario que dispongas de un token de bot de discord para ejecutar el proyecto. Puedes obtener tu token en [Discord Developer Portal](https://discord.com/developers/applications).

## Instalación

El proyecto funciona con [pyproject.toml](./pyproject.toml) a través de [poetry](https://python-poetry.org), en caso de que no lo tengas instalado puedes usarlo a por medio de pip

### poetry (recomendado)

1. Instala las dependencias:
   ```sh
   poetry install
   ```

2. Activa el entorno virtual:
   ```sh
   poetry shell
   ```

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

3. Instala poetry
   ```sh
   pip install poetry
   ```

4. Instala las dependencias:
   ```sh
   poetry install
   ```

## Ejecución

Posterior a la instalación ejecuta el proyecto:

```sh
python main.py
```

## Diagnóstico y recuperación

### Logs

En caso de errores o comportamientos inesperados, se genera una carpeta `logs/` indicando el motivo del problema. Estos pueden ser en arranque, configuración o ejecución. Revisar por el archivo con la etiqueta `current.log` ya que puede existir más de un archivo.

Para el caso de docker, ejecutar `docker logs <container>` para consultar los logs.

### Arranque parcial

Es posible que tras ejecutar el bot, este no logre arrancar y cancele la ejecución. Muchas veces se debe a [variables de entorno](#variables-de-entorno) no configuradas o con valores incorrectos.

### Estado

Para comprobar si el bot está disponible, ejecutar el comando `/ping` o `/help`, para verificar que este encendido y haya cargado los [cogs](./modules/) necesarios para funcionar.

### Cache

En caso de que el bot no haya cargado todos los comandos, sin comandos o que el comando `/help` no muestre las referencias correctas, reiniciar la ejecución del bot para forzar la sincronización en [Events.py](./modules/Events.py).

### Dependencias

Tras realizar `git pull` o cambios en las dependencias es posible que existan problemas, reinstalarlas con `poetry install`.
