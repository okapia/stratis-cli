"""
Miscellaneous top-level actions.
"""

from __future__ import print_function

from .._constants import BUS
from .._constants import SERVICE
from .._constants import TOP_OBJECT

from .._dbus import Manager

from .._errors import StratisCliUnimplementedError
from .._errors import StratisCliValueUnimplementedError

class TopActions(object):
    """
    Top level actions.
    """

    @staticmethod
    def create_pool(namespace):
        """
        Create a stratis pool.
        """
        if namespace.force:
            raise StratisCliValueUnimplementedError(
               namespace.force,
               "namespace.force"
            )

        if namespace.redundancy != 'none':
            raise StratisCliValueUnimplementedError(
               namespace.redundancy,
               "namespace.redundancy"
            )

        proxy = BUS.get_object(SERVICE, TOP_OBJECT)

        (result, rc, message) = Manager(proxy).CreatePool(
           namespace.name,
           namespace.device,
           0
        )

        if rc == 0:
            print("New pool with object path: %s" % result)

        return (rc, message)

    @staticmethod
    def list_pools(namespace):
        """
        List all stratis pools.
        """
        # pylint: disable=unused-argument
        proxy = BUS.get_object(SERVICE, TOP_OBJECT)

        (result, rc, message) = Manager(proxy).ListPools()
        if rc != 0:
            return (rc, message)

        for item in result:
            print(item)
        return (rc, message)

    @staticmethod
    def destroy_pool(namespace):
        """
        Destroy a stratis pool.
        """
        if namespace.force:
            raise StratisCliValueUnimplementedError(
               namespace.force,
               "namespace.force"
            )

        proxy = BUS.get_object(SERVICE, TOP_OBJECT)

        (result, rc, message) = Manager(proxy).DestroyPool(namespace.name)

        if rc == 0:
            print("Deleted pool with object path: %s" % result)

        return (rc, message)

    @staticmethod
    def rename_pool(namespace):
        """
        Rename a pool.
        """
        # pylint: disable=unused-argument
        raise StratisCliUnimplementedError("No rename facility available.")