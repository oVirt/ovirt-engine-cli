
# parser_tab.py
# This file is automatically generated. Do not edit.
_tabversion = '3.2'

_lr_method = 'LALR'

_lr_signature = '[2`\x88\xc7\xdc\x98^\xc4\x8e\xf3\xfc9\x9a\r\xc2'
    
_lr_action_items = {'GT':([2,3,9,10,11,12,13,17,18,19,20,21,25,28,29,30,31,32,33,34,35,36,37,38,39,42,44,45,46,],[-6,-36,-10,-8,-36,-7,-11,-9,23,-36,-12,-13,23,-21,-20,-14,-15,-17,-18,-36,-19,-31,-32,-25,-24,-22,-26,-23,-16,]),'WORD':([0,1,2,3,4,6,7,8,9,10,11,12,13,15,16,17,19,22,23,26,27,34,51,],[2,-34,-6,9,-5,-1,-35,2,-10,-8,9,-7,-11,-33,-2,-9,32,-4,36,36,36,32,-3,]),'STRING':([2,3,9,10,11,12,13,17,19,23,26,27,34,],[-6,13,-10,-8,13,-7,-11,-9,33,37,37,37,33,]),'HEREDOC':([2,3,9,10,11,12,13,17,18,19,20,21,25,28,29,30,31,32,33,34,35,36,37,38,39,40,42,43,44,45,46,50,],[-6,-36,-10,-8,-36,-7,-11,-9,-36,-36,-12,-13,-36,-21,-20,-14,-15,-17,-18,-36,-19,-31,-32,-25,-24,48,-22,-28,-26,-23,-16,-27,]),'=':([19,],[34,]),'NEWLINE':([0,1,2,3,4,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,25,28,29,30,31,32,33,34,35,36,37,38,39,40,42,43,44,45,46,47,48,49,50,51,],[1,-34,-6,-36,-5,-1,15,1,-10,-8,-36,-7,-11,1,-33,-2,-9,-36,-36,-12,-13,-4,-36,-21,-20,-14,-15,-17,-18,-36,-19,-31,-32,-25,-24,-36,-22,-28,-26,-23,-16,1,-29,-30,-27,-3,]),'LT':([2,3,9,10,11,12,13,17,18,19,20,21,25,28,29,30,31,32,33,34,35,36,37,38,39,42,44,45,46,],[-6,-36,-10,-8,-36,-7,-11,-9,27,-36,-12,-13,27,-21,-20,-14,-15,-17,-18,-36,-19,-31,-32,-25,-24,-22,-26,-23,-16,]),'PIPE':([2,3,9,10,11,12,13,17,18,19,20,21,25,28,29,30,31,32,33,34,35,36,37,38,39,42,44,45,46,],[-6,-36,-10,-8,-36,-7,-11,-9,-36,-36,-12,-13,41,-21,-20,-14,-15,-17,-18,-36,-19,-31,-32,-25,-24,-22,-26,-23,-16,]),'BANG':([0,1,4,6,7,8,15,16,22,51,],[5,-34,-5,-1,-35,5,-33,-2,-4,-3,]),'SHELL':([5,41,],[14,50,]),'OPTION':([2,3,9,10,11,12,13,17,18,19,20,21,30,31,32,33,34,35,46,],[-6,-36,-10,-8,19,-7,-11,-9,19,-36,-12,-13,-14,-15,-17,-18,-36,-19,-16,]),'MARKER':([24,],[39,]),'LTLT':([2,3,9,10,11,12,13,17,18,19,20,21,25,28,29,30,31,32,33,34,35,36,37,38,39,42,44,45,46,],[-6,-36,-10,-8,-36,-7,-11,-9,24,-36,-12,-13,24,-21,-20,-14,-15,-17,-18,-36,-19,-31,-32,-25,-24,-22,-26,-23,-16,]),';':([0,1,2,3,4,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,25,28,29,30,31,32,33,34,35,36,37,38,39,40,42,43,44,45,46,47,48,49,50,51,],[7,-34,-6,-36,-5,-1,-35,7,-10,-8,-36,-7,-11,7,-33,-2,-9,-36,-36,-12,-13,-4,-36,-21,-20,-14,-15,-17,-18,-36,-19,-31,-32,-25,-24,-36,-22,-28,-26,-23,-16,7,-29,-30,-27,-3,]),'GTGT':([2,3,9,10,11,12,13,17,18,19,20,21,25,28,29,30,31,32,33,34,35,36,37,38,39,42,44,45,46,],[-6,-36,-10,-8,-36,-7,-11,-9,26,-36,-12,-13,26,-21,-20,-14,-15,-17,-18,-36,-19,-31,-32,-25,-24,-22,-26,-23,-16,]),'$end':([1,4,6,7,8,15,16,22,51,],[-34,-5,-1,-35,0,-33,-2,-4,-3,]),}

