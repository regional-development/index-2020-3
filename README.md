Індекс діяльності ОДА (3 квартал 2020 року):
==============================
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/regional-development/index-2020-3/main)
[![RTD](https://readthedocs.org/projects/index-2020-3/badge/?version=latest)](https://index-2020-3.readthedocs.io/)

## Table of Contents
+ [Важливі посилання](#links)
+ [Відтворення](#getting_started)
+ [Як долучитись (contributing)](.github/CONTRIBUTING.rst)

## Важливі посилання <a name = "links"></a>

1. [Сирі дані]()
2. [Презентація]()
3. [Таблиця з параметрами](https://docs.google.com/spreadsheets/d/1Pisy6EX4fkUnlm9rAqLsD_ycwWiUC9p-u3ZpKZe6oAs/edit?usp=sharing)

## Відтворення <a name = "getting_started"></a>
Ці інструкції допоможуть відтворити віртуальне середовища: через `binder` в хмарі або на локальному комп'ютері через `venv` 

### Локальне віртувальне середовище (venv)
```bash
$ gh repo clone regional-development/index-2020-3
$ cd index-2020-3
$ python -m venv env
$ source env/Scripts/activate
(env)$ python -m pip install -U pip setuptools wheel
(env)$ python -m pip install -r requirements.txt 
(env)$ jupyter notebook
```
