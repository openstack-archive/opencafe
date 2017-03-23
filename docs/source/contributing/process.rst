===================
Code Review Process
===================

The goal of the code review process is to provide constructive feedback to
contributors and to ensure that any changes follow the direction of the
OpenCafe project. While a reviewer will look for any obvious logical flaws,
the primary purpose of code reviews is **not** to verify that the submitted
code functions correctly. We understand that the original design of OpenCafe
did not lend itself well to unit testing, but we encourage that submissions
include tests when possible.

Process Overview
----------------

Two steps will occur before a pull request is merged. First, our CI will use
tox to run our style checks and all unit tests against the proposed branch.
Once these checks pass, the pull request needs to reviewed and approved by at
least one OpenCafe maintainer (the current list of maintainers can be viewed
in the AUTHORS file of this project). 

Review Etiquette
----------------

- Keep feedback constructive. Comment on the code and not the person.
  All comments should be civil.
- Review comments should be specific and descriptive. If alternative
  implementations need to be proposed, describe alternatives either as
  an inline snippet in the review comments or in a linked gist.
- All standards that contributors are held to should be documented.
  Reviewers should be able to point a contributor to a coding standard
  (either in PEP 8 or the OpenCafe development guidelines) that supports
  the concern. If you find that something is missing from the documented
  coding standards, open a pull request to our documentation with your
  clarifications.

Review Guidelines
-----------------

Reviewers are encouraged to use their own judgement and express concerns or
recommend alternatives as part of the review process. There is not a
definitive checklist that reviewers use to evaluate a submission, but the
following are some basic criteria that a reviewer would be likely to use:

- Does this submission follow standard Python and OpenCafe coding standards?
- Does the architecture of the solution make sense? Is there either a more
  simple or scalable solution? Does the solution add unnecessary complexity? 
- Do the names of classes, functions, and variables impact the readability
  of the code?
- Do all classes and functions have docstrings?
- Are there sections of code whose purpose is unclear? Would additional
  comments or refactoring make it more clear?
- Were tests added for cases created by the code submission?
  (where applicable)

Merging
-------

Once a pull request has passed our CI and code review, the reviewer will try
to merge the pull request to the master branch. If conflicting changes have
occurred during the time your pull request was open, a rebase may be required
before the pull request can be merged successfully.
