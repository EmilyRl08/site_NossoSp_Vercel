
import os
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

# Caminho principal do projeto
BASE_DIR = Path(__file__).resolve().parent.parent


# Lê o arquivo .env (se existir)
try:
    from dotenv import load_dotenv

    load_dotenv(BASE_DIR / ".env")
except ImportError:
    pass


# Funções para leitura das variáveis de ambiente
def env_bool(nome, padrao=False):
    valor = os.environ.get(nome)

    if valor is None:
        return padrao

    return valor.strip().lower() in ("1", "true", "yes", "sim", "on")


def env_lista(nome):
    return [
        item.strip()
        for item in os.environ.get(nome, "").split(",")
        if item.strip()
    ]


# ==========================================
# CONFIGURAÇÕES DE SEGURANÇA
# ==========================================

SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-!3t#=t0y^m&=o&53&v#lk*%0--ic4uz*%35mn*ke!+jww3ur"
)

# Em produção, configure DEBUG=False no Vercel
DEBUG = env_bool("DEBUG", False)

# Domínios autorizados
ALLOWED_HOSTS = list(set(
    env_lista("ALLOWED_HOSTS") + [
        "site-nosso-sp-vercel.vercel.app",
        "localhost",
        "127.0.0.1",
    ]
))

# Origens autorizadas para requisições CSRF
CSRF_TRUSTED_ORIGINS = list(set(
    env_lista("CSRF_TRUSTED_ORIGINS") + [
        "https://site-nosso-sp-vercel.vercel.app",
    ]
))


# ==========================================
# APLICATIVOS INSTALADOS
# ==========================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'noticias',
]


# ==========================================
# MIDDLEWARE
# ==========================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


ROOT_URLCONF = 'config.urls'


# ==========================================
# CONFIGURAÇÃO DOS TEMPLATES
# ==========================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


WSGI_APPLICATION = 'config.wsgi.application'


# ==========================================
# BANCO DE DADOS
# ==========================================

# Com DATABASE_URL, utiliza PostgreSQL (Supabase).
# Sem DATABASE_URL, utiliza SQLite local.

def banco_de_dados():
    url = os.environ.get("DATABASE_URL", "").strip()

    if not url:
        return {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }

    dados = urlparse(url)

    porta = dados.port or 5432

    opcoes = {
        chave: valores[0]
        for chave, valores in parse_qs(dados.query).items()
    }

    opcoes.setdefault("sslmode", "require")

    configuracao = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': unquote(dados.path.lstrip("/")) or "postgres",
        'USER': unquote(dados.username or ""),
        'PASSWORD': unquote(dados.password or ""),
        'HOST': dados.hostname or "",
        'PORT': porta,
        'CONN_MAX_AGE': int(os.environ.get("DB_CONN_MAX_AGE", "60")),
        'OPTIONS': opcoes,
    }

    # Configuração para Transaction Pooler do Supabase
    if porta == 6543:
        configuracao['DISABLE_SERVER_SIDE_CURSORS'] = True
        configuracao['CONN_MAX_AGE'] = 0

    return {'default': configuracao}


DATABASES = banco_de_dados()


# ==========================================
# VALIDAÇÃO DE SENHAS
# ==========================================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# ==========================================
# IDIOMA E FUSO HORÁRIO
# ==========================================

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_TZ = True


# ==========================================
# ARQUIVOS ESTÁTICOS E MÍDIA
# ==========================================

STATIC_URL = '/static/'

STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'

MEDIA_ROOT = BASE_DIR / 'media'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]


# ==========================================
# CHAVE PRIMÁRIA PADRÃO
# ==========================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ==========================================
# GEOAPIFY - MAPAS
# ==========================================

GEOAPIFY_API_KEY = os.environ.get(
    "GEOAPIFY_API_KEY",
    "f73beb4cb8c849f0a2ca9139a6728752"
)


# ==========================================
# SUPABASE STORAGE
# ==========================================

SUPABASE_URL = os.environ.get(
    "SUPABASE_URL", ""
).strip().rstrip("/")

SUPABASE_SERVICE_ROLE_KEY = os.environ.get(
    "SUPABASE_SERVICE_ROLE_KEY", ""
).strip()

SUPABASE_STORAGE_BUCKET = os.environ.get(
    "SUPABASE_STORAGE_BUCKET", "noticias"
).strip()


# ==========================================
# SEGURANÇA HTTPS EM PRODUÇÃO
# ==========================================

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
