Mailman Shell Parsers
=====================

This directory consists of the various parsers that
have been built for use with the mailman shell. The shell
parser has been built in such a way that each command has
a different and independent parser, so that adding new commands
can be done flexibly and easily, without worrying about the
existing code.

Here is the list of commands along with the grammars used for 
parsing them

====
show
====

Tokens
------
SHOW   : 'show'
SCOPE  : '(user|domain|list)s?'
WHERE  : 'where'
OP     : '=|in|like'
AND    : 'and'
STRING : '`([a-zA-Z0-9_@\.\*\-\$ ]*)`'

Grammar
-------

S : SHOW SCOPE FILTER ;
FILTER : WHERE EXP | ;
EXP : STRING OP STRING CONJ ;
CONJ : AND EXP | ;

======
Create
=======

Tokens
------
CREATE : 'create'
SCOPE  : 'user|domain|list'
WITH   : 'with'
AND    : 'and'
STRING : '`([a-zA-Z0-9_@\.\*\-\$ ]*)`'

Grammar
-------

S : CREATE SCOPE WITH EXP ;
EXP : STRING "=" STRING CONJ ;
CONJ : AND EXP | ;

=======
delete
=======

Tokens
------
DELETE : 'delete'
SCOPE  : '(user|domain|list)s?'
WHERE  : 'where'
OP     : '=|in|like'
AND    : 'and'
STRING : '`([a-zA-Z0-9_@\.\*\-\$ ]*)`'

Grammar
-------

S : DELETE SCOPE FILTER ;
FILTER : WHERE EXP | ;
EXP : STRING OP STRING CONJ ;
CONJ : AND EXP | ;

=========
subscribe
=========

Tokens
------
SUBSCRIBE  : 'subscribe'
USER       : '(user)?'
TO         : 'to'
STRING : '`([a-zA-Z0-9_@\.\*\-\$ ]*)`'

Grammar
-------

S : SUBSCRIBE USER USERLIST TO STRING ;
USERLIST : STRING NEXT ;
NEXT : USERLIST | ;


=============
unsubscribe
=============

Tokens
------
UNSUBSCRIBE : 'unsubscribe'
USER        : '(user)?'
FROM        : 'from'
STRING      : '`([a-zA-Z0-9_@\.\*\-\$ ]*)`'

Grammar
-------

S : UNSUBSCRIBE USER USERLIST TO STRING ;
USERLIST : STRING NEXT ;
NEXT : USERLIST | ;

======
unset
======

Tokens
------
UNSET : 'unset'
STRING      : '`([a-zA-Z0-9_@\.\*\-\$ ]*)`'

Grammar
-------

S : UNSET STRING ;

====
set
====

Tokens
------
SET : 'set'
STRING      : '`([a-zA-Z0-9_@\.\*\-\$ ]*)`'

Grammar
-------

S : SET STRING "=" STRING ;

=======
update
=======

Tokens
------

UPDATE      : 'update'
PREFERENCE  : 'preference'
STRING      : '`([a-zA-Z0-9_@\.\*\-\$ ]*)`'
TO          : 'to'
WITH        : 'with'
AND         : 'and'
FOR         : 'for'
GLOBALLY    : 'globally'
DOMAIN      : 'user|address|member'

Grammar
-------
S : UPDATE PREFERENCE STRING TO STRING E ;
E : GLOBALLY | FOR DOMAIN WITH EXP ;
EXP : STRING "=" STRING CONJ ;
CONJ : AND EXP | ;
