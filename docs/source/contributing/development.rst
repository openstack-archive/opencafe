===================
Development Process
===================

Starting a Feature
------------------

To give your development visibility, we strongly recommend creating a GitHub
issue describing your change before making any non-trivial change. This will
also give other contributors an early opportunity to provide feedback on your
change, which allows for questions that may have come up during the review
process be addressed earlier.

All development should occur in feature branches. The name of the feature
branch should be a short, meaningful name helps a reviewer understand the
purpose of the request. The scope of a feature branch should be relatively
narrow and granular. It should either cover a small, standalone feature or
one aspect of a larger feature. By keeping the scope of individual changes
small, it encourages the size of pull requests to stay small as well. While
there is no hard limit on the number of lines in a change, in general a review
should not be larger than several hundred lines of code. If it grows larger
than that, consider re-evaluating what the change is trying to accomplish to
determine if it can be broken up into smaller chunks.

Maintaining a Feature Branch
----------------------------

During the lifetime of a branch, you will likely want to perform commits as
your code progresses. However, when you submit your feature, your intent will
be to submit the entirety of your work as one logical change. There are
several strategies that can be used to handle this problem. The first is to
commit to the feature branch as you normally would, and then squash the
commits before submitting the branch for review. Another option is to make an
initial commit to your branch and then amend all additional changes to that
commit. We recommend the first approach as it allows you to have a history
of your changes while working on the branch.

Another issue to consider while working in a feature branch is that other
submissions may be merged before you submit your changes. These merged changes
may modify some of the same code that you are also changing, leading to a
conflict when your change is merged. To avoid this, you should be updating
your master branch regularly to determine if changes have been made that will
conflict with your feature branch. To sync your fork's master branch with
OpenCafe's master, use the following steps::

    0. git remote add upstream https://github.com/CafeHub/opencafe (this step
       only needs to be performed the first time)
    1. git checkout master
    2. git fetch upstream (you need to set the 
    3. git merge upstream/master

Once you have the upstream changes in your local repository, you can merge any
changes back into your feature branch by rebasing. If any conflicts occurs
during the rebase, you will need to resolve those issues before the rebase can
finish the process. If your master branch is up to date, your feature branch
can be updated using the following steps::

    1. git checkout <your_branch>
    2. git rebase -i master
    3. Git should complain about conflicting changes to resolve
    4. Resolve any merge conflicts
    5. git rebase --continue

Committing Changes for Review
-----------------------------

Once you have completed development of your feature, you should squash your
commits to a single change to keep the commit history of the project clean.
Your commit message should be informative and reference any GitHub issues
that you have worked on in this branch. The following is one example::

    Fixes an issue with JSON serialization. Addresses issue #145.
