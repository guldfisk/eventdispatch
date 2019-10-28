import types
import weakref


class WeakMethodRef(object):

    def __init__(self, f, callback = None):
        try:
            self._obj = weakref.ref(
                f.__self__,
                (
                    None
                    if callback is None else
                    (lambda o: callback(self))
                ),
            )
            self._method = weakref.ref(f.__func__)
            self.hash = hash(
                types.MethodType(
                    self._method(),
                    self._obj(),
                )
            )
        except AttributeError:
            self._obj = None
            self._method = None
            self.hash = hash(None)

    def __call__(self):
        if not self.dead():
            return types.MethodType(
                self._method(),
                self._obj()
            )

    def __eq__(self, other):
        return (
            hasattr(other, '__self__')
            and self._obj == other.__self__()
            and self._method == other.__func__()
        )

    def __hash__(self):
        return self.hash

    def dead(self):
        return self._obj is None or self._obj() is None

    def __self__(self):
        return self._obj

    def __func__(self):
        return self._method

    def __str__(self):
        if self.dead():
            return '<{}; dead>'.format(
                super(WeakMethodRef, self).__repr__()
            )
        return '<{}; to {}>'.format(
            super(WeakMethodRef, self).__repr__(),
            types.MethodType(
                self._method(),
                self._obj()
            )
        )
