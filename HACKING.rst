=================
Coding Standards
=================
OpenCAFE standards are intended to allow flexability in solving coding issues,
while maintaining uniformity and overall code quality.


Rules of Law
------------
1. If a base class exists, use it. If the base class is missing features
   that you need, make improvements to the base class before implementing
   a new one.
2. Functions should only return one type.  If a function can return a
   single item or a list of items, choose to return a list of items always,
   even if that means returning a list with a single item.
3. All code should be as explicit as possible. Favor readability/clarity over
   brevity.
4. Once you have submitted a branch for review, the only changes that
   should be made to that branch are changes requested by reviewers or
   functional issues.  Any follow on work should be submitted in a new
   branch/pull request.
   **Failure to comply will result in the pull request being abandoned.*
5. If you want to change the rules of law, do lots of reviews, get added to
   core and make a pull request!


Development Standards
------------------
- It is **HIGHLY** encouraged that if you have not already read (and even if
  it's been a while since you have) the Python Enhancement Proposals (PEPs)
  PEP-8 and PEP 20 that you do so.
- Guidelines here are intended to help encourage code unity, they are not
  unbreakable rules, but should be adhered to failing a good reason not to.
  When in doubt, **ALL** code should conform either directly to or in the
  spirit of Python PEP 20, if you are still in doubt, go with Python PEP-8.
- If you really are still in doubt, see Guideline 2.
  Base Classes are your friend. Use them when they make sense.
- Always use **SPACES**. **NEVER TABS**. All block indention should be
  four (4) spaces.
- Avoid single letter variable names except in the case of iterators,
  in which case a descriptive variable name would still be preferable
  if possible.
- Do not leave trailing whitespace or whitespace in blank lines.
- Put two newlines between top-level code (funcs, classes, etc).
- Use only UNIX style newlines ("\n"), not Windows style ("\r\n").
- Follow the ordering/spacing guidelines described in PEP8 for imports.
- Put one newline between methods in classes and anywhere else.
- Avoid using line continuations unless absolutely necessary. Preferable
  alternatives are to wrap long lines in parenthesis, or line breaking
  on the open parenthesis of a function call.
- Long strings should be handled by wrapping the string in parenthesis
  and having quote delimited strings per line within.
Example::
    long_string = ('I cannot fit this whole phrase on one '
                   'line, but I can properly format this string '
                   'by using this type of structure.')
- Do not write "except:", use "except Exception:" at the very least
- Use try/except where logical. Avoid wrapping large blocks of code in
  in huge try/except blocks.
- Blocks of code should either be self documenting and/or well commented,
  especially in cases of non-standard code.
- Use Python list comprehensions when possible. They can make large blocks
  of code collapse to a single line.
- Use Enumerated Types where logical to pass around string constants
  or magic numbers between Functions, Methods, Classes and Packages.
  Python does not provide a default Enumerated Type data type, CloudCafe uses
  Class structs by naming convention in their place.

Example::
  class ComputeServerStates(object):
      ACTIVE = "ACTIVE"
      BUILD = "BUILD"
      REBUILD = "REBUILD"
      ERROR = "ERROR"
      DELETING = "DELETING"
      DELETED = "DELETED"
      RESCUE = "RESCUE"
      PREP_RESCUE = "PREP_RESCUE"
      RESIZE = "RESIZE"
      VERIFY_RESIZE = "VERIFY_RESIZE"

