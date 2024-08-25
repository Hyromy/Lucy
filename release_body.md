**ÍNDICE**
- [Reestructuración](#reestructuración)
    - [Cogs](#cogs)
    - [Archivos json](#archivos-json)
        - [Traducciones](#traducciones)
- [Novedades](#noveadades)
    - [Commands](#commands)
    - [Nuevos cogs](#nuevos-cogs)
        - [Config](#config)
        - [Info](#info)
        - [Mod](#mod)
- [Bugs](#bugs)

## Reestructuración
### Cogs
Se reestructuraron los cogs para dividorlos en cogs de eventos, privados y públicos

### Archivos json
Se agregó una carpeta de archivos json para organizarlos

#### Traducciones
Se agregó una carpeta de traducciones (de inglés a español)

## Noveadades
### Nuevos comandos
#### Commands
- **avatar**
Muestra la url del icono de perfil propio o de algún usuario especificado

- **ball**
Da una respuesta aleatoria a una pregunta

- **emoji**
Muestra la url de imagen de un emoji personalizado (conocido por el bot)

### Nuevos cogs
#### Config
Destinado a la configuración del bot en servidores

#### Info
Destinado a otorgar información adicinal de objetos en discord
- **help**
Otorga información adicinal sobre los cogs (categorías) y sus comandos

- **serverinfo**
Muestra información del servidor

- **userinfo**
Muestra información del usuario propio o especificado

- **userpermissions**
Muestra los permisos que tenga el usuario propio o especificado

#### Mod
Destinado a la moderación en servidores
- **purge**
Elimina una cantidad especifica de mensajes en un canal de servidor

- **kick**
Expulsa a un usuario especificado del servidor

- **ban**
Banea a un usuario especificado del servidor

## Bugs
- Se arregló un error en el comando `env` que impedía enviar las claves si es que alguna de ellas contenía `=`