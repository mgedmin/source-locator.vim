" File: source-locator.vim
" Author: Marius Gedminas <marius@gedmin.as>
" Version: 3.0
" Last Modified: 2026-05-29

" Old function names for backwards compatibility
function! LocateTest(line)
  call source_locator#go(a:line)
endfunction

function! LocateTestFromClipboard()
  call source_locator#go_clipboard()
endfunction

command! -bar -nargs=? LocateTest	call source_locator#go(<q-args>)
command! -bar ClipboardTest		call source_locator#go_clipboard()
