source-locator.vim
------------------

Vim plugin to help me easily jump to the source location for an error.

Use case: I'm staring at an error (e.g. a Python traceback) in a console
or on a web page.  I tripple-click the line that contains the filename
and line number, copy it into the clipboard, then switch to Vim, and
hit a key (I use ``<F7>`` personally) that's mapped to ``:ClipboardTest``
in my ``.vimrc``.  This plugin extracts the filename and line number
from the clipboard and finds the right file (and line) for me.

The plugin attempts to handle mismatching directory layouts, so that you
can copy a line from a server's log file that complains about

  "/opt/mywebsite/lib/site-packages/python3.5/foo/bar/baz.py", line 42

and it'll be smart enough to realize the corresponding file in your source
checkout is named

  ./src/foo/bar/baz.py

In addition to filenames and line numbers, the plugin can attempt to
locate classes and functions by using your ctags database.


Requirements
------------

Vim with Python/Python3 support for the advanced logic (an older, dumber
pure-vimscript fallback is automatically available if your vim lacks
Python support).


Usage
-----

The following commands are defines:

:ClipboardTest
    jump to the location in the ``"*`` register

:LocateTest <filename>

:LocateTest <filename>:<lineno>

:LocateTest <tag>
    jump to the desired location


You can use these with ``:verbose`` to get more insight into what it's
doing, e.g. ::


    :2verbose ClipboardTest


Keybindings
-----------

By default there are no key bindings.

You may want to add a mapping in your ``~/.vimrc``.  I like ::

    map <F7> :ClipboardTest<CR>


Configuration
-------------

g:source_locator_prefixes
    Default: ['src']

    Path prefixes to try when the file is otherwise not found.

g:source_locator_suffixes
    Default: ['.py']

    Filename suffixes to try when the file is otherwise not found.


Bugs
----

- There's no :help


Copyright
---------

``source-locator.vim`` was written by Marius Gedminas <marius@gedmin.as>.
Licence: MIT.
