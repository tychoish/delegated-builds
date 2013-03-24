======================
Delegated Build Script
======================

Overview
--------

This is a simple script for facilitating builds of a project stored in
a git repository without interrupting current work or the current
state of the repository and without requiring any changes to an
existing build system.

Using the procedure provided by this script will only provide benefit
to builds facing certain kinds of contention in certain kinds of
workflows. Consider delegated builds if:

- your build process blocks productivity while running.

- you (regularly) build from multiple branches, at once and cannot
  currently build both branches concurrently. Delegated builds are
  particularly helpful if this process blocks productivity.

Additional Resources
--------------------

See the following resources for more information on the script and its
use:

- `Introductory Blog Post <http://tychoish.com/rhizome/delegated-builds>`_

- `Use in the MongoDB Documentation Project <https://github.com/mongodb/docs/blob/master/bin/delegated-build>`_

Use
---

Modify the script so that:

- the ``branches`` list contains the full list of branches you want
  to be able to build. While you can hard code this, it's probably
  better for the script to discover this itself.

- the ``builders`` list contains a full list of ``make`` targets that
  you want to be able to build. Again, the build system could report
  what these targets, which is preferable, but hard coding and
  manipulating work.

Then, use the script with the following arguments, as follows: ::

  delegated-build.py --branch <branch-name> --target <builder> <--logfile <path>> <--wait>

``--branch`` and ``--builder`` select the branch and builder, which
must exist on the allowable branches/builders list. Logfile is
optional, and overrides the default log file option
(``build/staging-build-<date>.log``). ``--wait`` is also optional and
defaults to ``False``. When ``--wait`` is ``True``, the script will
block until the ``make`` exits, otherwise the build process will
continue in the background.
