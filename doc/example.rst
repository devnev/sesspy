
Example
-------

::

 #
 # config
 #

 import ConfigParser
 import sesspy.config

 config = ConfigParser.RawConfigParser()
 # get_config is a callable that reads the specified paths on first call. This
 # allows overriding of the paths and other arguments
 get_config = sesspy.config.LazyConfigReader(
     config, ['/etc', '~/.config'], leaf='example'
 )

 #
 # connections
 #

 import sesspy.sqlalchemy
 import sesspy.registry

 # use the convenience functions for sqlalchemy
 example_db = sesspy.sqlalchemy.db_connection(
     db_uri=sesspy.config.ConfigOption(get_config, 'general', 'db_uri'),
     engine_args=dict(pool_recycle=3600),
     name='example_db',
 )

 # or create and register a session factory by hand
 example_connection = sesspy.session.SessionFactory(
     source_factory=sesspy.source.GuardedFactorySource(
         factory=my_connect_func,
         args=lambda: ((get_config().get('general', 'my_uri'),), {}),
     )
     adapter_factory=sesspy.source.sessionless_source_adapter,
     local_openers=False,
 )
 sesspy.registry.default_registry.register_component(
     'other_example', example_connection,
 )

 #
 # models
 #

 import sesspy.ref

 class Model1(object):
     # arg may be a component, another ref, a key for the registry (must not
     # contain any "." characters) or an import path.
     # making the ref a class attribute allows it to be overriden easily for
     # testing (dependency injection)
     db = sesspy.ref.ComponentRef(connector)

     def __init__(self, db=None):
         if db is not None:
             # 'db' may be any permissible ComponentRef arg, see above
             self.db = db

     # note: the decorator can be overriden by explicitly passing a keyword
     # argument, e.g. o.do_something(foo, example_db=my_db)
     @sesspy.dec.with_component(db, arg='example_db')
     def do_something(self, thing, example_db):
         example_db.execute(...)

     def do_something_else(self):
         # the decorator is basically a fancy way of doing this
         with self.db() as connection:
             connection.execute(...)

 class Model2(object):
     # skip explicit ComponentRef, look up in registry
     # note that in this case the 'arg' argument is optional
     @sesspy.dec.with_component('example_db')
     def do_something(self, thing, example_db):
         example_db.execute(...)

     @sesspy.dec.with_component('other_example', arg='connection')
     def do_something_with_connection(self, connection):
         connection.do(...)

 class Model3(object):
     # skip explicit ComponentRef, use an import path
     @sesspy.dec.with_component('example.db.connector', arg='example_db')
     def do_something(self, thing, example_db):
         example_db.execute(...)
