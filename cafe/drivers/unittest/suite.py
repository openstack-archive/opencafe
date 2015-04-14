# Copyright 2015 Rackspace
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""
Contains a monkeypatched version of unittest's TestSuite class that supports
a version of addCleanup that can be used in classmethods.  This allows a
more granular approach to teardown to be used in setUpClass and classmethod
helper methods
"""

from unittest.suite import TestSuite, _DebugResult, util


class OpenCafeUnittestTestSuite(TestSuite):

    def _tearDownPreviousClass(self, test, result):
        previousClass = getattr(result, '_previousTestClass', None)
        currentClass = test.__class__
        if currentClass == previousClass:
            return
        if getattr(previousClass, '_classSetupFailed', False):
            return
        if getattr(result, '_moduleSetUpFailed', False):
            return
        if getattr(previousClass, "__unittest_skip__", False):
            return

        tearDownClass = getattr(previousClass, 'tearDownClass', None)
        if tearDownClass is not None:
            try:
                tearDownClass()
            except Exception as e:
                if isinstance(result, _DebugResult):
                    raise
                className = util.strclass(previousClass)
                errorName = 'tearDownClass (%s)' % className
                self._addClassOrModuleLevelException(result, e, errorName)
            # Monkeypatch: run class cleanup tasks regardless of whether
            # tearDownClass succeeds or not
            finally:
                if hasattr(previousClass, '_do_class_cleanup_tasks'):
                    previousClass._do_class_cleanup_tasks()

        # Monkeypatch: run class cleanup tasks regardless of whether
        # tearDownClass exists or not
        else:
            if getattr(previousClass, '_do_class_cleanup_tasks', False):
                previousClass._do_class_cleanup_tasks()

    def _handleClassSetUp(self, test, result):
        previousClass = getattr(result, '_previousTestClass', None)
        currentClass = test.__class__
        if currentClass == previousClass:
            return
        if result._moduleSetUpFailed:
            return
        if getattr(currentClass, "__unittest_skip__", False):
            return

        try:
            currentClass._classSetupFailed = False
        except TypeError:
            # test may actually be a function
            # so its class will be a builtin-type
            pass

        setUpClass = getattr(currentClass, 'setUpClass', None)
        if setUpClass is not None:
            try:
                setUpClass()
            except Exception as e:
                if isinstance(result, _DebugResult):
                    raise
                currentClass._classSetupFailed = True
                className = util.strclass(currentClass)
                errorName = 'setUpClass (%s)' % className
                self._addClassOrModuleLevelException(result, e, errorName)
                # Monkeypatch: Run class cleanup if setUpClass fails
                currentClass._do_class_cleanup_tasks()
