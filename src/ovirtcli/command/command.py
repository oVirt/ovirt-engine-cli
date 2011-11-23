
import uuid

from ovirtcli import metadata
from cli.command import Command
from ovirtcli.utils.typehelper import TypeHelper

from ovirtsdk.xml import params
from ovirtsdk.utils.parsehelper import ParseHelper


class OvirtCommand(Command):
    """Base class for RHEV commands."""

    def check_connection(self):
        """ensure we have a connection."""
        if self.context.connection is None:
            self.error('not connected', help='try \'help connect\'')
        return self.context.connection

    def resolve_base(self, options):
        """resolve a base object from a set of '--typeid value' options."""
        connection = self.check_connection()
#        path = {}

        for opt, val in options.items():
            if not opt.endswith('id'):
                continue
            typename = opt[2:-2]
            coll = typename + 's'
            if not (TypeHelper.isKnownType(typename) or  TypeHelper.isKnownType(coll)):
                self.error('no such type: %s' % typename)

            if hasattr(connection, coll):
                coll_ins = getattr(connection, coll)
                uuid_cand = self._toUUID(val)
                if uuid_cand != None:
                    base = coll_ins.get(id=val)
                else:
                    base = coll_ins.get(name=val)

                if base is None and len(options) > 0:
                    self.error('cannot find object %s' % val)
                return base


##            info = schema.type_info(typename)
#            if info is None:
#                self.error('unknown type: %s' % typename)
#            path[info[3]] = (options[opt], info)
##        base = connection.get(schema.API)
##        info = schema.type_info(type(base))
##FIXME:
#        info = None
#        while path:
##            links = connection.get_links(base)
##FIXME:
#            links = None
#            for link in links:
#                if link in path:
#                    break
#            else:
#                self.error('cannot find object in %s' % info[2])
#            id, info = path.pop(link)
##            base = self.get_object(info[0], id, base)
#            base = False
##FIXME:
#            if base is None:
#                self.error('%s does not exist: %s' % (info[2], id))
#        return base

    def create_object(self, typ, options, scope=None):
        """Create a new object of type `typ' based on the command-line
        options in `options'."""

        candidate = getattr(params, ParseHelper.getXmlWrapperType(typ))
        if candidate is not None:
            obj = candidate.factory()
            fields = metadata.get_fields(candidate, 'C', scope)
            for field in fields:
                key = '--%s' % field.name
                if key in options:
                    field.set(obj, options[key], self.context)
            return obj
        return None

    def update_object(self, obj, options, scope=None):
        """Create a new binding type of type `typ', and set its attributes
        with values from `options'."""
        fields = metadata.get_fields(type(obj.superclass), 'U', scope)
        for field in fields:
            key = '--%s' % field.name
            if key in options:
                field.set(obj, options[key], self.context)
        return obj

    def read_object(self):
        """If input was provided via stdin, then parse it and return a binding
        instance."""
        stdin = self.context.terminal.stdin
        # REVISE: this is somewhat of a hack (this detects a '<<' redirect by
        # checking if stdin is a StringIO)
        if not hasattr(stdin, 'len'):
            return
        buf = stdin.read()
        try:
            obj = params.parseString(buf)
        except Exception:
            self.error('could not parse input')
        return obj

    def get_collection(self, typ, opts=[], base=None):
        self.check_connection()
        connection = self.context.connection

        if base is None:
            if hasattr(connection, typ):
                return getattr(connection, typ).list(query=' '.join(opts) if len(opts) > 0
                                                                          else None)
        else:
            if hasattr(base, typ):
                return getattr(base, typ).list(query=' '.join(opts) if len(opts) > 0
                                                                    else None)
        return None

    def get_object(self, typ, id, base=None):
        """Return an object by id or name."""
        self.check_connection()
        connection = self.context.connection

        candidate = typ if typ is not None and isinstance(typ, type('')) \
                        else type(typ).__name__.lower()

        if base is None: base = connection
        if hasattr(base, candidate + 's'):
            coll = getattr(base, candidate + 's')
            if coll is not None:
                uuid_cand = self._toUUID(id)
                if uuid_cand != None:
                    return coll.get(id=id)
                else:
                    return coll.get(name=id)
        else:
            self.error('no such type: %s' % candidate)
        return None

    def _toUUID(self, string):
        try:
            return uuid.UUID(string)
        except:
            return None

    def _get_types(self, plural):
#        """INTERNAL: return a list of types."""
#        connection = self.check_connection()
#        links = connection.get_links(connection.api())
##        types = [schema.type_info(link) for link in links ]
##FIXME: support types exposer
#        types = []
#        ix = 2 + int(plural)
#        types = [ info[ix] for info in types if info and info[ix] ]
#        return types

        #return TypeHelper.getKnownTypes()
        return []

    def get_singular_types(self):
        """Return a list of singular types."""
        return self._get_types(False)

    def get_plural_types(self):
        """Return a list of plural types."""
        return self._get_types(True)

    def get_options(self, typ, flag, scope=None):
        """Return a list of options for typ/action."""
        fields = metadata.get_fields(typ, flag, scope=scope)
        options = [ '--%-20s %s' % (field.name, field.description)
                    for field in fields ]
        return options
