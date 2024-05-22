" File: source-locator.vim
" Author: Marius Gedminas <marius@gedmin.as>
" Version: 2.1
" Last Modified: 2024-05-22

if !exists('g:source_locator_prefixes')
    let g:source_locator_prefixes = ['src']
endif

if !exists('g:source_locator_suffixes')
    let g:source_locator_suffixes = ['.py']
endif

if has('python') || has('python3')

    let s:python = has('python3') ? 'python3' : 'python'
    exec s:python "import source_locator # see source_locator.py"

    function! LocateTest(line)
        exec s:python "source_locator.locate(vim.eval('a:line'), verbose=int(vim.eval('&verbose')))"
    endfunction

else " no Python, fall back to old logic

function! LocateTest(line)
    " The line is something like
    "    FAIL: ivija.reportgen.tests.test_pdr.doctest_PDRCoverPage
    " or
    "    Failure in test doctest_PDRCoverPage (ivija.reportgen.tests.test_pdr)
    " The thing to do is to jump to tag doctest_PDRCoverPage.  Also, when
    " the test is
    "    ivija.reportgen.tests.test_report_sections.TestReport.test_render
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

endif

function! LocateTestFromClipboard()
    call LocateTest(substitute(@*, '\f\zs\n\ze\f', '', 'g'))
endfunction

command! -bar -nargs=? LocateTest	call LocateTest(<q-args>)
command! -bar ClipboardTest		call LocateTestFromClipboard()
