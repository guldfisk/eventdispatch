import types
import weakref

class WeakMethodRef(object):
	def __init__(self, f, callback=None):
		if callback:
			c = (lambda o: callback(self))
		else:
			c = None
		try:
			self._obj = weakref.ref(f.__self__, c)
			self._meth = weakref.ref(f.__func__)
			self.hash = hash(
				types.MethodType(
					self._meth(),
					self._obj()
				)
			)
		except AttributeError:
			self._obj = None
			self._meth = None
			self.hash = hash(None)
	def __call__(self):
		if not self.dead():
			return types.MethodType(
				self._meth(),
				self._obj()
			)
	def __eq__(self, other):
		return (
			hasattr(other, '__self__')
			and self._obj==other.__self__()
			and self._meth==other.__func__()
		)
	def __hash__(self):
		return self.hash
	def dead(self):
		return self._obj is None or self._obj() is None
	def __self__(self):
		return self._obj
	def __func__(self):
		return self._meth
	def __str__(self):
		if self.dead():
			return '<%s; dead>' % super(WeakMethodRef, self).__repr__()
		return '<%s; to %r' % (
			super(WeakMethodRef, self).__repr__(),
			types.MethodType(
				self._meth(),
				self._obj()
			)
		)