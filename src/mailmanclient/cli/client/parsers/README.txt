Mailman Shell Parsers
**********************

This directory consists of the various parsers that
have been built for use with the mailman shell. The shell
parser has been built in such a way that each command has
a different and independent parser, so that adding new commands
can be done flexibly and easily, without worrying about the
existing code.

The `show` command
=================

The command to display the mailman objects

Tokens
------
::

    SHOW   : 'show'
    SCOPE  : '(user|domain|list)s?'
    WHERE  : 'where'
    OP     : '=|in|like'
    AND    : 'and'
    STRING : '`([a-zA-Z0-9_@\.\*\-\$ ]*)`'

Grammar
-------
::

    S : SHOW SCOPE FILTER ;
    FILTER : WHERE EXP | ;
    EXP : STRING OP STRING CONJ ;
    CONJ : AND EXP | ;

The `create` command
====================

The commands to create mailman objects

Tokens
------
::

    CREATE : 'create'
    SCOPE  : 'user|domain|list'
    WITH   : 'with'
    AND    : 'and'
    STRING : '`([a-zA-Z0-9_@\.\*\-\$ ]*)`'

Grammar
-------
::

    S : CREATE SCOPE WITH EXP ;
    EXP : STRING "=" STRING CONJ ;
    CONJ : AND EXP | ;

The `delete` command
====================

The commands to delete mailman objects

Tokens
------
::

    DELETE : 'delete'
    SCOPE  : '(user|domain|list)s?'
    WHERE  : 'where'
    OP     : '=|in|like'
    AND    : 'and'
    STRING : '`([a-zA-Z0-9_@\.\*\-\$ ]*)`'

Grammar
-------
::

    S : DELETE SCOPE FILTER ;
    FILTER : WHERE EXP | ;
    EXP : STRING OP STRING CONJ ;
    CONJ : AND EXP | ;

The `subscribe` Command
=====================

The commands to subscribe a list of users to a mailing lists

Tokens
------
::

    SUBSCRIBE  : 'subscribe'
    USER       : '(user)?'
    TO         : 'to'
    STRING : '`([a-zA-Z0-9_@\.\*\-\$ ]*)`'

Grammar
-------
::

    S : SUBSCRIBE USER USERLIST TO STRING ;
    USERLIST : STRING NEXT ;
    NEXT : USERLIST | ;

The `unsubscribe` Command
=========================

The commands to unsubscribe a list of users from a mailing lists

Tokens
------
::

    UNSUBSCRIBE : 'unsubscribe'
    USER        : '(user)?'
    FROM        : 'from'
    STRING      : '`([a-zA-Z0-9_@\.\*\-\$ ]*)`'

Grammar
-------
::

    S : UNSUBSCRIBE USER USERLIST TO STRING ;
    USERLIST : STRING NEXT ;
    NEXT : USERLIST | ;

The `unset` command
===================

Command to unset a shell variable

Tokens
------
::

    UNSET : 'unset'
    STRING      : '`([a-zA-Z0-9_@\.\*\-\$ ]*)`'

Grammar
-------
::

    S : UNSET STRING ;

The `set` Command
=================

Command to set a shell variable

Tokens
------
::

    SET : 'set'
    STRING      : '`([a-zA-Z0-9_@\.\*\-\$ ]*)`'

Grammar
-------
::

    S : SET STRING "=" STRING ;

The `update` command
====================

Command to update a preference

Tokens
------
::

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
::

    S : UPDATE PREFERENCE STRING TO STRING E ;
    E : GLOBALLY | FOR DOMAIN WITH EXP ;
    EXP : STRING "=" STRING CONJ ;
    CONJ : AND EXP | ;
