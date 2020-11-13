# -*- coding: utf-8 -*-
""" 
Модуль містить допоміжні функції для об'єднання та збереження даних. 
"""
import pandas as pd 
from pathlib import Path
from functools import reduce
from .formula import weighted_average


ROOT = Path(__file__).resolve().parent.parent  
PATH_RAW = ROOT / "data" / "raw"
PATH_INTERIM = ROOT / "data" / "interim"
PATH_PROCESSED = ROOT / "data" / "processed"
POPULATION = pd.read_excel(PATH_RAW / "P99" / "population.xls", index_col=0)
REGIONS = {"region": POPULATION.index.tolist()}
REGIONS_MAP = POPULATION["region_id"].astype(float).to_dict()
POPULATION_MAP = POPULATION["population"].to_dict()


def _merge_all(data, on, return_all_regions=True):
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
    df[parameter] = weighted_average(df, columns, weights)
    df.to_csv(PATH_PROCESSED / f"{parameter}.csv", index=False)
    if show_results:
        return df
