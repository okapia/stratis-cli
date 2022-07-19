# Copyright 2019 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Test error type string formatting.
"""

# isort: STDLIB
import unittest

# isort: LOCAL
from stratis_cli._error_codes import PoolDeviceSizeChangeCode
from stratis_cli._errors import (
    StratisCliGenerationError,
    StratisCliIncoherenceError,
    StratisCliPartialFailureError,
    StratisCliUnknownInterfaceError,
)


class ErrorFmtTestCase(unittest.TestCase):
    """
    Test stringification of various error types.
    """

    def _string_not_empty(self, exception):
        """
        :param exception: an object of a Stratis CLI error type
        :type exception: Exception
        """
        self.assertNotEqual(str(exception), "")

    def test_stratis_cli_incoherence_error_fmt(self):
        """
        Test 'StratisCliIncoherenceError'
        """
        self._string_not_empty(StratisCliIncoherenceError("Error"))

    def test_stratis_cli_unknown_interface_error_fmt(self):
        """
        Test 'StratisCliUnknownInterfaceError'
        """
        self._string_not_empty(StratisCliUnknownInterfaceError("BadInterface"))

    def test_stratis_cli_generation_error_fmt(self):
        """
        Test 'StratisCliGenerationError'
        """
        self._string_not_empty(StratisCliGenerationError("Error"))

    def test_stratis_cli_partial_failure_error(self):
        """
        Test 'StratisCliPartialFailureError'
        """
        self._string_not_empty(
            StratisCliPartialFailureError("action", "unique resource")
        )
        self._string_not_empty(
            StratisCliPartialFailureError(
                "action", "unique resource", "something failed"
            )
        )


class SummarizeTestCase(unittest.TestCase):
    """
    Test summarize() function.
    """

    def _summarize_test(self, summary_value):
        """
        Check that the summary value is a str and is non-empty.

        :param summary_value: the result of calling summary()
        """
        self.assertIsInstance(summary_value, str)
        self.assertNotEqual(summary_value, "")

    def test_pool_device_size_change_code(self):
        """
        Verify valid strings returned from summary() method.
        """

        self._summarize_test(PoolDeviceSizeChangeCode.DEVICE_SIZE_INCREASED.summarize())
        self._summarize_test(PoolDeviceSizeChangeCode.DEVICE_SIZE_DECREASED.summarize())
