# -*- coding: utf-8 -*-
"""
    prestans3.types
    ~~~~~~~~~~~~~~~
    
    A WSGI compliant REST micro-framework.

    :copyright: (c) 2016 Anomaly Software
    :license: Apache 2.0, see LICENSE for more details.
"""
import functools


class ImmutableType(object):
    """
    Base class of all |types|. Default behaviour of setting an attribute on this class is to throw an
    :class:`AttributeError<builtins.AttributeError>`

    Attributes:
        property_rules  registered property rules for this |type|
    """

    property_rules = {}

    def __init__(self, validate_immediately=True):
        """
        NOTE: call this method after setting values if validating immediately in order for validation to work!

        if validate_immediately is set, this may possibly raise a |ValidationException| when initializing the object.
        This is the default behaviour of all immutable types.

        :param bool validate_immediately: whether to validate this object on construction or defer validation to the
                                          user or prestans3 REST api process
        :raises: |ValidationException| on invalid state when validate_immediately is True
        """
        if validate_immediately:
            self.validate()

    @classmethod
    def property(cls, **kwargs):
        """
        :return: configured |_Property| Class
        :rtype: |_Property|
        """
        return _Property(of_type=cls, **kwargs)

    __prestans_attribute__ = True

    def validate(self, validation_exception=None):
        """
        validates against own |rules| and configured |attribute|\ 's rules.

        :
        :raises: |ValidationException| on invalid state
        :rtype: ``True``
        """

        # iterate through own rules
        for property_rule in self.property_rules:
            pass
            # property_rule(self)
        if validation_exception is not None:
            return True
        else:
            raise validation_exception  # todo change this, this implementation is incorrect

    #
    @classmethod
    def from_value(cls, value, *args, **kwargs):
        """
        returns the wrapped instance of this |type| from a given value. subclasses of |ImmutableType| must override this
        method if prestans should attempt to assign a |_Property| to an object other than an instance of this class.

        for a |Model| containing a |String| |_Property|, this will allow an api developer to set the contents of the
        |String| |type| to a native python ``str``:

        >>> import prestans3.types as types
        >>> class MyClass(types.Model):
        ...     name = String.property()
        ...
        >>> my_class = MyClass()
        >>> my_class.name = "jum"

        :param value: an acceptable value according to the |type|\ 's subclass
        :raises NotImplementedError: if called on a subclass that does not override this method
        """
        raise NotImplementedError

    @classmethod
    def register_property_rule(cls, property_rule, name=None, default=None, configurable=True):
        """
        Register a |rule| with all instances and subclasses of this |type|

        :param property_rule: callable to be registered
        :type property_rule: rule(instance: ImmutableType, config: any) -> bool
        :param str name: name of the |rule| as will appear in configuring the property:
        :param object default: the default configuration to apply to this |rule| if none is specified
        :param bool configurable: when ``False``, adding a rule configuration for this property will throw an error

        >>> import prestans3.types as types
        >>> class MyClass(Model):
        ...     pass
        ...
        >>> def my_property_rule(instance, config):  # assuming config is a bool
        ...     pass
        ...
        >>> MyClass.register_property_rule(my_property_rule, name="custom_prop")
        >>> class MyOwningClass(Model):
        ...     sub_prop = MyClass.property(custom_prop=True)  # should now configure the custom_prop
        """
        arg_count = property_rule.__code__.co_argcount
        if arg_count != 2:
            func_name = property_rule.__name__
            func_args = property_rule.__code__.co_varnames
            raise ValueError(
                "expected property_rule function with 2 arguments, received function with {} argument(s): {}({})".format(
                    arg_count, func_name, ", ".join(func_args)))

        @functools.wraps(property_rule)
        def wrapped_pr(*args):
            result = property_rule(*args)
            return result
            # if not isinstance()

        wrapped_pr.default_config = default
        wrapped_pr.configurable = configurable
        if name is None:
            name = wrapped_pr.__name__
        cls.property_rules.update({name: wrapped_pr})

    @classmethod
    def get_property_rule(cls, name):
        """ retrieve the |rule| by name (``str``) """
        return cls.property_rules[name]


