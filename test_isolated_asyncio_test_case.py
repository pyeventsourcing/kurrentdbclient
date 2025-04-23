from unittest import IsolatedAsyncioTestCase


class TestAsyncSetupError(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        msg = "This should cause the test suite to fail"
        raise Exception(msg)

    async def test(self):
        pass


class TestAsyncTeardownError(IsolatedAsyncioTestCase):
    async def asyncTearDown(self):
        msg = "This should cause the test suite to fail"
        raise Exception(msg)

    async def test(self):
        pass


class TestAsyncTestError(IsolatedAsyncioTestCase):
    async def test(self):
        msg = "This should cause the test suite to fail"
        raise Exception(msg)
