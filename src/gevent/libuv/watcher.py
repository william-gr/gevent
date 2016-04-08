# pylint: disable=too-many-lines, protected-access, redefined-outer-name, not-callable
from __future__ import absolute_import, print_function
import sys

import gevent.libuv._corecffi as _corecffi # pylint:disable=no-name-in-module,import-error

ffi = _corecffi.ffi # pylint:disable=no-member
libuv = _corecffi.lib # pylint:disable=no-member


from gevent._ffi import watcher as _base


class watcher(_base.watcher):
    _FFI = ffi
    _LIB = libuv

    _watcher_prefix = 'uv'
    _watcher_struct_pattern = '%s_t'
    _watcher_callback_name = '_gevent_generic_callback0'


    def _watcher_ffi_set_priority(self, priority):
        # libuv has no concept of priority
        pass

    def _watcher_ffi_init(self, args):
        self._watcher_init(self.loop.ptr,
                           self._watcher,
                           *args)

    def _watcher_ffi_start(self):
        self._watcher_start(self._watcher, self._watcher_callback)

    def _watcher_ffi_stop(self):
        self._watcher_stop(self._watcher)

    def _watcher_ffi_ref(self):
        libuv.uv_ref(self._watcher)

    def _watcher_ffi_unref(self):
        libuv.uv_unref(self._watcher)

    def _get_ref(self):
        return libuv.uv_has_ref(self._watcher)

    def _set_ref(self, value):
        if value:
            self._watcher_ffi_ref()
        else:
            self._watcher_ffi_unref()

    ref = property(_get_ref, _set_ref)

    def feed(self, _revents, _callback, *_args):
        raise Exception("Not implemented")

class io(_base.IoMixin, watcher):
    _watcher_type = 'poll'
    _watcher_callback_name = '_gevent_poll_callback2'

    EVENT_MASK = libuv.UV_READABLE | libuv.UV_WRITABLE

    def __init__(self, loop, fd, events, ref=True, priority=None):
        super(io, self).__init__(loop, fd, events, ref=ref, priority=priority, _args=(fd,))
        self._fd = fd
        self._events = events

    def _get_fd(self):
        return self._fd

    @_base.not_while_active
    def _set_fd(self, fd):
        self._fd = fd
        self._watcher_ffi_init((fd,))

    def _get_events(self):
        return self._events

    @_base.not_while_active
    def _set_events(self, events):
        self._events = events

    def _watcher_ffi_start(self):
        self._watcher_start(self._watcher, self._events, self._watcher_callback)

class fork(object):
    # We'll have to implement this one completely manually

    def __init__(self, *args, **kwargs):
        pass

    def start(self, *args):
        pass

    def stop(self, *args):
        pass

class async(_base.AsyncMixin, watcher):

    def _watcher_ffi_init(self, args):
        pass

    def _watcher_ffi_start(self):
        self._watcher_init(self.loop.ptr, self._watcher, self._watcher_callback)

    def _watcher_ffi_stop(self):
        self._watcher_init(self.loop.ptr, self._watcher, ffi.NULL)

    def send(self):
        libuv.uv_async_send(self._watcher)

    @property
    def pending(self):
        return None