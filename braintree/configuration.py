import os
import sys
import braintree
import braintree.util.http_strategy.pycurl_strategy
import braintree.util.http_strategy.httplib_strategy
import braintree.util.http_strategy.requests_strategy

class Configuration(object):
    """
    A class representing the configuration of your Braintree account.
    You must call configure before any other Braintree operations. ::

        braintree.Configuration.configure(
            braintree.Environment.Sandbox,
            "your_merchant_id",
            "your_public_key",
            "your_private_key"
        )

    By default, every request to the Braintree servers verifies the SSL connection
    using the `PycURL <http://pycurl.sourceforge.net/>`_
    library.  This ensures valid encryption of data and prevents man-in-the-middle attacks.

    If you are in an environment where you absolutely cannot load `PycURL <http://pycurl.sourceforge.net/>`_, you
    can turn off SSL Verification by setting::

        Configuration.use_unsafe_ssl = True

    This is highly discouraged, however, since it leaves you susceptible to
    man-in-the-middle attacks.

    If you are using Google App Engine, you must use unsafe ssl [1]_::

        The proxy the URL Fetch servicr uses cannot authenticate the host it
        is contacting. Because there is no certificate trust chain, the proxy
        accepts all certificates, including self-signed certificates. The
        proxy server cannot detect "man in the middle" attacks between App
        Engine and the remote host when using HTTPS.

.. [1] `URL Fetch Python API Overview <https://developers.google.com/appengine/docs/python/urlfetch/overview>`_
    """
    @staticmethod
    def configure(environment, merchant_id, public_key, private_key):
        Configuration.environment = environment
        Configuration.merchant_id = merchant_id
        Configuration.public_key = public_key
        Configuration.private_key = private_key
        Configuration.use_unsafe_ssl = False

    @staticmethod
    def gateway():
        return braintree.braintree_gateway.BraintreeGateway(Configuration.instantiate())

    @staticmethod
    def instantiate():
        return Configuration(
            Configuration.environment,
            Configuration.merchant_id,
            Configuration.public_key,
            Configuration.private_key
        )

    @staticmethod
    def api_version():
        return "3"

    def __init__(self, environment, merchant_id, public_key, private_key):
        self.environment = environment
        self.merchant_id = merchant_id
        self.public_key = public_key
        self.private_key = private_key
        self._http_strategy = self.__determine_http_strategy()

    def base_merchant_path(self):
        return "/merchants/" + self.merchant_id

    def base_merchant_url(self):
        return self.environment.protocol + self.environment.server_and_port + self.base_merchant_path()

    def http(self):
        return braintree.util.http.Http(self)

    def http_strategy(self):
        if Configuration.use_unsafe_ssl:
            return braintree.util.http_strategy.httplib_strategy.HttplibStrategy(self, self.environment)
        else:
            return self._http_strategy

    def __determine_http_strategy(self):
        if "PYTHON_HTTP_STRATEGY" in os.environ:
            return self.__http_strategy_from_environment()

        if sys.version_info[0] == 2 and sys.version_info[1] == 5:
            return braintree.util.http_strategy.pycurl_strategy.PycurlStrategy(self, self.environment)
        else:
            return braintree.util.http_strategy.requests_strategy.RequestsStrategy(self, self.environment)

    def __http_strategy_from_environment(self):
        strategy_name = os.environ["PYTHON_HTTP_STRATEGY"]
        if strategy_name == "httplib":
            return braintree.util.http_strategy.httplib_strategy.HttplibStrategy(self, self.environment)
        elif strategy_name == "pycurl":
            return braintree.util.http_strategy.pycurl_strategy.PycurlStrategy(self, self.environment)
        elif strategy_name == "requests":
            return braintree.util.http_strategy.requests_strategy.RequestsStrategy(self, self.environment)
        else:
            raise ValueError("invalid http strategy")