_lr_action = { }
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = { }
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'option_value':([19,34,],[31,46,]),'name':([0,8,],[3,3,]),'redirections':([18,],[25,]),'heredoc':([40,],[47,]),'argument':([3,11,],[10,17,]),'eol':([0,8,14,47,],[4,4,22,51,]),'option_list':([11,],[18,]),'command':([0,8,],[6,16,]),'argument_list':([3,],[11,]),'file':([23,26,27,],[38,44,45,]),'pipeline':([25,],[40,]),'main':([0,],[8,]),'redirection':([18,25,],[28,42,]),'empty':([3,11,18,19,25,34,40,],[12,20,29,35,43,35,49,]),'option':([11,18,],[21,30,]),}

_lr_goto = { }
for _k, _v in _lr_goto_items.items():
   for _x,_y in zip(_v[0],_v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = { }
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> main","S'",1,None,None,None),
  ('main -> command','main',1,'p_main','/home/mpastern/Coding/oVirt/ovirt-engine-cli/src/cli/parser.py',110),
  ('main -> main command','main',2,'p_main','/home/mpastern/Coding/oVirt/ovirt-engine-cli/src/cli/parser.py',111),
  ('command -> name argument_list option_list redirections pipeline heredoc eol','command',7,'p_command','/home/mpastern/Coding/oVirt/ovirt-engine-cli/src/cli/parser.py',121),
  ('command -> BANG SHELL eol','command',3,'p_command','/home/mpastern/Coding/oVirt/ovirt-engine-cli/src/cli/parser.py',122),
  ('command -> eol','command',1,'p_command','/home/mpastern/Coding/oVirt/ovirt-engine-cli/src/cli/parser.py',123),
  ('name -> WORD','name',1,'p_name','/home/mpastern/Coding/oVirt/ovirt-engine-cli/src/cli/parser.py',138),
  ('argument_list -> empty','argument_list',1,'p_argument_list','/home/mpastern/Coding/oVirt/ovirt-engine-cli/src/cli/parser.py',142),
  ('argument_list -> argument','argument_list',1,'p_argument_list','/home/mpastern/Coding/oVirt/ovirt-engine-cli/src/cli/parser.py',143),
  ('argument_list -> argument_list argument','argument_list',2,'p_argument_list','/home/mpastern/Coding/oVirt/ovirt-engine-cli/src/cli/parser.py',144),
  ('argument -> WORD','argument',1,'p_argument','/home/mpastern/Coding/oVirt/ovirt-engine-cli/src/cli/parser.py',155),
  ('argument -> STRING','argument',1,'p_argument','/home/mpastern/Coding/oVirt/ovirt-engine-cli/src/cli/parser.py',156),
  ('option_list -> empty','option_list',1,'p_option_list','/home/mpastern/Coding/oVirt/ovirt-engine-cli/src/cli/parser.py',161),
  ('option_list -> option','option_list',1,'p_option_list','/home/mpastern/Coding/oVirt/ovirt-engine-cli/src/cli/parser.py',162),
  ('option_list -> option_list option','option_list',2,'p_option_list','/home/mpastern/Coding/oVirt/ovirt-engine-cli/src/cli/parser.py',163),
  ('option -> OPTION option_value','option',2,'p_option','/home/mpastern/Coding/oVirt/ovirt-engine-cli/src/cli/parser.py',175),
  ('option -> OPTION = option_value','option',3,'p_option','/home/mpastern/Coding/oVirt/ovirt-engine-cli/src/cli/parser.py',176),
  ('option_value -> WORD','option_value',1,'p_option_value','/home/mpastern/Coding/oVirt/ovirt-engine-cli/src/cli/parser.py',184),
  ('option_value -> STRING','option_value',1,'p_option_value','/home/mpastern/Coding/oVirt/ovirt-engine-cli/src/cli/parser.py',185),
  ('option_value -> empty','option_value',1,'p_option_value','/home/mpastern/Coding/oVirt/ovirt-engine-cli/src/cli/parser.py',186),
  ('redirections -> empty','redirections',1,'p_redirections','/home/mpastern/Coding/oVirt/ovirt-engine-cli/src/cli/parser.py',191),
  ('redirections -> redirection','redirections',1,'p_redirections','/home/mpastern/Coding/oVirt/ovirt-engine-cli/src/cli/parser.py',192),
  ('redirections -> redirections redirection','redirections',2,'p_redirections','/home/mpastern/Coding/oVirt/ovirt-engine-cli/src/cli/parser.py',193),
  ('redirection -> LT file','redirection',2,'p_redirection','/home/mpastern/Coding/oVirt/ovirt-engine-cli/src/cli/parser.py',204),
  ('redirection -> LTLT MARKER','redirection',2,'p_redirection','/home/mpastern/Coding/oVirt/ovirt-engine-cli/src/cli/parser.py',205),
  ('redirection -> GT file','redirection',2,'p_redirection','/home/mpastern/Coding/oVirt/ovirt-engine-cli/src/cli/parser.py',206),
  ('redirection -> GTGT file','redirection',2,'p_redirection','/home/mpastern/Coding/oVirt/ovirt-engine-cli/src/cli/parser.py',207),
  ('pipeline -> PIPE SHELL','pipeline',2,'p_pipeline','/home/mpastern/Coding/oVirt/ovirt-engine-cli/src/cli/parser.py',212),
  ('pipeline -> empty','pipeline',1,'p_pipeline','/home/mpastern/Coding/oVirt/ovirt-engine-cli/src/cli/parser.py',213),
  ('heredoc -> HEREDOC','heredoc',1,'p_heredoc','/home/mpastern/Coding/oVirt/ovirt-engine-cli/src/cli/parser.py',219),
  ('heredoc -> empty','heredoc',1,'p_heredoc','/home/mpastern/Coding/oVirt/ovirt-engine-cli/src/cli/parser.py',220),
  ('file -> WORD','file',1,'p_file','/home/mpastern/Coding/oVirt/ovirt-engine-cli/src/cli/parser.py',225),
  ('file -> STRING','file',1,'p_file','/home/mpastern/Coding/oVirt/ovirt-engine-cli/src/cli/parser.py',226),
  ('eol -> ; NEWLINE','eol',2,'p_eol','/home/mpastern/Coding/oVirt/ovirt-engine-cli/src/cli/parser.py',231),
  ('eol -> NEWLINE','eol',1,'p_eol','/home/mpastern/Coding/oVirt/ovirt-engine-cli/src/cli/parser.py',232),
  ('eol -> ;','eol',1,'p_eol','/home/mpastern/Coding/oVirt/ovirt-engine-cli/src/cli/parser.py',233),
  ('empty -> <empty>','empty',0,'p_empty','/home/mpastern/Coding/oVirt/ovirt-engine-cli/src/cli/parser.py',238),
]
