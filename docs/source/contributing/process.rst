===============
Review Process
===============

The goal of the code review process is to provide constructive feedback to team
members and to ensure that any changes follow the direction of the OpenCafe project.
While a reviewer will look for any obvious logical flaws, the primary purpose of code
reviews is **not** to verify that the submitted code functions correctly.
Code should be well tested before submission.

Review Etiquette
----------------

* Keep feedback constructive. All comments should be civil.
* Don't review your own requests.
* Comments should be descriptive. If alternate solutions need to be proposed, describe alternatives either as a snippet in the comment or in a linked gist.
* There should not be undocumented standards that submitters are held to. You should be able to point a submitter to
  a coding standard (either in PEP 8 or the OpenCafe documentation) that supports your concern. If you feel that something
  is missing from the documented coding standards, open a pull request with your clarifications.

Review Guidelines
-----------------

Reviewers are encouraged to use their own judgement and express concerns or recommend alternatives as part of the review process.
There is not a definitive checklist that reviewers use to evaluate a submission, but the following are some basic criteria a reviewer would be likely to use:

* Does this submission follow standard Python and OpenCafe coding standards?
* Does the architecture of the solution make sense? Is there either a more simple or scalable solution?
* Do the names of classes, functions, and variables add to the readability of the code?
* Do all classes and functions have docstrings?
* Are there sections of code whose purpose is unclear? Would additional comments or refactoring make it more clear?
* Were tests added for new functionality? (where applicable)

Voting
------

For a pull request to be accepted, it needs to pass three voting categories: Verified, Code Reviewed, and Approved.

* Verified - This vote determines if any pre-review gating jobs failed. A -1 means that at least one gating job failed,
  while +1 represents success.
* Code Review - Performed by contributors and core reviewers. This gate requires
  a +1 vote from any user as well as a +2 vote from a core reviewer. Votes for
  a review can range from -2 to +2. A rough breakdown of the intent of each rating are:

    * -2 - Request is judged as unacceptable to be merged as is. Reasons for this might include include duplication
      of effort, serious architectural flaws, addition of unnecessary dependencies,
      non-scalable solutions, or modifications that will break existing functionality.
    * -1 - Request may have minor issues that need to be addressed before the request is approved.
      Reasons may include factors such as unclear variable, function, or class names, missing docstrings, logical errors,
      or missing error checking.
    * +1 - Non-core member, approved.
    * +2 - Core member, approved.

* Approved - Once a pull request has passed code review, a core reviewer can vote +1
  in this category to allow the request to be merged. A vote of -1 is not typically used.

Merging
-------

Once a pull request has passed all voting requirements, Gerrit will try to merge the pull request to the master branch.
If conflicting changes have occurred during the time your pull request was open, a rebase may be required before
the pull request can be merged successfully.