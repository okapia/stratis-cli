# Copyright 2016 Red Hat, Inc.
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
Test signature parsing.
"""

import string
import unittest

from dbus_signature_pyparsing import Parser

from hypothesis import given
from hypothesis import settings
from hypothesis import strategies

from hs_dbus_signature import dbus_signatures

from stratis_cli._dbus._signature._xformer import ToDbusXformer

# Omits h, unix fd, because it is unclear what are valid fds for dbus
SIGNATURE_STRATEGY = dbus_signatures(max_codes=20, blacklist="h")

OBJECT_PATH_STRATEGY = strategies.one_of(
   strategies.builds(
      '/'.__add__,
      strategies.builds(
         '/'.join,
         strategies.lists(
            strategies.text(
               alphabet=[
                  x for x in \
                     string.digits + \
                     string.ascii_uppercase + \
                     string.ascii_lowercase + \
                     '_'
               ],
               min_size=1,
               max_size=10
            ),
            max_size=10
         )
      )
   )
)


class StrategyGenerator(Parser):
    """
    Generate a hypothesis strategy for generating objects for a particular
    dbus signature which make use of base Python classes.
    """
    # pylint: disable=too-few-public-methods

    @staticmethod
    def _handleArray(toks):
        """
        Generate the correct strategy for an array signature.

        :param toks: the list of parsed tokens
        :returns: strategy that generates an array or dict as appropriate
        :rtype: strategy
        """

        if len(toks) == 5 and toks[1] == '{' and toks[4] == '}':
            return strategies.dictionaries(keys=toks[2], values=toks[3])
        elif len(toks) == 2:
            return strategies.lists(elements=toks[1])
        else: # pragma: no cover
            raise ValueError("unexpected tokens")

    def __init__(self):
        super(StrategyGenerator, self).__init__()

        # pylint: disable=unnecessary-lambda
        self.BYTE.setParseAction(
           lambda: strategies.integers(min_value=0, max_value=255)
        )
        self.BOOLEAN.setParseAction(lambda: strategies.booleans())
        self.INT16.setParseAction(
           lambda: strategies.integers(min_value=-0x8000, max_value=0x7fff)
        )
        self.UINT16.setParseAction(
           lambda: strategies.integers(min_value=0, max_value=0xffff)
        )
        self.INT32.setParseAction(
           lambda: strategies.integers(
              min_value=-0x80000000,
              max_value=0x7fffffff
           )
        )
        self.UINT32.setParseAction(
           lambda: strategies.integers(min_value=0, max_value=0xffffffff)
        )
        self.INT64.setParseAction(
           lambda: strategies.integers(
              min_value=-0x8000000000000000,
              max_value=0x7fffffffffffffff
           )
        )
        self.UINT64.setParseAction(
           lambda: strategies.integers(
              min_value=0,
              max_value=0xffffffffffffffff
           )
        )
        self.DOUBLE.setParseAction(lambda: strategies.floats())

        self.STRING.setParseAction(lambda: strategies.text())
        self.OBJECT_PATH.setParseAction(lambda: OBJECT_PATH_STRATEGY)
        self.SIGNATURE.setParseAction(lambda: SIGNATURE_STRATEGY)

        def _handleVariant():
            """
            Generate the correct strategy for a variant signature.

            :returns: strategy that generates an object that inhabits a variant
            :rtype: strategy
            """
            signature_strategy = dbus_signatures(
               max_codes=5,
               min_complete_types=1,
               max_complete_types=1,
               blacklist="h"
            )
            return signature_strategy.flatmap(
               lambda x: strategies.tuples(
                  strategies.just(x),
                  self.COMPLETE.parseString(x)[0]
               )
            )

        self.VARIANT.setParseAction(_handleVariant)

        self.ARRAY.setParseAction(StrategyGenerator._handleArray)

        self.STRUCT.setParseAction(
           # pylint: disable=used-before-assignment
           lambda toks: strategies.tuples(*toks[1:-1])
        )

STRATEGY_GENERATOR = StrategyGenerator().PARSER


class ParseTestCase(unittest.TestCase):
    """
    Test parsing various signatures.
    """

    _PARSER = ToDbusXformer()

    @given(SIGNATURE_STRATEGY)
    @settings(max_examples=100)
    def testParsing(self, signature):
        """
        Test that parsing is always succesful.
        """
        base_type_objects = [
           x.example() for x in \
              STRATEGY_GENERATOR.parseString(signature, parseAll=True)
        ]
        results = self._PARSER.PARSER.parseString(signature, parseAll=True)
        funcs = [f for (f, _) in results]
        sigs = [s for (_, s) in results]

        results = [f(x) for (f, x) in zip(funcs, base_type_objects)]
        values = [v for (v, _) in results]
        levels = [l for (_, l) in results]

        for sig, level in zip(sigs, levels):
            if 'v' not in sig:
                self.assertEqual(level, 0)
