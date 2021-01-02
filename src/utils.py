# -*- coding: utf-8 -*-
""" 
Модуль містить допоміжні функції для підготовки даних та проведення розрахунків. 
"""
import numpy as np
import pandas as pd
from scipy import stats
from pathlib import Path
from functools import reduce


ROOT = Path(__file__).resolve().parent.parent
PATH_RAW = ROOT / "data" / "raw"
PATH_INTERIM = ROOT / "data" / "interim"
PATH_PROCESSED = ROOT / "data" / "processed"
POPULATION = pd.read_excel(PATH_RAW / "P99" / "population.xls", index_col=0)
REGIONS = {"region": POPULATION.index.tolist()}
REGIONS_MAP = POPULATION["region_id"].astype(float).to_dict()
POPULATION_MAP = POPULATION["population"].to_dict()


def _divide(a, b):
    """ Повертає 0 при діленні на 0 замість `np.inf`. """
    return np.divide(a, b, out=np.zeros_like(a), where=b != 0)


def merge_all(data, on, return_all_regions=True):
    """Послідовно виконує pd.merge на масиві таблиць.


    Parameters
    ----------
    data: list[pd.DataFrame]
        Список таблиць, які необхідно об'єднати
    on: str
        Ключ для об'єднання таблиць
    return_all_regions : bool
        Чи включати відсутні області в таблицю


    Returns
    -------
    `pd.DataFrame`
        Об'єднана єдина таблиця
    """
    df = reduce(lambda l, r: pd.merge(l, r, on=on, how="outer"), data)
    if not return_all_regions:
        return df

    all_regions = df.append(pd.DataFrame(REGIONS))
    return (
        all_regions.assign(order=all_regions["region"].map(REGIONS_MAP))
        .drop_duplicates("region")
        .sort_values("order")
        .drop("order", axis=1)
        .reset_index(drop=True)
    )


def weighted_average(df, columns, weights, multiplier=10):
    r"""Ф-ція середнього зваженого.

    .. math::
        \bar{x} = \frac{\sum_{i=1}^{n} w_ix_i}{\sum_{i=1}^{n} w_i} \times m
    де :math:`x` є `значенням`, :math:`w` є його вагою значення, :math:`m` є мультиплікатором.


    Parameters
    ----------
    df : pd.DataFrame
        Таблиця з параметрами
    columns : list[str]
        Перелік колонок, значення яких слід розрахувати
    weights: dict[str, float]
        Словник з назвою параметру та його вагою
    multiplier : float
        Мультиплікатор результату


    Examples
    --------
    >>> df = pd.DataFrame({
        "A": [1, 4, 4, 5, 6, 7, 5, 3, 4, 5],
        "B": [2, 8, 1, 4, 6, 2, 8, 1, 1, 1],
    })

    Функція адаптова під роботу з таблицею (використовує `broadcasting`),
    що містить окремі колонки, які необхідно порахувати; у реальному застосуванні
    ці колонки визначаються патерном.

    >>> weighted_average(df=df, columns=["A", "B"], weights={"A": 1.5, "B": 2})
    0    15.714286
    1    62.857143
    2    22.857143
    3    44.285714
    4    60.000000
    5    41.428571
    6    67.142857
    7    18.571429
    8    22.857143
    9    27.142857
    dtype: float64


    Returns
    -------
    `pd.Series`
        Колонка з розрахованим середнім зваженим
    """
    s = sum(df[col] * weights.get(col) for col in columns) / sum(weights.values())
    return s * multiplier


def zscore_wrapper(df, param, cv=1.96):
    r"""Визначає аутлаєри колонки `param` за допомогою
    `scipy.stats.zscore <https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.zscore.html>`_.

    Відхилення (аутлаєр) є статистично значущим, якщо отримане значення є більшим або меншим
    за критичне значення `cv`.

    .. math::
        z =\frac{x_i-\mu}{\sigma}


    Parameters
    ----------
    df : pd.DataFrame
        Таблиця з параметрами
    param : str
        Назва параметру
    cv : float
        Критичне значення [1.96, 2.58] для 95% та 99% стат. значущості відповідно

    Examples
    --------
    
    Певний параметр може містити аутлаєри, які часом можуть виникати внаслідок помилки в даних 
    або свідчити про аномальну ситуацію в певних областях (обидва варіанти можуть викривлювати
    результати розрахунків). 
    
    Для прикладу я генерую датасет `df`, що містить одну колонку `param`, котра складається з 
    випадкового набору значень в межах нормального розподілу (normal distribution) 
    
    >>> df = pd.DataFrame({"param": np.random.standard_normal(size=24)})
    >>> df
           param
    0  -1.292244
    1  -2.610441
    2   0.069343
    3  -0.959068
    4   0.407773
    5   0.192192
    6   0.694097
    7  -0.758156
    8   0.403748
    9   1.585239
    10 -0.807982
    11 -0.507439
    12 -0.312586
    13  0.624023
    14 -0.953230
    15 -0.797517
    16  1.604804
    17 -1.187396
    18 -0.535961
    19  2.263956
    20 -0.182657
    21  0.616233
    22 -0.928197
    23 -0.320723
    
    Функція по суті є обгорткою для ``scipy.stats.zscore`` і повертає ті рядки-аутлаєри 
    (чиї значення zscore виходять за критичне значення ``cv``)
    
    >>> zscore_wrapper(df, "param")
           param
    1  -2.610441
    19  2.263956
    

    Returns
    -------
    `pd.DataFrame`
        Таблиця з статистично значущими аутлаєрами
    """
    ss = stats.zscore(df[param], ddof=1, nan_policy="omit")
    return df.loc[abs(ss) > cv, :]


