# {{ cookiecutter.repository }}

## Descripción general

Este proyecto es un **template de aplicación serverless Python** diseñado para ser utilizado por un CLI que automatiza la generación de archivos para aplicaciones backend modernas. El template proporciona una arquitectura completa y escalable para desarrollar APIs RESTful usando AWS Lambda, API Gateway y bases de datos relacionales.

### Características principales:

- **Arquitectura Serverless**: Basada en AWS Lambda con API Gateway
- **Framework de Capas**: Sistema modular con capas reutilizables para lógica de negocio
- **ORM Avanzado**: SQLAlchemy con modelos base y servicios genéricos
- **Infraestructura como Código**: Despliegue automatizado con Pulumi
- **Desarrollo Local**: Servidor FastAPI para desarrollo y testing
- **Validación y Manejo de Errores**: Sistema robusto de validación de requests
- **Paginación y Filtros**: Funcionalidades avanzadas de consulta de datos
- **Soft Delete**: Manejo de eliminación lógica de registros
- **Exportación CSV**: Funcionalidad de exportación de datos
- **Múltiples Bases de Datos**: Soporte para MySQL y PostgreSQL
- **Logging Estructurado**: Integración con AWS Lambda Powertools

### Tecnologías utilizadas:

- **Python 3.11+**
- **AWS Lambda & API Gateway**
- **SQLAlchemy 2.0** (ORM)
- **Pulumi** (Infraestructura)
- **FastAPI** (Desarrollo local)
- **AWS Lambda Powertools** (Logging y utilidades)
- **Poetry** (Gestión de dependencias)

## Estructura de carpetas

```
{{cookiecutter.directory_name}}/
├── 📁 infra/                          # Infraestructura como código (Pulumi)
│   ├── __main__.py                    # Punto de entrada principal de Pulumi
│   ├── config.py                      # Configuración global del proyecto
│   ├── parameters.py                  # Parámetros de configuración
│   ├── pre_build.py                   # Scripts de pre-construcción
│   ├── 📁 commons/                    # Componentes comunes de infraestructura
│   │   ├── __init__.py
│   │   └── tags.py                    # Definición de tags AWS
│   ├── 📁 components/                 # Componentes de infraestructura
│   │   ├── __init__.py
│   │   ├── apigateway.py              # Configuración de API Gateway
│   │   ├── lambda_functions.py        # Stack de funciones Lambda
│   │   ├── lambda_layers.py           # Configuración de capas Lambda
│   │   ├── lambda_role.py             # Roles IAM para Lambda
│   │   └── 📁 lambdas/                # Configuración específica de Lambdas
│   │       └── __init__.py
│   └── 📁 utils/                      # Utilidades de infraestructura
│       ├── __init__.py
│       ├── build_api.py               # Construcción de API
│       ├── build_lambdas.py           # Construcción de Lambdas
│       ├── build_layer.py             # Construcción de capas
│       └── 📁 aws/                     # Utilidades específicas de AWS
│           ├── __init__.py
│           ├── secrets.py             # Manejo de AWS Secrets Manager
│           └── ssm.py                  # Manejo de AWS Systems Manager
│
├── 📁 src/                            # Código fuente de la aplicación
│   ├── 📁 functions/                  # Funciones individuales
│   │   └── 📁 hello_world/            # Ejemplo de función
│   │       ├── endpoint.yaml          # Definición del endpoint OpenAPI
│   │       ├── infra_config.py        # Configuración de infraestructura específica
│   │       ├── function.py            # Código principal de la función
│   │       └── test_function.py       # Tests unitarios
│   │
│   └── 📁 libs/                       # Capas compartidas de la aplicación
│       └── 📁 core/                   # Capa principal del sistema
│           ├── __init__.py
│           └── 📁 python/             # Código Python de la capa
│               ├── __init__.py
│               ├── requirements.txt   # Dependencias de la capa
│               │
│               ├── 📁 core_aws/       # Utilidades específicas de AWS
│               │   ├── __init__.py
│               │   ├── secret_manager.py # Manejo de secretos
│               │   ├── sqs.py         # Utilidades para SQS
│               │   └── ssm.py         # Utilidades para SSM
│               │
│               ├── 📁 core_db/        # Capa de acceso a datos
│               │   ├── __init__.py
│               │   ├── BaseModel.py   # Modelo base con SQLAlchemy
│               │   ├── BaseService.py # Servicio base para operaciones CRUD
│               │   ├── config.py     # Configuración de conexiones DB
│               │   ├── DBConnection.py # Gestión de conexiones
│               │   ├── 📁 models/     # Modelos de datos específicos
│               │   │   ├── __init__.py
│               │   │   └── myModel.py # Ejemplo de modelo
│               │   └── 📁 services/   # Servicios de negocio
│               │       ├── __init__.py
│               │       └── myModel_service.py # Ejemplo de servicio
│               │
│               ├── 📁 core_http/      # Capa de manejo HTTP/REST
│               │   ├── __init__.py
│               │   ├── BaseController.py # Controlador base con CRUD genérico
│               │   ├── utils.py       # Utilidades HTTP
│               │   ├── 📁 enums/      # Enumeraciones del sistema
│               │   │   ├── __init__.py
│               │   │   ├── http_status_code.py # Códigos de estado HTTP
│               │   │   └── request_parts.py # Partes de la request
│               │   ├── 📁 exceptions/ # Manejo de excepciones
│               │   │   ├── __init__.py
│               │   │   └── api_exception.py # Excepción base de API
│               │   ├── 📁 interfaces/ # Interfaces y contratos
│               │   │   ├── __init__.py
│               │   │   ├── pagination_result.py # Resultado paginado
│               │   │   └── resource_reference.py # Referencias de recursos
│               │   └── 📁 validators/ # Sistema de validación
│               │       ├── __init__.py
│               │       ├── decorators.py # Decoradores de validación
│               │       └── request_validator.py # Validador de requests
│               │
│               └── 📁 core_utils/    # Utilidades generales
│                   ├── __init__.py
│                   ├── constants.py   # Constantes del sistema
│                   ├── environment.py # Manejo de variables de entorno
│                   ├── str.py        # Utilidades de strings
│                   └── 📁 email/     # Sistema de emails
│                       ├── __init__.py
│                       ├── config.py # Configuración de email
│                       ├── example_template.html # Template de ejemplo
│                       └── templates.py # Templates de email
│
├── 📄 api.yaml                        # Especificación OpenAPI/Swagger
├── 📄 pyproject.toml                  # Configuración de Poetry y dependencias
├── 📄 Pulumi.yaml                     # Configuración de Pulumi
├── 📄 Pulumi.dev.yaml                 # Configuración específica de entorno dev
├── 📄 LICENSE                         # Licencia del proyecto
└── 📄 README.md                       # Documentación del proyecto
```

