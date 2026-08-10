" Set defaults for option values
if !exists('g:source_locator_prefixes')
  let g:source_locator_prefixes = ['src']
endif
if !exists('g:source_locator_suffixes')
  let g:source_locator_suffixes = ['.py']
endif
if !exists('g:source_locator_prefer_clipboard')
  if &clipboard =~ 'unnamedplus'
    let g:source_locator_prefer_clipboard = 1
  else
    let g:source_locator_prefer_clipboard = 0
  endif
endif

" Make sure the Python code is imported
if has('pythonx')
  pyx import source_locator
endif

function source_locator#go(line)
  if has('pythonx')
    pyx source_locator.locate(vim.eval('a:line'), verbose=int(vim.eval('&verbose')))
  else
    call source_locator#go_fallback(a:line)
  endif
endfunction

function source_locator#go_fallback(line)
  " no Python, fall back to old logic
  " do not expect to have a good time, but maybe it's better than nothing

  " The line is something like
  "   FAIL: ivija.reportgen.tests.test_pdr.doctest_PDRCoverPage
  " or
  "   Failure in test doctest_PDRCoverPage (ivija.reportgen.tests.test_pdr)
  " The thing to do is to jump to tag doctest_PDRCoverPage.  Also, when
  " the test is
  "   ivija.reportgen.tests.test_report_sections.TestReport.test_render
  " try jumping to TestReport.test_render first, to avoid ambiguities

  let l:m = matchlist(a:line, '\([^: ]\+\):\(\d\+\)')
  if l:m != []
    let fn = l:m[1]
    let row = l:m[2]
    exec "e +" . l:row . " " . l:fn
    return
  endif
  let l:m = matchlist(a:line, '"\([^"]\+\)", line \(\d\+\)')
  if l:m != []
    let fn = l:m[1]
    let row = l:m[2]
    exec "e +" . l:row . " " . l:fn
    return
  endif
  let l:m = matchlist(a:line, 'File \([^"]\+\), line \(\d\+\)')
  if l:m != []
    let fn = l:m[1]
    let row = l:m[2]
    exec "e +" . l:row . " " . l:fn
    return
  endif
  let l:m = matchlist(a:line, '\([-_a-z0-9/.]\+\)')
  if l:m != []
    let fn = l:m[1]
    if filereadable(fn)
      exec "e " . l:fn
      return
    endif
    let fn = 'src/' . fn
    if filereadable(fn)
      exec "e " . l:fn
      return
    endif
  endif
  let l:m = matchlist(a:line, '[a-zA-Z0-9_.]*[.]\(Test[a-zA-Z_0-9]\+[.][a-zA-Z_0-9]\+\)')
  if l:m == []
    let l:m = matchlist(a:line, '[a-zA-Z0-9_.]*[.]\([a-zA-Z_0-9]\+\)')
  endif
  if l:m == []
    let l:m = matchlist(a:line, 'in test \([a-zA-Z_0-9]\+\)')
  endif
  if l:m == []
    let l:m = matchlist(a:line, '\([a-zA-Z_0-9]*test[a-zA-Z_0-9]\+\)')
  endif
  if l:m == []
    let l:m = matchlist(a:line, '^\([a-zA-Z_0-9]\+\)$')
  endif
  if l:m == []
    echo "Don't know how to find" a:line
    return
  endif
  let l:testname = l:m[1]
  if taglist('^'.l:testname.'$') == [] && stridx(l:testname, '.') != -1
    let l:testname = l:testname[stridx(l:testname, '.') + 1:]
  endif
  exec "tjump" l:testname
endfunction

function source_locator#clipboard()
  " Since I can never remember which is which:
  "   * is the primary selection register
  "   + is the clipboard register
  if g:source_locator_prefer_clipboard
    let clipboard_text = @+ ?? @*
  else
    let clipboard_text = @* ?? @+
  endif
  " Sometimes filenames get hard-wrapped, so delete any newlines between two
  " filename characters
  return substitute(clipboard_text, '\f\zs\n\ze\f', '', 'g')
endfunction

function source_locator#go_clipboard()
  call source_locator#go(source_locator#clipboard())
endfunction

" Intended for a mapping like
" au FileType qf map <buffer> gF <Cmd>call source_locator#go_quickfix()<CR>
function source_locator#go_quickfix()
  if has('pythonx')
    pyx source_locator.locate(vim.current.line, command_prefix='wincmd p | ')
  else
    let line = getline('.')
    wincmd p
    call source_locator#go_fallback(line)
  endif
endfunction
