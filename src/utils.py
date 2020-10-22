# -*- coding: utf-8 -*-
import os
import numpy as np 
import pandas as pd 
from scipy import stats
from pathlib import Path
from functools import reduce
from sqlalchemy import create_engine
from dotenv import find_dotenv, load_dotenv


load_dotenv(find_dotenv())
MSSQL = os.environ.get("MSSQL")
POSTGRESQL = os.environ.get("POSTGRESQL")
ROOT = Path(__file__).resolve().parent.parent  
PATH_RAW = ROOT / "data" / "raw"
PATH_INTERIM = ROOT / "data" / "interim"
PATH_PROCESSED = ROOT / "data" / "processed"
POPULATION = pd.read_excel(PATH_RAW / "P99" / "population.xls", index_col=0)
REGIONS = {"region": POPULATION.index.tolist()}
REGIONS_MAP = POPULATION["region_id"].astype(float).to_dict()
POPULATION_MAP = POPULATION["population"].to_dict()


def db_connect(query, db="MSSQL"):
    """ Зчитує таблицю з бази даних. 
    
    
    Parameters
    ----------
    query : str
        sql query, напр. SELECT * FROM "Budget"."Incomes";
    """
    _db = MSSQL if db == "MSSQL" else POSTGRESQL
    con = create_engine(_db)
    return pd.read_sql(query, con)


def merge_all(data, on, return_all_regions=True):
    """ Послідовно виконує pd.merge на масиві таблиць. 
    
    
    Parameters
    ----------
    data: list[pd.DataFrame]
        Список таблиць, які необхідно об'єднати
    on: str
        Ключ для об'єднання таблиць
    return_all_regions : bool
        Чи включати відсутні області в таблицю
    """
    df = reduce(lambda l, r: pd.merge(l, r, on=on, how="outer"), data)
    if not return_all_regions:
        return df

    all_regions = df.append(pd.DataFrame(REGIONS))
    return (
        all_regions
        .assign(order=all_regions["region"].map(REGIONS_MAP))
        .drop_duplicates("region")
        .sort_values("order")
        .drop("order", axis=1)
        .reset_index(drop=True)
    )


def divide(a, b):
    """ Повертає 0 при діленні на 0 замість `inf`. """
    return np.divide(a, b, out=np.zeros_like(a), where=b!=0)


def weighted_average(df, columns, weights, multiplier=1.0):
    """ Ф-ція середнього зваженого. 
    
    
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
    """
    s = sum(df[col] * weights.get(col) for col in columns) / sum(weights.values())
    return s * multiplier


def outliers(df, param, cv=1.96):
    """ Повертає рядки з аутлаєром в колонці `param`.

    the standard score is the number of standard deviations 
    by which the value of a raw score is above or below the 
    mean value of what is being observed or measured.

    Відхилення є статистично значущим, якщо значення є більшим або меншим
    за критичне значення `cv`
    
    
    Parameters
    ----------
    df : pd.DataFrame
        Таблиця з параметрами
    param : str
        Назва параметру
    cv : float
        Критичне значення [1.96, 2.58] для 95% та 99% відповідно
    """
    ss = stats.zscore(df[param], ddof=1, nan_policy="omit")
    return df.loc[abs(ss) > cv, :] 


def normalize_parameter(
    array, 
    fill_na=True, 
    min_bound=None, 
    max_bound=None,
    feature_range=(0, 1), 
    reverse=False
):
    """ Min-max normalization. 
    
    Нормалізує значення `array` до шкали `feature_range`, використовуючи задані 
    -- `min_bound` та `max_bound` -- або поточні мін. та макс. значення `array`  
    

    Parameters
    ----------
    array : pd.Series
        Колонка, значення якої нормалізуємо
    fill_na : bool
        NaN policy: заповнюємо порожні значення нулями (True) або ні (False)
    min_bound, max_bound : Any (None, int, float)
        Задані нижня та верхні межі параметрів 
        За замовченням - мінімальні та максимальні значення колонки. 
        Приклад: якщо ми хочемо порівняти наявність генеральних планів у селах 
                 і за найкращий показник свідомо беремо 100%, але в жодній з 
                 областей такого показника немає, ми вручну встановлюємо 
                 верхню межу як 100% замість максимального значення по областях
    feature_range : tuple (min, max), default=(0, 1)
        Шкала, в межах якої трансформуємо дані [мінімальне, максимальне]
    reverse : bool
        Спосіб нормалізації

    Examples
    --------
    >>> array = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
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
    """
    s = array.fillna(0) if fill_na else array
    array_min, array_max = s.min(), s.max()
    if min_bound is None:
        min_bound = array_min
    if max_bound is None:
        max_bound = array_max
        
    array_bounds = (array_min, array_max)
    normalization_bounds = (min_bound, max_bound)
    print(f"{feature_range=}; {fill_na=}; {array_bounds=}; {normalization_bounds=}")

    feature_min, feature_max = feature_range
    min_max_normalization = feature_min + ((s - min_bound) * (feature_max - feature_min) / (max_bound - min_bound))
    return 1 - min_max_normalization if reverse else min_max_normalization



def save_data(sources, weights, parameter, show_results=False):
    """ Розраховує оцінку галузевого параметру 
    
    
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
        on="region"
    )
    df_raw.to_csv(PATH_PROCESSED / f"{parameter}_raw.csv", index=False)

    df = merge_all(
        data=[df.loc[:, df.columns.str.contains(_re_norm)] for df in sources],
        on="region"
    )
    columns = df.loc[:, df.columns.str.contains("p")].columns
    df[parameter] = weighted_average(df, columns, weights, multiplier=10)
    df.to_csv(PATH_PROCESSED / f"{parameter}.csv", index=False)
    if show_results:
        return df
