import itertools
import weakref

from eventdispatch.weakmethodref import WeakMethodRef

class _WeakSet(set):
	def __init__(self):
		def _remove(item, wself=weakref.ref(self)):
			self = wself()
			if self is not None:
				self.discard_ref(item)
		self._remove = _remove
	def register_ref(self, item):
		if hasattr(item, '__self__'):
			return WeakMethodRef(item, self._remove)
		return weakref.ref(item, self._remove)
	def __iter__(self):
		for item_ref in set(self):
			item = item_ref()
			if item is not None:
				yield item
	def add(self, item):
		super(_WeakSet, self).add(self.register_ref(item))
	def discard_ref(self, item):
		super(_WeakSet, self).discard(item)
	def discard(self, item):
		super(_WeakSet, self).discard(self.register_ref(item))
	def __str__(self):
		return '_WeakSet(%s)' % super(_WeakSet, self).__str__()

class DispatchSession(object):
	def __init__(self):
		self.signal_map = {}
	def connect(self, f, signal=None):
		if not signal in self.signal_map:
			self.signal_map[signal] = _WeakSet()
		self.signal_map[signal].add(f)
	def send(self, signal, **kwargs):
		return [
			pair 
			for pair in 
			(
				(connected, connected(**kwargs))
				for connected in
				itertools.chain(
					self.get_connected(signal),
					self.get_connected(None)
				)
			)
			if pair[0]
		]
	def get_connected(self, signal):
		return self.signal_map.get(signal, _WeakSet())
	def disconnect(self, f, signal=None):
		self.signal_map[signal].discard(f)
	def __str__(self):
		return 'DispatchSession(%s)' % {
			key: [
				item
				for item in
				self.signal_map[key]
			]
			for key in
			self.signal_map
		}