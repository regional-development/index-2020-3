Інструкція для відтворення документації
=======================================

Згенерувати документацію з ``src/``
---------------------------------

Спочатку імпортувати ``src`` в ``conf.py``.

Після: 

.. code-block:: console

    $ sphinx-apidoc -f -o ./source ./../src/


Додати ``source/modules.rst`` в `toctree` в ``index.rst``

Згенерувати html
----------------

.. code-block:: console

    $ make html


Якщо віндовс: 

.. code-block:: console

    $ sphinx-build -b html . _build