class _Property(object):
    """
    Base class for all |_Property| configurations. not instantiated directly but called from the owning |type|\ 's
    :func:`property()<prestans3.types.ImmutableType.property>` method. A |_Property| is a type descriptor that allows the
    setting of prestans attributes on it's containing class
    """

    def __init__(self, of_type, required=True, **kwargs):
        """
        :param of_type: The class of the |type| being configured. Must be a subclass of |ImmutableType|
        :type of_type: T <= :attr:`ImmutableType.__class__<prestans3.types.ImmutableType>`
        """
        self._of_type = of_type
        self._rules_config = {}
        self._setup_rules_config(kwargs)
        self.required = required
        # if 'required' not in kwargs:
        #     kwargs.update(required=lambda is_required, instance: _required(True, instance))
        # if 'default' not in kwargs:
        #     kwargs.update(default=lambda default_value, instance: ImmutableType._Property._default(None, instance))
        # for _ in kwargs.keys():
        #     pass
        # todo return ImmutableType whose validate method will call it's validators curried with it's member values

    def __set__(self, instance, value):
        """
        If the value provided is not a subclass of the this |_Property|\ 's |type|\ , then it is passed to
        :func:`.ImmutableType.from_value()` in an attempt to coerce the value to the desired |type|.

        :param instance: the storage for this class' |attributes|\ .
        :type instance: dict[str, |ImmutableType|\ ]
        :param value: a subclass or coercible value of this class's |type|\ .
        :type value: T <= G
        """
        # _prestans_attributes.update()
        print("set value: {}".format(value))
        # if value is a ImmutableType then set it otherwise construct it from variable
        if isinstance(value[1], self._of_type):
            instance[value[0]] = value[1]
        else:
            instance[value[0]] = self._of_type.from_value(value[1])

    def __get__(self, instance, owner):
        """
        :param instance: The instance of this |type|
        :type instance: T <= |ImmutableType|
        :param owner: class type of the instance
        :type owner: any
        :return: the value this descriptor holds
        """
        # my_locals = locals()
        # print("got value: {}".format(instance._value))
        # return instance._value
        return instance

    @property
    def rules_config(self):
        """ contains the configuration for all the |rules| on this |_Property| instance """
        return self._rules_config

    @property
    def property_type(self):
        """
        :return: T <= :attr:`ImmutableType.__class__<prestans3.types.ImmutableType>`
        """
        return self._of_type

    def _add_rule_config(self, key, config):
        """ adds a configuration of a |rule| to this instance """
        try:
            _rule = self.property_type.get_property_rule(key)
        except KeyError:
            raise ValueError("{} is not a registered rule of type {}".format(key, self.property_type.__name__))
        if not _rule.configurable:
            raise ValueError("{} is a non-configurable rule in class {}, (see {}.{}()))" \
                             .format(key, self.property_type.__name__, ImmutableType.__name__,
                                     ImmutableType.register_property_rule.__name__))
        self._rules_config.update({key: config})

    def get_rule_config(self, key):
        """ find a |rule|\ 's configuration by its name """
        return self._rules_config[key]

    def _setup_rules_config(self, kwargs):
        """
        merge default rule configs with explicit rule configs in kwargs

        :param dict kwargs:
        """
        defaults = {key: rule.default_config for key, rule in list(self.property_type.property_rules.items()) \
                    if rule.default_config and rule.configurable}
        all_config = defaults.copy()
        all_config.update(kwargs)
        [self._setup_non_configurable_rule_config(key, rule.default_config) \
         for key, rule in list(self.property_type.property_rules.items()) \
         if not rule.configurable and rule.default_config]
        [self._add_rule_config(key, config) for key, config in list(all_config.items())]

    def _setup_non_configurable_rule_config(self, key, config):
        try:
            self.property_type.get_property_rule(key)
        except KeyError:
            raise ValueError("{} is not a registered rule of type {}".format(key, self.property_type.__name__))

        if key in self.rules_config:
            from prestans3.errors import InvalidMethodUseError
            raise InvalidMethodUseError(self.__class__._setup_non_configurable_rule_config,
                                        "This is an internal method and shouldn't be called directly, "
                                        "if you wish to make a rule configurable, use the configurable kwarg in "
                                        "the {}.{}() function".format(ImmutableType.__name__,
                                                                      ImmutableType.register_property_rule.__name__))
        self._rules_config.update({key: config})


# noinspection PyAbstractClass
class Scalar(ImmutableType):
    """
    Base type of all |Scalar| |attributes|\ .

    known Subclasses:
        - |Boolean|
        - |Number|
            - |Integer|
            - |Float|
        - |String|
        - |Date|
        - |DateTime|
        - |Time|
    """
    pass


# noinspection PyAbstractClass
class Container(ImmutableType):
    """ subclass of all |types| with containable |attributes| """

    # dict[str, func(owner: |ImmutableType|, instance: |ImmutableType|, config: any) -> bool]
    # func raises |ValidationException| on invalidation
    _owner_property_rules = {}

    @classmethod
    def register_owner_property_rule(cls, owner_property_rule, name=None, default=None):
        """
        Register an owner type |rule| with all instances and subclasses of this |type|

        :param owner_property_rule: callable to be registered
        :type owner_property_rule: rule(owner: T <= Container.__class__, instance: ImmutableType, config: any) -> bool
        :param str name: name of the |rule| as will appear in configuring the |_Property|:

        >>> import prestans3.types as types
        >>> class MyClass(Model):
        ...     pass
        ...
        >>> def my_owner_property_rule(owner, instance, config):  # assuming config is a bool
        ...     pass
        ...
        >>> MyClass.register_property_rule(my_owner_property_rule, name="custom_owner_prop")
        >>> class MyOwningClass(Model):
        ...     sub_owner_prop = MyClass.property(custom_owner_prop=True)  # should now configure the custom_prop
        """
        argcount = owner_property_rule.__code__.co_argcount
        if argcount != 3:
            func_name = owner_property_rule.__name__
            func_args = owner_property_rule.__code__.co_varnames
            raise ValueError(
                "expected owner_property_rule function with 3 arguments, received function with {} argument(s): {}({})" \
                    .format(argcount, func_name, ", ".join(func_args)))

        @functools.wraps(owner_property_rule)
        def wrapped_opr(*args):
            result = owner_property_rule(*args)
            # if not isinstance()

        if name is None:
            name = wrapped_opr.__name__
        cls._owner_property_rules.update({name: wrapped_opr})

    @classmethod
    def get_owner_property_rule(cls, name):
        """ retrieve the owner |rule| by name (``str``) """
        return cls._owner_property_rules[name]


from .boolean import Boolean as Boolean
from .number import Number as Number
from .integer import Integer as Integer
from .float import Float as Float
from .string import String as String
from .model import Model as Model
from .array import Array as Array
from .p_date import Date as Date
from .p_datetime import DateTime as DateTime
from .time import Time as Time
