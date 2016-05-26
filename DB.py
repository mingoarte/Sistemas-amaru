# -*- coding: utf-8 -*-

# -------------------------------------------------------------------------
# This scaffolding model makes your app work on Google App Engine too
# File is released under public domain and you can use without limitations
# -------------------------------------------------------------------------

if request.global_settings.web2py_version < "2.14.1":
    raise HTTP(500, "Requires web2py 2.13.3 or newer")

# -------------------------------------------------------------------------
# if SSL/HTTPS is properly configured and you want all HTTP requests to
# be redirected to HTTPS, uncomment the line below:
# -------------------------------------------------------------------------
# request.requires_https()

# -------------------------------------------------------------------------
# app configuration made easy. Look inside private/appconfig.ini
# -------------------------------------------------------------------------
from gluon.contrib.appconfig import AppConfig

# -------------------------------------------------------------------------
# once in production, remove reload=True to gain full speed
# -------------------------------------------------------------------------
myconf = AppConfig(reload=True)

if not request.env.web2py_runtime_gae:
    # ---------------------------------------------------------------------
    # if NOT running on Google App Engine use SQLite or other DB
    # ---------------------------------------------------------------------
    db = DAL('sqlite://storage.db')
    '''
    db = DAL(myconf.get('db.uri'),
             pool_size=myconf.get('db.pool_size'),
             migrate_enabled=myconf.get('db.migrate'),
             check_reserved=['all'])'''
else:
    # ---------------------------------------------------------------------
    # connect to Google BigTable (optional 'google:datastore://namespace')
    # ---------------------------------------------------------------------
    db = DAL('google:datastore+ndb')
    # ---------------------------------------------------------------------
    # store sessions and tickets there
    # ---------------------------------------------------------------------
    session.connect(request, response, db=db)
    # ---------------------------------------------------------------------
    # or store session in Memcache, Redis, etc.
    # from gluon.contrib.memdb import MEMDB
    # from google.appengine.api.memcache import Client
    # session.connect(request, response, db = MEMDB(Client()))
    # ---------------------------------------------------------------------

# -------------------------------------------------------------------------
# by default give a view/generic.extension to all actions from localhost
# none otherwise. a pattern can be 'controller/function.extension'
# -------------------------------------------------------------------------
response.generic_patterns = ['*'] if request.is_local else []
# -------------------------------------------------------------------------
# choose a style for forms
# -------------------------------------------------------------------------
response.formstyle = myconf.get('forms.formstyle')  # or 'bootstrap3_stacked' or 'bootstrap2' or other
response.form_label_separator = myconf.get('forms.separator') or ''

# -------------------------------------------------------------------------
# (optional) optimize handling of static files
# -------------------------------------------------------------------------
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

# -------------------------------------------------------------------------
# (optional) static assets folder versioning
# -------------------------------------------------------------------------
# response.static_version = '0.0.0'

# -------------------------------------------------------------------------
# Here is sample code if you need for
# - email capabilities
# - authentication (registration, login, logout, ... )
# - authorization (role based authorization)
# - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
# - old style crud actions
# (more options discussed in gluon/tools.py)
# -------------------------------------------------------------------------

from gluon.tools import Auth, Service, PluginManager

# host names must be a list of allowed host names (glob syntax allowed)
auth = Auth(db, host_names=myconf.get('host.names'))
service = Service()
plugins = PluginManager()

# -------------------------------------------------------------------------
# create all tables needed by auth if not custom tables
# -------------------------------------------------------------------------
auth.define_tables(username=False, signature=False)

# -------------------------------------------------------------------------
# configure email
# -------------------------------------------------------------------------
mail = auth.settings.mailer
mail.settings.server = 'logging' if request.is_local else myconf.get('smtp.server')
mail.settings.sender = myconf.get('smtp.sender')
mail.settings.login = myconf.get('smtp.login')
mail.settings.tls = myconf.get('smtp.tls') or False
mail.settings.ssl = myconf.get('smtp.ssl') or False

# -------------------------------------------------------------------------
# configure auth policy
# -------------------------------------------------------------------------
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

# -------------------------------------------------------------------------
# Define your tables below (or better in another model file) for example
#
# >>> db.define_table('mytable', Field('myfield', 'string'))
#
# Fields can be 'string','text','password','integer','double','boolean'
#       'date','time','datetime','blob','upload', 'reference TABLENAME'
# There is an implicit 'id integer autoincrement' field
# Consult manual for more options, validators, etc.
#
# More API examples for controllers:
#
# >>> db.mytable.insert(myfield='value')
# >>> rows = db(db.mytable.myfield == 'value').select(db.mytable.ALL)
# >>> for row in rows: print row.id, row.myfield
# -------------------------------------------------------------------------

# -------------------------------------------------------------------------
# after defining tables, uncomment below to enable auditing
# -------------------------------------------------------------------------
# auth.enable_record_versioning(db)

