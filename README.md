# Lucy

Discord bot de propósito general

![Discord.py](https://img.shields.io/badge/Discord.py-2.6.4-blue?logo=discord)
![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![Docker](https://img.shields.io/badge/Docker-Container-blue?logo=docker)

## Índice

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

Para el caso de que `PRODUCTION=True`, solo debe de configurarse como mínimo `DISCORD_BOT_TOKEN`.

Por otro lado es necesario configurar `TESTING_DISCORD_BOT_TOKEN` y `TESTING_GUILD_ID`.

Obtén tu Token en [Discord Developer Portal](https://discord.com/developers/applications)

Configura las variables de entorno creando en la raíz del proyecto un archivo nombrado `.env` y establece las claves necesarias

| Clave | Valor por defecto | Descripción |
| - | - | - |
| `PRODUCTION` | `False` | Establece si el modo es de producción |
| `DISCORD_BOT_TOKEN` | `None` | Token del bot  de producción |
| `TESTING_DISCORD_BOT_TOKEN` | `None` | Token del bot de pruebas |
| `TESTING_GUILD_ID` | `None` | Id de servidor de pruebas a sincronizar |
| `RELEASES_URL` | `None` | Link de releases _formato https://api.github.com/repos/{user}/{repo}/releases/latest_ |

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
