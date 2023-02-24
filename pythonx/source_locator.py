"""
" HACK to make this file source'able by vim as well as importable by Python:
exe has('python3') ? 'py3' : 'py' 'import sys; sys.modules.pop("source_locator"); import source_locator'
finish
"""
# the second half of source-locator.vim
import vim
import os
import re


patterns = [
    # unittest error format
    re.compile(r'^(?:ERROR|FAIL): (?P<tag>[a-zA-Z_0-9]+) [(](?P<module_class>[a-zA-Z0-9_.]*[.][a-zA-Z_0-9]+)[)]'),
    # svn status output
    re.compile(r'^[A-Z?]      (?P<filename>[^ ]+)$'),
    # py.test encloses the filename in square brackets sometimes,
    re.compile(r'\[(?P<filename>[^: ]+):(?P<lineno>\d+)]'),
    # py.test names tests like this
    re.compile(r'(?P<filename>[^: ]+)::(?P<tag>test[a-zA-Z_0-9]+)'),
    # pdb puts the line number in parentheses,
    re.compile(r'(?P<filename>[^: ]+)[(](?P<lineno>\d+)[)][a-zA-Z_][a-zA-Z_0-9]+[(][)]'),
    # oesjskit tracebacks from firefox
    # E           ()@http://localhost:56166/test/test_Main.js:346
    re.compile(r'http://[a-z0-9.]*:([0-9]+?)/(?P<filename>[^: ]+):(?P<lineno>\d+)]'),
    # standard compiler error message format
    re.compile(r'(?P<filename>[^: ]+):(?P<lineno>\d+)'),
    # grep output
    re.compile(r'(?P<filename>[^: ]+):'),
    # tracebacks (the variant with 'lineno N' comes from tracemalloc)
    re.compile(r'"(?P<filename>[^: ]+)", line(?:no)? (?P<lineno>\d+)'),
    re.compile(r'File (?P<filename>[^: ]+), line(?:no)? (?P<lineno>\d+)'),
    # filename (lines 123-456)
    re.compile(r'(?P<filename>[^ ]+) [(]lines (?P<lineno>\d+)-\d+[)]'),
    # anything that looks like a unit test name (unittest style)
    re.compile(r'(?P<tag>(?:doc)?test[a-zA-Z0-9_]*) [(](?P<module_class>[a-zA-Z0-9_.]*[.][a-zA-Z_0-9]+)[)]'),
    # json record with {..."path": "filename", "line": NNN...}
    re.compile(r'"(?P<filename>[^ "]+)", "line": (?P<lineno>\d+)'),
    # anything that looks like a filename
    re.compile(r'(?P<filename>[-_a-zA-Z0-9/.]{3,})'),
    # anything that looks like a package/module
    re.compile(r'(^|[^/])(?P<module>[a-zA-Z0-9_.]{3,})($|[^/])'),
    # anything that looks like a unit test name (ivija test runner style)
    re.compile(r'in test (?P<tag>[a-zA-Z_0-9]+)'),
    re.compile(r'(?P<tag>[a-zA-Z0-9_.]*[.]Test[a-zA-Z_0-9]+[.][a-zA-Z_0-9]+)'),
    re.compile(r'(?P<tag>[a-zA-Z0-9_.]*[.][a-zA-Z_0-9]+)'),
    re.compile(r'(?P<tag>[a-zA-Z0-9_]*test[a-zA-Z_0-9]+)'),
    # anything that looks like a tag
    re.compile(r'(?P<tag>[a-zA-Z0-9_.]+)'),
]


def iter_matches(line, verbose=False):
    for pattern in patterns:
        if verbose > 3:
            print("TRYING %s" % pattern)
        for match in pattern.finditer(line):
            yield match.groupdict()


def get_file_prefixes():
    # Filename search logic will take /path/to/filename and try
    #   prefix1/path/to/filename
    #   prefix2/path/to/filename
    #   prefix1/to/filename
    #   prefix2/to/filename
    #   prefix1/filename
    #   prefix2/filename
    # for this reason the first prefix should really be ''.
    prefixes = vim.eval('g:source_locator_prefixes')
    if not isinstance(prefixes, list):
        prefixes = prefixes.split(',')
    return [''] + prefixes


def get_file_suffixes():
    suffixes = vim.eval('g:source_locator_suffixes')
    if not isinstance(suffixes, list):
        suffixes = suffixes.split(',')
    return [''] + suffixes


