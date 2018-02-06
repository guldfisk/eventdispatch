import typing as t

import itertools
import weakref

from eventdispatch.weakmethodref import WeakMethodRef

class _WeakSet(set):
	def __init__(self):
		super(_WeakSet, self).__init__()
		def _remove(item, weak_self=weakref.ref(self)):
			self = weak_self()
			if self is not None:
				self._discard_ref(item)
		self._remove = _remove
	def _register_ref(self, item):
		if hasattr(item, '__self__'):
			return WeakMethodRef(item, self._remove)
		return weakref.ref(item, self._remove)
	def __iter__(self):
		for item_ref in set(self):
			item = item_ref()
			if item is not None:
				yield item
	def add(self, item):
		super(_WeakSet, self).add(self._register_ref(item))
	def _discard_ref(self, item):
		super(_WeakSet, self).discard(item)
	def discard(self, item):
		super(_WeakSet, self).discard(self._register_ref(item))
	def __str__(self):
		return '_WeakSet(%s)' % super(_WeakSet, self).__str__()

class DispatchSession(object):
	def __init__(self):
		self.signal_map = {} #type: t.Dict[t.Hashable, t.Set[t.Callable]]
	def connect(self, f: t.Callable, signal: t.Hashable = None):
		if not signal in self.signal_map:
			self.signal_map[signal] = _WeakSet()
		self.signal_map[signal].add(f)
	def send(self, signal, **kwargs) -> t.List[t.Tuple[t.Callable, t.Any]]:
		return [
			(_connected, value)
			for _connected, value in 
			(
				(connected, connected(**kwargs))
				for connected in
				itertools.chain(
					self.get_connected(signal),
					self.get_connected(None)
				)
			)
			if value is not None
		]
	def get_connected(self, signal) -> t.Set[t.Callable]:
		return self.signal_map.get(signal, _WeakSet())
	def disconnect(self, f, signal=None) -> None:
		self.signal_map[signal].discard(f)
	def __str__(self):
		return '{}({})'.format(
			self.__class__.__name__,
			{
				key: [
					item
					for item in
					self.signal_map[key]
				]
				for key in
				self.signal_map
			}
		)