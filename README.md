# symbol_version
A helper for library maintainers to use symbol versioning

## Why use symbol versioning?
The main reason is to be able to keep the library [ABI](https://en.wikipedia.org/wiki/Application_binary_interface) stable.

If a library is intended to be used for a long time, it will need updates for
eventual bug fixes and/or improvement.
This can lead to changes in the [API](https://en.wikipedia.org/wiki/Application_programming_interface) and, in the worst case, changes to the
[ABI](https://en.wikipedia.org/wiki/Application_binary_interface).

Using symbol versioning, it is possible to make compatible changes and keep the
applications working without recompiling.
If incompatible changes were made (breaking the [ABI](https://en.wikipedia.org/wiki/Application_binary_interface)), symbol versioning allows both
incompatible versions to live in the same system without conflict.
And even more uncommon situations, like an application to be linked to
different (incompatible) versions of the same library.

For more information, I strongly recommend reading:
* [How to write shared libraries](https://www.akkadia.org/drepper/dsohowto.pdf), by Ulrich Drepper

## How to add symbol versioning to my library?

Adding version information to the symbols is easy. Keeping the [ABI](https://en.wikipedia.org/wiki/Application_binary_interface) stable, unfortunately, is not. This project intends to help in the first part.

To add version information to symbols of a library, one can use version scripts (in Linux).
Version scripts are files used by linkers to map symbols to a given version.
It contains the symbols exported by the library grouped by the releases where they were introduced. For example:
```
LIB_EXAMPLE_1_0_0
{
	global:
		symbol;
		another_symbol;
	local:
		*;
};
```
In this example, the release ``LIB_EXAMPLE_1_0_0`` introduces the symbols ``symbol`` and ``another_symbol``.
The ``*`` wildcard in ``local`` catches all other symbols, meaning only ``symbol`` and ``another_symbol`` are globally exported as part of the library [API](https://en.wikipedia.org/wiki/Application_programming_interface).

If a compatible change is made, it would introduce a new release, like:
```
LIB_EXAMPLE_1_1_0
{
	global:
		new_symbol;
} LIB_EXAMPLE_1_0_0;

LIB_EXAMPLE_1_0_0
{
	global:
		symbol;
		another_symbol;
	local:
		*;
};
```
The new release ``LIB_EXAMPLE_1_1_0`` introduces the symbol ``new_symbol``.
The ``*`` wildcard should be only in one version, usually in the oldest version.
The ``} LIB_EXAMPLE_1_0_0;`` part in the end of the new release means the new release depends on the old release.

Suppose a new incompatible version ``LIB_EXAMPLE_2_0_0`` released after ``LIB_EXAMPLE_1_1_0``. Its map would look like:
```
LIB_EXAMPLE_2_0_0
{
	global:
		a_newer_symbol;
		another_symbol;
		new_symbol;
	local:
		*;
};
```
The symbol ``symbol`` was removed (and that is why it was incompatible). And a new symbol was introduced, ``a_newer_symbol``.

Note that all global symbols in all releases were merged in a unique new release.

## symbol_version.py script usage
This project delivers only a script, ``symbol_version.py``. This is my first project in python, so feel free to point out ways to improve it.

Both available sub-commands (``update`` and ``new``) expect a list of symbols given in stdin. The list of symbols are words separated by non-alphanumeric characters (matches with the regular expression ``[a-zA-Z0-9_]+``). For example:
```
symbol, another, one_more
```
and
```
symbol
another
one_more
```
are valid inputs.
### tl;dr
``$ python symbol_version.py update -s lib_example.map < symbols_list``

or (setting an output):
``$ python symbol_version.py update -s lib_example.map -o new.map < symbols_list``

or :
``$ cat symbols_list | ./symbol_version.py update -s lib_example.map -o new.map``

or (to create a new map):
``$ cat symbols_list | ./symbol_version.py new -r lib_example_1_0_0 -o new.map``

### Long version


Runing  ``$ python symbol_version.py -h`` will give:
```
usage: symbol_version.py [-h] {update,new} ...

Helper tools for linker version script maintenance

optional arguments:
  -h, --help    show this help message and exit

Subcommands:
  Valid subcommands:

  {update,new}  These subcommands have their own set of options
    update      Update the map file
    new         Create a new map file

Call a subcommand passing '-h' to see its specific options
```
There are two subcommands, ``update`` and ``new``
Running ``$ python symbol_script.py update -h`` will give:
```
usage: symbol_version.py update [-h] [-o OUT] [-i INPUT] [-d]
                                [--verbosity {quiet,error,warning,info,debug} | --quiet | --debug]
                                [-c] (-a | -r | -s)
                                file

positional arguments:
  file                  The map file being updated

optional arguments:
  -h, --help            show this help message and exit
  -o OUT, --out OUT     Output file (defaults to stdout)
  -i INPUT, --in INPUT  Read from a file instead of stdio
  -d, --dry             Do everything, but do not modify the files
  --verbosity {quiet,error,warning,info,debug}
                        Set the program verbosity
  --quiet               Makes the program quiet
  --debug               Makes the program print debug info
  -c, --care            Do not continue if the ABI would be broken
  -a, --add             Adds the symbols to the map file.
  -r, --remove          Remove the symbols from the map file. This breaks the
                        ABI.
  -s, --symbols         Compare the given symbol list with the current map
                        file and update accordingly. May break the ABI.

A list of symbols is expected as the input. If a file is provided with '-i',
the symbols are read from the given file. Otherwise the symbols are read from
stdin.
```
Running  ``$ python symbol_script.py new -h`` will give:
```
usage: symbol_version.py new [-h] [-o OUT] [-i INPUT] [-d]
                             [--verbosity {quiet,error,warning,info,debug} | --quiet | --debug]
                             [-n NAME] [-v VERSION] [-r RELEASE]

optional arguments:
  -h, --help            show this help message and exit
  -o OUT, --out OUT     Output file (defaults to stdout)
  -i INPUT, --in INPUT  Read from a file instead of stdio
  -d, --dry             Do everything, but do not modify the files
  --verbosity {quiet,error,warning,info,debug}
                        Set the program verbosity
  --quiet               Makes the program quiet
  --debug               Makes the program print debug info
  -n NAME, --name NAME  The name of the library (e.g. libx)
  -v VERSION, --version VERSION
                        The release version (e.g. 1_0_0)
  -r RELEASE, --release RELEASE
                        The full name of the release to be used (e.g.
                        LIBX_1_0_0)

A list of symbols is expected as the input. If a file is provided with '-i',
the symbols are read from the given file. Otherwise the symbols are read from
stdin.
```

