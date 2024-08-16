django-alive-checks
===================

`django-alive-checks` is a Django application that provides additional health checks for your Django projects. These checks are designed to work with the `django-alive <https://github.com/pinax/django-alive>`_ package but include dependencies that cannot be part of `django-alive` itself.

Installation
------------

You can install the base package with:

.. code-block:: bash

    pip install django-alive-checks

If you want to include support for Elasticsearch, install with:

.. code-block:: bash

    pip install django-alive-checks[elasticsearch]

Usage
-----

### Check Elasticsearch

The ``check_elasticsearch`` function allows you to ping an Elasticsearch server to verify that it is reachable and functioning correctly. This function requires the ``elasticsearch`` package to be installed.

#### Function Signature

.. code-block:: python

    def check_elasticsearch(settings):
        pass

#### Parameters

- ``settings`` (``dict``): A dictionary of settings that will be passed to the ``Elasticsearch()`` constructor. This allows you to configure the connection to your Elasticsearch server.

#### Example

.. code-block:: python

    from django_alive_checks.checks import check_elasticsearch

    # Example settings for connecting to Elasticsearch
    elasticsearch_settings = {
        'hosts': ['localhost:9200'],
    }

    # Perform the health check
    try:
        check_elasticsearch(elasticsearch_settings)
        print("Elasticsearch is alive!")
    except Exception as e:
        print(f"Elasticsearch check failed: {e}")

This function will attempt to ping the Elasticsearch server. If the server is reachable and responds to the ping, the function will complete successfully. If not, it will raise a ``HealthcheckFailure`` exception.

### Integration with django-alive

To integrate the ``check_elasticsearch`` function with your ``django-alive`` checks, you can add it to your health checks configuration:

.. code-block:: python

    # settings.py

    from django_alive_checks.checks import check_elasticsearch

    ALIVE_CHECKS = [
        # Other checks...
        lambda: check_elasticsearch({'hosts': ['localhost:9200']}),
    ]

Testing
-------

To run the tests for this project:

.. code-block:: bash

    python -m unittest discover

The tests cover the following scenarios:

- Successful connection to Elasticsearch.
- Failed connection to Elasticsearch.
- Exceptions during connection attempts.
- Handling the absence of the ``elasticsearch`` package.

Contributing
------------

Contributions are welcome! If you encounter any issues, have ideas for improvements, or want to add more checks, feel free to open an issue or submit a pull request.

License
-------

This project is licensed under the MIT License. See the `LICENSE` file for more details.

Acknowledgments
---------------

Thanks to the Django and Elasticsearch communities for their continued support and development of the libraries that make this project possible.

