# -*- coding: utf-8 -*-
"""
    tests.types.test_model
    ~~~~~~~~~~~~~~~~~~~~~~

    A WSGI compliant REST micro-framework.

    :copyright: (c) 2016 Anomaly Software
    :license: Apache 2.0, see LICENSE for more details.
"""
import random
from datetime import datetime

import pytest
from prestans3.errors import ValidationException, AccessError
from prestans3.types import Array
from prestans3.types import DateTime
from prestans3.types import Float
from prestans3.types import Integer, String, Model
from prestans3.types.model import ModelValidationException

exception_1 = ValidationException(String)
exception_2 = ValidationException(String)


class MyModel(Model):
    some_string = String.property()


# def test_validation_tree_can_accept_single_validation_message_in___init__

class MySuperModel(Model):
    some_model = MyModel.property(required=True)
    stringy_1 = String.property()
    stringy_2 = String.property()


def test_should_raise_exception_when_adding_validation_exception_for_attribute_of_different_type():
    exception_integer = ValidationException(Integer)
    model_exception = ModelValidationException(MySuperModel, ('stringy_1', exception_1))
    with pytest.raises(TypeError) as error:
        model_exception.add_validation_exception('stringy_2', exception_integer)
    assert 'validation exception for MySuperModel.stringy_2 was of type Integer, ' + \
           'however MySuperModel.stringy_2 is a String Property' \
           in str(error.value)
    with pytest.raises(TypeError) as error:
        ModelValidationException(MySuperModel, ('stringy_2', exception_integer))
    assert 'validation exception for MySuperModel.stringy_2 was of type Integer, ' + \
           'however MySuperModel.stringy_2 is a String Property' \
           in str(error.value)


def test_validation_error_can_have_child_validation_exception():
    validation_exception = ValidationException(String)
    model_exception = ModelValidationException(MyModel, ('some_string', validation_exception))
    assert isinstance(model_exception.validation_exceptions['some_string'], ValidationException)
    assert validation_exception == model_exception.validation_exceptions['some_string']


def test_can_append_additional_child_validation_exceptions_to_validation_exception():
    model_exception = ModelValidationException(MySuperModel, ('stringy_1', exception_1))
    model_exception.add_validation_exception('stringy_2', exception_2)
    assert all([key in model_exception.validation_exceptions.keys() for key in ['stringy_1', 'stringy_2']])
    assert exception_1 == model_exception.validation_exceptions['stringy_1']
    assert exception_2 == model_exception.validation_exceptions['stringy_2']


def test_should_not_add_non_validation_exception_subclass_to_model_validation_exceptions():
    model_exception = ModelValidationException(MySuperModel, ('stringy_1', exception_1))
    with pytest.raises(TypeError):
        model_exception.add_validation_exception('stringy_2', "not an exception")
    with pytest.raises(TypeError):
        ModelValidationException(MySuperModel, ('stringy_2', "also not an exception"))


def test_should_only_add_validation_exceptions_for_attribute_keys_of_defined_prestans_properties_contained_on_model_class_definition():
    model_exception = ModelValidationException(MySuperModel, ('stringy_1', exception_1))
    with pytest.raises(AttributeError) as error:
        model_exception.add_validation_exception('not_an_attribute', exception_1)
    assert 'not_an_attribute is not a configured prestans attribute of MySuperModel class, when trying to set validation exception' in str(
        error.value)


def test_can_retrieve_dict_of_validation_exceptions_by_qualified_name():
    sub_sub_exception = ValidationException(String)
    sub_model_exception = ModelValidationException(MyModel, ('some_string', sub_sub_exception))
    model_exception = ModelValidationException(MySuperModel, ('some_model', sub_model_exception))


def test_nested_exception_message_correctly_constructed_from_root_exception_class():
    validation_exception = ValidationException(String, "error with string")
    sub_validation_exception = ModelValidationException(MyModel, ('some_string', validation_exception))
    super_validation_exception = ModelValidationException(MySuperModel, ('some_model', sub_validation_exception))
    expected_message = 'MySuperModel.some_model.some_string is invalid: ["error with string"]'
    assert expected_message == str(super_validation_exception[0])


def test_cannot_add_validation_exception_to_scalar_validation_exception():
    model_exception = ModelValidationException(String, "error")
    with pytest.raises(TypeError):
        # noinspection PyUnresolvedReferences
        model_exception.add_validation_exception('not way', ValidationException(String, "error"))


def test_property_type_returns_correct_value():
    assert ModelValidationException(MySuperModel, ('stringy_1', exception_1)).property_type == MySuperModel


def test_can_make_mutable_version_of_model_class():
    mutable_model = MyModel.mutable()
    mutable_model.some_string = 'potato'


def test_cannot_make_mutable_of_base_model_class():
    with pytest.raises(TypeError):
        Model.mutable()


def test_model_validation_exception_iters_own_messages_and_attribute_messages():
    class __Model(Model):
        my_string = String.property()
        my_int = Integer.property()

    exception = ModelValidationException(__Model)
    exception.add_validation_messages(["own message"])
    exception.add_validation_exception("my_string", ValidationException(String, "invalid"))
    exception.add_validation_exception("my_int", ValidationException(Integer, "invalid"))

    def invalid_format(name, message):
        return '{} is invalid: ["{}"]'.format(name, message)

    assert invalid_format(__Model.__name__, "own message") in str(exception)
    assert invalid_format("{}.{}".format(__Model.__name__, 'my_string'), "invalid") in str(exception)
    assert invalid_format("{}.{}".format(__Model.__name__, 'my_int'), "invalid") in str(exception)


