import itertools
import weakref
from weakmethodref import WeakMethodRef
		
class _WeakSet(set):
	def __init__(self):
		def _remove(item, wself=weakref.ref(self)):
			self = wself()
			if self is not None:
				self.discardRef(item)
		self._remove = _remove
	def registerRef(self, item):
		if hasattr(item, '__self__'):
			return WeakMethodRef(item, self._remove)
		return weakref.ref(item, self._remove)
	def __iter__(self):
		for itemref in set(self):
			item = itemref()
			if item is not None:
				yield item
	def add(self, item):
		super(_WeakSet, self).add(self.registerRef(item))
	def discardRef(self, item):
		super(_WeakSet, self).discard(item)
	def discard(self, item):
		super(_WeakSet, self).discard(self.registerRef(item))
	def __str__(self):
		return '_WeakSet(%s)' % super(_WeakSet, self).__str__()

class DispatchSession(object):
	def __init__(self):
		self.signaleMap = {}
	def connect(self, f, signal=None):
		if not signal in self.signaleMap:
			self.signaleMap[signal] = _WeakSet()
		self.signaleMap[signal].add(f)
	def send(self, signal, **kwargs):
		return [
			pair 
			for pair in 
			(
				(connected, connected(**kwargs))
				for connected in
				itertools.chain(
					self.getConnected(signal), 
					self.getConnected(None)
				)
			)
			if pair[0]
		]
	def getConnected(self, signal):
		return self.signaleMap.get(signal, _WeakSet())
	def disconnect(self, f, signal=None):
		self.signaleMap[signal].discard(f)
	def __str__(self):
		return 'DispatchSession(%s)' % {
			key: [
				item
				for item in
				self.signaleMap[key]
			]
			for key in
			self.signaleMap
		}