### Descripción detallada de componentes:

#### 🏗️ **Infraestructura (`infra/`)**
- **Pulumi**: Infraestructura como código para AWS
- **Componentes modulares**: API Gateway, Lambda functions, layers, roles IAM
- **Configuración flexible**: Soporte para múltiples entornos (dev, qa, prod)
- **Utilidades AWS**: Integración con Secrets Manager, SSM, SQS

#### 🚀 **Funciones (`src/functions/`)**
- **Estructura modular**: Cada función en su propio directorio
- **Configuración por función**: `endpoint.yaml` define la API específica
- **Tests incluidos**: Tests unitarios para cada función
- **Configuración de infraestructura**: Parámetros específicos por función

#### 🧩 **Capas Compartidas (`src/libs/core/python/`)**
- **core_db**: ORM con SQLAlchemy, modelos base, servicios genéricos
- **core_http**: Controladores REST, validación, manejo de errores
- **core_aws**: Utilidades específicas de AWS (Secrets, SSM, SQS)
- **core_utils**: Utilidades generales, emails, constantes

#### 🔧 **Características Avanzadas**
- **CRUD Genérico**: Controlador base que maneja automáticamente operaciones CRUD
- **Paginación**: Sistema de paginación automático con metadatos
- **Filtros y Búsqueda**: Filtros avanzados con soporte para relaciones
- **Soft Delete**: Eliminación lógica de registros
- **Exportación CSV**: Funcionalidad de exportación de datos
- **Validación**: Sistema robusto de validación de requests
- **Múltiples DBs**: Soporte para MySQL y PostgreSQL simultáneamente

## Requisitos previos
- Python 3.11
- Poetry
- Acceso a las bases de datos (credenciales vía variables de entorno/Secrets)

Opcional para despliegue de infraestructura:
- Pulumi CLI configurado y credenciales AWS válidas

## Variables de entorno
Crear un archivo `.env` en la raíz del proyecto con al menos:
- `ENVIRONMENT` (por ejemplo: `dev`, `qa`, `prod`). Se usa como prefijo de rutas locales.
- Credenciales/DSN para MySQL y PostgreSQL según la configuración de `src/layers/core/python/core_db/config.py` o variables consumidas por `DBConnection`.

Ejemplo mínimo:
```
ENVIRONMENT=dev
MYSQL_HOST=...
MYSQL_USER=...
MYSQL_PASSWORD=...
MYSQL_DB=...
POSTGRES_HOST=...
POSTGRES_USER=...
POSTGRES_PASSWORD=...
POSTGRES_DB=...
```

## Instalación de dependencias
Usando Poetry:
```
poetry install
```
Si trabajas con un virtualenv externo, actívalo primero o usa:
```
poetry shell
```

## Preparar entorno local (layers)
Para que los imports de `layers` funcionen localmente, instalar las layers como paquete local:
```
python dev_tools/install_local_layers.py
```
Este script empaqueta el contenido de `src/layers/core/python/*` y lo instala en el entorno actual.

## Generar rutas locales (FastAPI)
Construir las rutas locales a partir de la definición OpenAPI y las lambdas:
```
python dev_tools/build_local_api.py
```
Esto genera `src/api_local/router.py` con rutas FastAPI que despachan a las funciones Lambda locales, simulando el evento de API Gateway.

## Levantar servidor local
Iniciar el servidor de desarrollo FastAPI con autoreload:
```
python dev_tools/up_local_server.py
```
- El servidor usa `ENVIRONMENT` como prefijo, por ejemplo: `/dev` si `ENVIRONMENT=dev`.
- OpenAPI local disponible en: `/openapi.json`.
- Salud básica en `/`.

Alternativamente, puedes ejecutar directamente con FastAPI CLI si ya tienes el `router` generado:
```
python -m fastapi dev dev_tools/main_server.py
```

## Pruebas
Los módulos de prueba para cada función están en `src/functions/*/test_function.py`. Ejecuta con pytest:
```
pytest
```

## Despliegue de infraestructura (opcional)
Pulumi se encuentra configurado en `infra/`. Para preparar y desplegar (requiere credenciales AWS):
```
cd infra
pulumi preview
pulumi up
```
Ajusta configuración y parámetros en `infra/config.py`, `infra/parameters.py` y utilidades bajo `infra/utils`.

## Notas
- La especificación `api.yaml` se usa para construir la API local y puede ser consumida por herramientas de documentación.
- Si agregas nuevas Lambdas, recuerda actualizar su `endpoint.yaml` y ejecutar nuevamente `build_local_api.py`.
- Asegúrate de contar con acceso a MySQL/PostgreSQL desde tu entorno local (VPN/SGs/Tunnels según aplique).