.. _codebase:

Codebase Structure
==================

.. code-block:: console

    ├── .github            <- Усе, що стосується github:
    │                         Contributing, Codebase Structure, Issue / PR templates тощо
    │
    ├── data               
    │   ├── interim        <- Опрацьовані дані, на основі яких проводяться розрахунки
    │   ├── processed      <- Результати розрахунків галузевих параметрів
    │   └── raw            <- Сирі дані
    │
    ├── docs               <- Вихідний код, що генерує `sphinx` документацію
    │
    ├── notebooks          <- Jupyter notebooks для підготовки та аналізу даних
    │
    ├── reports            <- Аналітична записка
    │   ├── presentation   <- Презентації з результатами
    │   └── figures        <- Графіки в оригінальній якості 
    │
    ├── scripts            <- Скрипти, що автоматично формують датасети з баз даних
    │
    ├── src                <- Допоміжні функції для розрахунку та візуалізації індексу
    │
    ├── .readthedocs.yml   <- Інструкції для readthedocs.io 
    │
    ├── README.md          <- Основний README
    │
    ├── TODO.md            <- Перелік завдань
    │
    ├── requirements.txt   <- Файл для відтворення віртуального середовище, 
    │                         згенерований за допомогою ── `pip freeze > requirements.txt`
    │
    ├── runtime.txt        <- Версія python для mybinder.org 
    │
    └── setup.py           <- Setuptools скрипт, що встановлює src/ як локальну бібліотеку
   