def test_immutable_type_cannot_set_prestans_attributes():
    class __Model(Model):
        my_string = String.property(required=False)

    model = __Model()
    with pytest.raises(AccessError) as error:
        model.my_string = "should not work"
    assert 'attempted to set value of prestans3 attribute on an immutable Model' in str(error.value)


def test_model_can_provide_initial_values_through_init_method():
    class _Model(Model):
        my_string = String.property()
        my_int = Integer.property()

        def __init__(self, my_string, my_int):
            super(_Model, self).__init__({'my_string': my_string, 'my_int': my_int})

    model = _Model('string', 1)
    assert model.my_int == 1
    assert model.my_string == 'string'


def test_cannot_del_prestans_attribute_on_immutable_model():
    class _Model(Model):
        def __init__(self, string):
            super(_Model, self).__init__({'my_string': 'cannot delete'})

        my_string = String.property(required=False)

    model = _Model('cannot delete')
    assert model.my_string == 'cannot delete'
    with pytest.raises(AccessError) as error:
        del model.my_string
    assert 'attempted to delete value of prestans3 attribute on an immutable Model' in str(error.value)


def test_cannot_pass_non_prestans_attributes_to_super_init_method():
    class _Model(Model):
        def __init__(self):
            super(_Model, self).__init__({'not_an_attribute': 'doesn\'t matter'})

    with pytest.raises(ValueError):
        _Model()


def test_can_retrieve_prestans_attributes_via_properties():
    class _Model(Model):
        my_string = String.property()

        def __init__(self):
            super(_Model, self).__init__({'my_string': 'default'})

    model = _Model()
    attributes = model.prestans_attributes
    assert attributes['my_string'] == 'default'


def test_cannot_mutate_prestans_attributes_for_immutable_model():
    class _Model(Model):
        my_string = String.property()

        def __init__(self):
            super(self.__class__, self).__init__({'my_string': 'default'})

    model = _Model()
    attributes = model.prestans_attributes
    with pytest.raises(AccessError):
        attributes['my_string'] = 'should not work'


def test_subclasses_of_model_inherit_attributes():
    class _Model(Model):
        my_string = String.property()

        def __init__(self, initial_values=None):
            if initial_values is None:
                initial_values = {}
            initial_values.update({'my_string': 'string1'})
            super(_Model, self).__init__(initial_values)

    class _SubModelShouldInherit(_Model):
        my_sub_string = String.property()

        def __init__(self):
            super(_SubModelShouldInherit, self).__init__({'my_sub_string': 'string2'})

    sub_model = _SubModelShouldInherit()
    attributes = sub_model.prestans_attributes
    assert 'my_string' in attributes
    assert 'my_sub_string' in attributes
    assert attributes['my_string'] == 'string1'
    assert attributes['my_sub_string'] == 'string2'


def test_can_mutate_prestans_attributes_for_mutable_model():
    class _Model(Model):
        my_string = String.property()

        def __init__(self):
            super(_Model, self).__init__({'my_string': 'default'})

    model = _Model.mutable()
    attributes = model.prestans_attributes
    attributes['my_string'] = 'should work'


def test_default_parameter_inits_value_with_copy_of_default_if_none_provided():
    class _Other(Model):
        pass

    class _Model(Model):
        string = String.property(default="default_string")
        other = _Other.property(default=_Other())

    model = _Model()
    model_2 = _Model()
    assert model.string == 'default_string'
    assert model.other is not model_2.other


def test_model_attribute_gets_configuration_passed_to_it_in_validation():
    class _SubModel(Model):
        pass

    def _foo(instance, config):
        assert config == 'bar'

    _SubModel.register_property_rule(_foo, name="foo", default='baz')

    class _Model(Model):
        sub = _SubModel.property(foo='bar')

    model = _Model.mutable()
    model.sub = _SubModel.mutable()
    model.validate()


def test_complex_model():
    class Item(Model):
        name = String.property(min_length=3, format_regex=r'[a-zA-Z ]+')
        price = Float.property()
        description = String.property(required=False)

    class LineOrder(Model):
        count = Integer.property(min=1)
        item = Item.property()

    class Order(Model):
        orders = Array.property(element_type=LineOrder, min_length=1, max_length=10, default=[])
        total_price = Float.property(min=0)
        purchase_date = DateTime.property()

    order = Order.mutable()
    orders = []
    for i in range(10):
        line_order = LineOrder.mutable()
        item = Item.mutable()
        item.name = random.choice(['shampoo', 'lead pencils', 'chips', 'milk', 'fat', 'meat', 'sour cream', 'nachos'])
        item.price = random.random() % 100
        item.description = random.choice(['fantastic product!', 'great buy', 'excellent quality', 'much wow'])
        line_order.item = item
        line_order.count = random.randint(1, 10)
        orders.append(line_order)
    order.orders = orders
    order.total_price = 7.3
    order.purchase_date = datetime(2000, 12, 26, 9, 0, 4, 0)

    order.validate()


def test_can_delete_transient_value_on_model():
    class _Model(Model):
        string = String.property(default="foo")

    model = _Model()
    model.baz = 'spam'
    assert model.baz == 'spam'
    del model.baz
    assert 'baz' not in model.__dict__