def detoxify(filename, verbose=False):
    parts = filename.split('/')
    if '.tox' in parts:
        idx = parts.index('.tox')
        # .tox/pyXY/lib/pythonX.Y/site-packages/
        if parts[idx + 4:idx + 5] == ['site-packages']:
            candidate = '/'.join(parts[idx + 5:])
            if verbose:
                print('.tox detected, trying %s', candidate)
            yield candidate
        # .tox/pypyX/site-packages/
        if parts[idx + 2:idx + 3] == ['site-packages']:
            candidate = '/'.join(parts[idx + 3:])
            if verbose:
                print('.tox detected, trying %s', candidate)
            yield candidate
    yield filename


def locate_file_detoxified(filename, verbose=False):
    for candidate in detoxify(filename, verbose=verbose):
        candidate = locate_file(candidate, verbose=verbose)
        if candidate:
            return candidate
    return None


def locate_file(filename, verbose=False):
    if verbose:
        print('looking for file %s' % filename)
    file_prefixes = get_file_prefixes()
    file_suffixes = get_file_suffixes()
    while filename:
        for prefix in file_prefixes:
            for suffix in file_suffixes:
                new_filename = os.path.join(prefix, filename + suffix)
                if verbose > 2:
                    print('  checking %s' % new_filename)
                if os.path.exists(new_filename):
                    return new_filename
        if '/' not in filename:
            break
        filename = filename.split('/', 1)[1]
        if verbose:
            print('  trying %s' % filename)
    return None


def locate_module(module, verbose=False):
    if verbose:
        print('looking for module %s' % module)
    filename = locate_file(module.replace('.', '/') + '.py')
    if not filename:
        filename = locate_file(module.replace('.', '/') + '/__init__.py')
    return filename


def tag_exists(tag_name, verbose=False, filename=None):
    if verbose:
        print('looking for tag %s' % tag_name)
    try:
        tags = vim.eval("taglist('^%s$')" % tag_name)
        if tags and filename:
            found_in = tags[0]['filename']
            if not os.path.samefile(found_in, filename):
                if verbose:
                    print('found tag in %s but wanted %s, ignoring' % (found_in, filename))
                return False
        return bool(tags)
    except vim.error:
        return False


def quote(s):
    return s.replace('\\', '\\\\').replace(' ', '\\ ')


def locate_command(line, verbose=False, e_command='e', tag_command='Tag', tjump_command='tjump'):
    for match in iter_matches(line, verbose=verbose):
        filename = match.get('filename')
        lineno = match.get('lineno')
        tag = match.get('tag')
        module_class = match.get('module_class')
        if verbose > 1:
            print('MATCH: {}'.format(
                ' '.join('{}={}'.format(k, v) for k, v in sorted(match.items()))))
        if tag and module_class:
            # Optional integration with https://github.com/mgedmin/pytag.vim
            try:
                import smart_tag
            except ImportError:
                pass
            else:
                finder = smart_tag.SmartTagFinder()
                full_tag = '%s.%s' % (module_class, tag)
                if verbose:
                    print('looking for tag %s' % full_tag)
                t, n, i = finder.find_best_tag(full_tag)
                if t:
                    return '%s %s' % (tag_command, full_tag)
        if filename:
            filename = locate_file_detoxified(filename, verbose=verbose)
        if not filename:
            module = match.get('module')
            if module:
                filename = locate_module(module, verbose=verbose)
        if filename and lineno:
            if os.path.samefile(filename, vim.current.buffer.name):
                # same file optimizatin: avoid re-reading, just jump to the right line
                return ':%d' % int(lineno)
            else:
                return '%s +%s %s' % (e_command, lineno, quote(filename))
        if tag:
            found = tag_exists(tag, verbose=verbose, filename=filename)
            if not found and '.' in tag:
                tag = tag.rsplit('.', 1)[-1]
                found = tag_exists(tag, verbose=verbose, filename=filename)
            if found:
                return '%s %s' % (tjump_command, quote(tag))
        if filename:
            return '%s %s' % (e_command, quote(filename))
    return None


def locate(line, verbose=False, e_command='e', tag_command='Tag', tjump_command='tjump', command_prefix=''):
    line = line.strip().replace('\\', '/')
    try:
        cmd = locate_command(line, verbose=verbose,
                             e_command=command_prefix + e_command,
                             tag_command=command_prefix + tag_command,
                             tjump_command=command_prefix + tjump_command)
        if cmd:
            print(cmd)
            try:
                vim.command(cmd)
            except vim.error:
                pass
        else:
            print("Don't know how to find %s" % line)
    except KeyboardInterrupt:
        pass