db.define_table('usuario',
    Field('ci', 'string', length=8),
    Field('nombres', 'string', length=50),
    Field('apellido', 'string', length=50),
    Field('password', 'password', length=10),
    Field('telefono', 'string', length=15),
    Field('email', 'string', length=30),
    Field('tipo', 'integer'),
    primarykey = ['ci'])

db.define_table('usbid',
    Field('ci_usuario', 'reference usuario.ci'),
    Field('usbid', 'string', length=20),
    primarykey = ['ci_usuario', 'usbid'])

db.define_table('jefe_dependencia',
    Field('id_jefe', 'id'),
    Field('ci_usuario', 'reference usuario.ci', notnull=True),
    primarykey = ['id_jefe'])

db.define_table('tipo_actividad',
    Field('id_tipo', 'id'),
    Field('nombre', 'string', length=128, notnull=True),
    Field('tipo_p_r', 'string', length=1, notnull=True),
    Field('descripcion', 'text', length=2048, notnull=True),
    Field('programa', 'string', length=128, notnull=True),
    Field('validacion', 'boolean', length=128, notnull=True),
    Field('producto', 'string', length=256),
    Field('nro_campos', 'integer'),
    Field('id_jefe_creador', 'reference jefe_dependencia.id_jefe'),
    Field('ci_usuario_propone', 'reference usuario.ci'),
    primarykey = ['id_tipo'])

db.define_table('actividad',
    Field('id_actividad', 'id'),
    Field('id_tipo', 'reference tipo_actividad.id_tipo'),
    Field('validacion', 'string', default='En espera'),
    Field('estado', 'string'),
    Field('evaluacion_criterio', 'string', length=256),
    Field('evaluacion_valor', 'string', length=256),
    Field('ci_usuario_modifica', 'reference usuario.ci'),
    Field('ci_usuario_elimina', 'reference usuario.ci'),
    Field('ci_usuario_crea', 'reference usuario.ci'),
    primarykey = ['id_actividad'])

db.define_table('permisos_tipo_act',
    Field('permiso', 'string', length=256),
    Field('id_tipo', 'reference tipo_actividad.id_tipo'),
    primarykey = ['permiso', 'id_tipo'])

db.define_table('catalogo',
    Field('id_catalogo', 'id'),
    Field('nro_campos', 'integer'),
    Field('nombre', 'string', length=128),
    primarykey = ['id_catalogo'])

db.define_table('campo',
    Field('id_campo', 'id'),
    Field('obligatorio', 'boolean'),
    Field('nombre', 'string', length=64),
    Field('lista', 'string', length=64),
    Field('despliega_cat', 'reference catalogo.id_catalogo'),
    primarykey = ['id_campo'])

db.define_table('campo_catalogo',
    Field('id_campo_cat', 'id'),
    Field('tipo_cat', 'string', length=256),
    Field('nombre', 'string', length=64),
    primarykey = ['id_campo_cat'])

db.define_table('log',
    Field('accion', 'text'),
    Field('accion_fecha', 'date'),
    Field('accion_ip', 'integer'),
    Field('descripcion', 'text'),
    Field('ci_usuario', 'reference usuario.ci'),
    primarykey = ['accion', 'accion_fecha', 'accion_ip'])

db.define_table('participa_act',
    Field('ci_usuario', 'reference usuario.ci'),
    Field('id_actividad', 'reference actividad.id_actividad'),
    primarykey = ['ci_usuario', 'id_actividad'])

db.define_table('tiene_campo',
    Field('id_actividad', 'reference actividad.id_actividad'),
    Field('id_campo', 'reference campo.id_campo'),
    Field('valor_campo', 'string', length=256),
    primarykey = ['id_actividad', 'id_campo'])

db.define_table('act_posee_campo',
    Field('id_tipo_act', 'reference tipo_actividad.id_tipo'),
    Field('id_campo', 'reference campo.id_campo'),
    primarykey = ['id_tipo_act', 'id_campo'])

db.define_table('gestiona_tipo_act',
    Field('id_jefe', 'reference jefe_dependencia.id_jefe'),
    Field('id_tipo_act', 'reference tipo_actividad.id_tipo'),
    primarykey = ['id_jefe', 'id_tipo_act'])

db.define_table('gestiona_catalogo',
    Field('id_jefe', 'reference jefe_dependencia.id_jefe'),
    Field('id_catalogo', 'reference catalogo.id_catalogo'),
    primarykey = ['id_jefe', 'id_catalogo'])

db.define_table('catalogo_tiene_campo',
    Field('id_catalogo', 'reference catalogo.id_catalogo'),
    Field('id_campo_cat', 'reference campo_catalogo.id_campo_cat'),
    primarykey = ['id_catalogo', 'id_campo_cat'])

db.define_table('catalogo_contiene_campo',
    Field('id_catalogo', 'reference catalogo.id_catalogo'),
    Field('id_campo_cat', 'reference campo_catalogo.id_campo_cat'),
    Field('valor', 'string', length=256),
    primarykey = ['id_catalogo', 'id_campo_cat'])



