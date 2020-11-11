Відтворення робочого середовища
===============================

.. image:: https://mybinder.org/badge_logo.svg
        :target: https://mybinder.org/v2/gh/regional-development/index-2020-3/main


Віртуальне середовище
---------------------

Ці інструкції допоможуть відтворити віртуальне середовище: 
через ``binder`` в хмарі або на локальному комп'ютері через ``venv``.

.. code-block:: console

    $ git clone https://github.com/regional-development/index-2020-3.git
    $ cd index-2020-3
    $ python -m venv env
    $ source env/Scripts/activate
    (env)$ python -m pip install -U pip setuptools wheel
    (env)$ python -m pip install -r requirements.txt

Для роботи з папкою ``notebooks/``: 

.. code-block:: console

    (env)$ jupyter notebook

Ключі доступу
-------------

Певні датасети -- `P02_006, P02_007, P04_009` -- формуються з локальних баз даних, котрі потребують ключів доступу. 

Поточна версія датасетів, котра використовується для розрахунків, збережена в агрегованому форматі в ``data/interim``. 
Якщо є потреба `оновити датасети`, слід додати ключі у файл ``.env`` у корені репозиторію у такому форматі:

.. code-block:: console

    MSSQL=123
    POSTGRESQL=123

Після цього слід встановити `dependencies` для роботи з базами даних та запустити скрипти: 

.. code-block:: console

    (env)$ python -m pip install -r requirements-dev.txt
    (env)$ python scripts/budget.py
    (env)$ python scripts/tenders.py
    (env)$ python scripts/vb.py


.. seealso::

    :ref:`contact`: для отримання ключів доступу