def normalize_parameter(
    array,
    fill_na=True,
    min_bound=None,
    max_bound=None,
    feature_range=(0, 1),
    reverse=False,
):
    r"""Імплементація min-max normalization формули:

    .. math::

        {x}' = a + \frac{(x-min(x))(b-a)}{max(x)-min(x)}

    де :math:`x` є `array`, :math:`a` та :math:`b` є `feature_range`, що за замовченням є [0, 1];

    Якщо параметри `min_bound` та `max_bound` задані, функція ігнорує
    реальні мінімальні та максимальні значення `array`.


    Parameters
    ----------
    array : pd.Series
        Колонка, значення якої нормалізуємо
    fill_na : bool
        NaN policy: заповнюємо порожні значення нулями (`True`) або ні (`False`)
    min_bound: Any[None, int, float]
        Задана нижня межа параметрів, або задане мінімальне значення колонки.
    max_bound: Any[None, int, float]
        Задана верхня межа параметрів, або задане максимальне значення колонки.
    feature_range : tuple (min, max), default=(0, 1)
        Шкала, в межах якої трансформуємо дані: [мінімальне, максимальне]
    reverse : bool
        Спосіб нормалізації. Найбільше значення отримує 1 якщо `True`, 0 якщо `False`.


    Examples
    --------
    >>> array = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

    За замовченням функція трансформує `array` в шкалу [0, 1], використовуючи наявні
    максимальні та мінімальні значення колонки.

    >>> normalize_parameter(array)
    feature_range=(0, 1); fill_na=True; array_bounds=(1, 10); normalization_bounds=(1, 10)
    0    0.000000
    1    0.111111
    2    0.222222
    3    0.333333
    4    0.444444
    5    0.555556
    6    0.666667
    7    0.777778
    8    0.888889
    9    1.000000
    dtype: float64

    Можемо задати максимальне значення самостійно. Наприклад, якщо ми хочемо порівняти наявність генеральних планів у селах
    і за найкращий показник свідомо беремо 100%, але в жодній з областей такого показника немає, ми вручну встановлюємо
    верхню межу як 100% замість максимального значення по областях

    Спрощений приклад на `array`: якщо `max_bound=15`, а реальне максимальне значення
    в межах колонки сягає `10`, найкращий з усіх рядків не отримує `1` (тому що
    порівнюється вже не відносно інших значень, а ще й відносно заданого максимального значення).

    >>> normalize_parameter(array, max_bound=15)
    feature_range=(0, 1); fill_na=True; array_bounds=(1, 10); normalization_bounds=(1, 15)
    0    0.000000
    1    0.071429
    2    0.142857
    3    0.214286
    4    0.285714
    5    0.357143
    6    0.428571
    7    0.500000
    8    0.571429
    9    0.642857
    dtype: float64

    Приклад використання іншої від [0, 1] шкали нормалізації:

    >>> normalize_parameter(array, feature_range=(2, 5))
    feature_range=(2, 5); fill_na=True; array_bounds=(1, 10); normalization_bounds=(1, 10)
    0    2.000000
    1    2.333333
    2    2.666667
    3    3.000000
    4    3.333333
    5    3.666667
    6    4.000000
    7    4.333333
    8    4.666667
    9    5.000000
    dtype: float64


    Returns
    -------
    `pd.Series`
        Колонка з нормалізованими значеннями
    """
    s = array.fillna(0) if fill_na else array
    array_min, array_max = array_bounds = s.min(), s.max()
    if min_bound is None:
        min_bound = array_min
    if max_bound is None:
        max_bound = array_max
    if reverse:
        min_bound, max_bound = max_bound, min_bound

    normalization_bounds = (min_bound, max_bound)
    feature_min, feature_max = feature_range
    print(f"{feature_range=}; {fill_na=}; {array_bounds=}; {normalization_bounds=}, {reverse=}")
    return feature_min + ((s - min_bound) * (feature_max - feature_min) / (max_bound - min_bound))


def save_data(sources, weights, parameter, show_results=False):
    """Розраховує оцінку галузевого параметру


    Parameters
    ----------
    sources: list[pd.DataFrame]
        Список усіх таблиць з нормалізованими показниками нижнього рівня
    weights: dict[str, float]
        Словник з назвою параметру та його вагою
    parameter : str
        Галузевий параметр (параметр верхнього рівня):
        [P1, P2, P3, P4, P5, P6, P7, P8]
    """
    _re_raw = "region|p\d{1}_\d{2}_raw$"
    _re_norm = "region|p\d{1}_\d{2}$"

    df_raw = merge_all(
        data=[df.loc[:, df.columns.str.contains(_re_raw)] for df in sources],
        on="region",
    )
    df_raw.to_csv(PATH_PROCESSED / f"{parameter}_raw.csv", index=False)

    df = merge_all(
        data=[df.loc[:, df.columns.str.contains(_re_norm)] for df in sources],
        on="region",
    )
    columns = df.loc[:, df.columns.str.contains("p")].columns
    df[parameter] = weighted_average(df, columns, weights)
    df.to_csv(PATH_PROCESSED / f"{parameter}.csv", index=False)
    if show_results:
        return df
