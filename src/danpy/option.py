from dataclasses import dataclass
from typing import Callable, TypeVar, Generic

T = TypeVar("T")
S = TypeVar("S")


@dataclass
class Some(Generic[T]):
    """
    A structural pattern matchable Option type for Python.

    For example

    .. code-block:: python

        x = to_opt(x)
        y = to_opt(y)
        match x, y:
            case Some(x), None:
                # do something with x
            case None, Some(y):
                # do something with y
            case Some(x), Some(y):
                # do something with both
            case _:
                # both are none :shrug:

    Compare this to the equivalent code without using :py:class:`Some`:

    .. code-block:: python

        match x, y:
            case x, None if x is not None:
                # do something with x
            case None, y if y is not None:
                # do something with y
            case x, y if x is not None and y is not None:
                # do something with both
            case _:
                # both are none :shrug:
    """

    val: T


Option = T | Some[T] | None  #: The "Option-like" types.


def to_opt(val: Option[T]) -> Some[T] | None:
    """
    Maybe wrap a value in :py:class:`Some` so we can use it pattern matches nicely.
    Idempotent, so calling on an instance of :py:class:`Some` will not nest.
    """
    match val:
        case Some():
            return val
        case None:
            return None
        case _:
            return Some(val)


def map_opt(val: Option[T], func: Callable[[T], S]) -> Some[S] | None:
    """
    Maybe map the contents of a :py:class:`Some`.
    If a raw :py:const:`T` is passed this will wrap it first.
    """
    match to_opt(val):
        case Some(t):
            return Some(func(t))
        case None:
            return None
        case _:
            assert False


def unwrap(some: T | Some[T]) -> T:
    """
    Get the value from inside a :py:class:`Some`.

    This function is idempotent so if a value is just the raw type, that will be returned.

    :raises: a :py:class:`TypeError` if ``None`` is passed.
    """
    match some:
        case Some(t):
            return t
        case None:
            raise TypeError()
        case _:
            return some


def or_default(opt: Option[T], default: T) -> T:
    """
    Either get the value contained in ``opt`` or return the default value if it is ``None``.

    Unlike the ``x or default`` idiom, this works with types that override the boolean operators.
    """
    try:
        return unwrap(opt)  # type: ignore
    except TypeError:
        return default


def or_get_default(opt: Option[T], get_default: Callable[[], T]) -> T:
    """
    Like the `(x or default)` idiom, but with lazy construction of the default value.

    See also :py:meth:`or_default`.
    """
    match opt:
        case Some(t):
            return t
        case None:
            return get_default()
        case _:
            return opt
