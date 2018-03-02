Contribution Guidelines
=======================

Portions of this guide are based on the excellent
contributing guide for the Python Requests_ library.

.. _Requests: http://www.python.org/

We know that contributing to open source projects can be a challenge,
so we've done our best to document our principals and processes. If you
are a new contributor, please take the time to read this document to
ensure that the process works as smoothly as possible. If you have
experiences while contributing that could have gone more smoothly if there
was a point that could have been explained better, help us out by making
a pull request to update this document.

We ask all maintainers and contributors to work with the following
principles in mind.

Be Cordial
----------

*Be cordial or be on your way*. *—Kenneth Reitz*

Developing software as a community will always be a challenge due to
differences in needs, styles and opinions. We strongly believe that
these differences can be handled in a respectful and productive manner.
While we value community contributions, **verbal abuse, intimidation,
and discrimination in any form of project communication will not be
tolerared.**

Get Early Feedback
------------------

If you are contributing, do not feel the need to sit on your contribution until
it is perfectly polished and complete. It helps everyone involved for you to
seek feedback as early as you possibly can. Submitting an early, unfinished
version of your contribution for feedback in no way prejudices your chances of
getting that contribution accepted, and can save you from putting a lot of work
into a contribution that is not suitable for the project.

Contribution Suitability
------------------------

Our project maintainers have the last word on whether or not a contribution is
suitable for OpenCafe. All contributions will be considered carefully, but from
time to time, contributions will be rejected because they do not suit the
current goals or needs of the project.

If your contribution is rejected, don't despair! As long as you followed these
guidelines, you will have a much better chance of getting your next
contribution accepted.

Code Contributions
==================

This section outlines the process for contributing code to the OpenCafe
project. All contributions should meet the OpenCafe coding standards,
which are documented in the next section.

Steps for Submitting Code
-------------------------

When contributing code, you'll want to follow this checklist:

1. Fork the repository on GitHub.
2. Run the tests to confirm they all pass on your system. If they don't, you'll
   need to investigate why they fail. If you're unable to diagnose this
   yourself, raise it as a bug report to the project.
3. Make your change.
4. Run the entire test suite again, confirming that all tests pass *including
   the ones you just added*.
5. Send a GitHub Pull Request to the main repository's ``master`` branch.
   GitHub Pull Requests are the expected method of code collaboration on this
   project.

The following sub-sections go into more detail on some of the points above.

Code Review
-----------

Contributions will not be merged until they've been code reviewed. You should
implement any code review feedback unless you strongly object to it. In the
event that you object to the code review feedback, you should make your case
clearly and calmly, and with technical reasoning. If, after doing so, the
feedback is still judged to apply, you must either apply the feedback or
withdraw your contribution.
 
New Contributors
----------------

If you are new or relatively new to Open Source, welcome! If you're concerned
about how best to contribute, consider contacting one of the project
maintainers and asking for help.

Coding Standards
================

OpenCAFE standards are intended to allow flexability in solving coding issues,
while maintaining uniformity and overall code quality.

Development Principles
----------------------

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
   *Failure to comply will result in the pull request being abandoned.*
5. These principals are based on the shared experience of the project
   maintainers.

Development Standards
---------------------

The following guidelines are intended to encourage a unified code style.
They are not unbreakable rules, but should be adhered to failing a good
reason to do otherwise.

- It is **HIGHLY** encouraged that if you have not already read (and even if
  it's been a while since you have) the Python Enhancement Proposals (PEPs)
  PEP 8 and PEP 20 that you do so.
- When in doubt, **ALL** code should conform either directly to or in the
  spirit of Python PEP 20. If you are still in doubt, go with PEP 8.
- Base Classes are your friend. Use them when they make sense.
- Always use **SPACES**. **NEVER TABS**. All block indention should be
  four (4) spaces.
- Avoid single letter variable names except in the case of iterators,
  in which case a descriptive variable name would still be preferable
  if possible.
- Do not leave trailing whitespace or whitespace in blank lines.
- Use only UNIX style newlines ("\n"), not Windows style ("\r\n").
- Follow the ordering/spacing guidelines described in PEP 8 for imports.
- Avoid using line continuations unless absolutely necessary. Preferable
  alternatives are to wrap long lines in parenthesis, or line breaking
  on the open parenthesis of a function call.
- Long strings should be handled by wrapping the string in parenthesis
  and having quote delimited strings per line within.

Example::

    long_string = ('I cannot fit this whole phrase on one '
                   'line, but I can properly format this string '
                   'by using this type of structure.')

- We prefer catching specific exceptions whenever possible. At the very
  least, use "except Exception:" rather than "except:".
- Use try/except over the minimim scope necessary. Avoid wrapping large
  blocks of code in in try/except blocks.
- Blocks of code should either be self documenting and/or well commented,
  especially in cases of non-standard code.
- Use Python list comprehensions when possible. They can make large blocks
  of code collapse to a single line.
- Use enumerated types where logical to pass around string constants
  or magic numbers between functions, methods, classes and packages.
  Since Python 2.7 does not provide an enumerated data type, OpenCafe uses
  class structs in the manner described in the following example.

Example:

::

    class ComputeServerStates(object):
        ACTIVE = "ACTIVE"
        BUILD = "BUILD"
        ERROR = "ERROR"        
        DELETED = "DELETED"
