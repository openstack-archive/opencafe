===================
Development Process
===================

Gerrit Account Setup
--------------------

Before contributing code, you will need an account with the OpenStack Gerrit instance.
This Gerrit instance uses Launchpad accounts for authentication, and also requires additional steps to
properly setup your SSH keys. The OpenStack Gerrit wiki has very detailed instructions on how to
`set up your account <https://wiki.openstack.org/wiki/Gerrit_Workflow#Account_Setup>`_,
`install git-review <https://wiki.openstack.org/wiki/Gerrit_Workflow#Git_Review_Installation>`_, and
`how to verify that you can submit code <https://wiki.openstack.org/wiki/Gerrit_Workflow#Project_Setup>`_.


Starting a Feature
------------------

All development should occur in feature branches. The name of the feature branch should be
a short, meaningful name as this name will show up in Gerrit as the title of your change.

The scope of a feature branch should be relatively narrow and granular. It should either cover a small,
standalone feature or one aspect of a larger feature. By keeping the scope of individual changes small,
it encourages the size of pull requests to stay small as well. While there is no hard limit on the number
of lines in a change, in general a review should not be larger than several hundred lines of code. If it
grows larger than that, consider re-evaluating what the change is trying to accomplish to determine
if it can be broken up install smaller chunks.


Maintaining a Feature Branch
----------------------------

During the lifetime of a branch, you will likely want to perform commits as your code progresses. However, when
you submit your feature, your intent will be to submit the entirety of your work as one logical change. There
are several strategies that can be used to handle this problem. The first is to commit to the feature branch
as you normally would, and then squash the commits before submitting the branch for review. The second approach
is to make one commit to the branch initially, and then use the --amend parameter with any further commits
to the branch. Both methods work equally well, so which one you choose to follow is left to personal preference.

Another issue to consider while developing in a branch is the changes that are occurring in the master branch.
While working in a feature branch, it is very likely that other submissions will be merged before you submit
your changes. You should be updating your master branch regularly (daily is recommended)
to determine if changes have been made that will conflict with your feature branch. If you determine that
a conflict will occur, you will want to rebase your branch as soon as possible to avoid merge conflicts
when you submit your code for review. If your master branch is up to date, your feature branch can be updated
using the following steps::

    1. git checkout <your_branch>
    2. git rebase -i master
    3. Git should complain about conflicting changes to resolve
    4. Resolve any merge conflicts
    5. git rebase --continue

Committing Changes
------------------

Git commit messages should match the following format:

* The first line of the message should be a brief description of the change
* The second line should be blank
* The rest of the message should be either a paragraph or bulleted list that describes
  the changes made in the submission. If the review is
  addressing an issue from an external tracking system such as GitHub or Launchpad, the issue number
  or a link to the issue should also be contained in the body of the commit message.

Example::

    Adds support for some_new_feature

    * Made change x in Class1
    * Made change y in Class2
    * Updated docs to reflect changes

Submission to Gerrit
------------------------

Once your changes are complete and the commit is made, the change is ready for review. Before submitting the code,
always make one final pass through your changes to make sure any debugging statements or commented out code is removed.
You will also want to run any unit tests in the project to make sure they still pass after your changes. Once you are
satisfied, you can submit your changes::

    git review
