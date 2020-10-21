Індекс діяльності ОДА (N квартал 2020 року):
==============================

## Table of Contents
+ [Важливі посилання](#links)
+ [Відтворення](#getting_started)
+ [Як долучитись (contributing)](.github/CONTRIBUTING.md)

## Важливі посилання <a name = "links"></a>

1. [Сирі дані]()
2. [Презентація]()
3. [Таблиця з параметрами](https://docs.google.com/spreadsheets/d/1Pisy6EX4fkUnlm9rAqLsD_ycwWiUC9p-u3ZpKZe6oAs/edit?usp=sharing)

## Відтворення <a name = "getting_started"></a>
Ці інструкції допоможуть відтворити віртуальне середовища: через `binder` в хмарі або на локальному комп'ютері через `venv` 

### .binder
[![Binder](https://mybinder.org/badge_logo.svg)]()

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
