# -*- coding: utf-8 -*-
""" 
Модуль містить допоміжні функції для візуалізації результатів оцінювання. 
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams 
from math import ceil, pi
from .utils import ROOT


FORMAT = "png"
MAX_PARAMS = 10
FIGURES = ROOT / "reports" / "figures"
dict_labels = {
    "P1": "економіка",
    "P2": "бюджет",
    "P3": "приватизація",
    "P4": "будівництво",
    "P5": "екологія",
    "P6": "освіта та здоров'я",
    "P7": "соцзахист",
    "P8": "праця",
}


def delete_frame(ax):
    """ sns.despine() для matplotlib. """
    ax.spines["top"].set_color("none")
    ax.spines["bottom"].set_color("none")
    ax.spines["left"].set_color("none")
    ax.spines["right"].set_color("none")


def draw_spider(ax, angles, values, values_mean, cols):
    """Spider-візуалізація.


    Parameters
    ----------
    ax: matplotlib.axes._subplots.AxesSubplot
        Тло візуалізації
    angles: list[float]
        Нахил для візулаізації
    values: list[floats]
        Оцінка параметрів верхнього рівня
    values_mean: float
        Середня оцінка параметрів верхнього рівня
    cols: list[str]
        Колонки параметрів верхнього рівня
    """
    rot_angles = [0, -45, 90, 45, 0, -45, 90, 45, 0]

    ax.set_rlabel_position(0)
    ax.set_theta_offset(pi / 2)
    ax.set_theta_direction(-1)

    yticks = [*range(0, 12, 2)]
    locs, labels = plt.xticks(angles[:-1], cols, color="grey", size=10, rotation=90)
    plt.yticks(yticks, [])

    plt.grid(color="#E8E8E8")
    ax.axis([0, angles[-1], 0, 10])
    ax.fill(angles, values_mean, color="gray", alpha=0.05)
    ax.plot(angles, values, linewidth=1, linestyle="solid", color="#2f3f60")
    for i, j in zip(angles, values):
        ax.annotate(str(round(j, 1)), xy=(i, j + 1.3), ha="center", va="center")

    plt.gcf().canvas.draw()
    for label, angle in zip(labels, rot_angles):
        x, y = label.get_position()
        ax.text(
            x,
            y,
            label.get_text(),
            transform=label.get_transform(),
            ha=label.get_ha(),
            va=label.get_va(),
            color="grey",
            rotation=angle,
        )
    ax.set_xticklabels([])


def draw_multiple_spiders(df_index, cols, save=False):
    """Створює графік, що показує значення параметрів верхнього рівня для кожної з областей.
    Обгорта для `draw_spider`


    Parameters
    ----------
    df_index: pd.DataFrame
        Таблиця з розрахованим індексом
    cols: list[str]
        Колонки параметрів верхнього рівня
    save: bool, defaults `False`
        Чи слід зберігати зображення в ``reports/figures``
    """
    rcParams["font.size"] = 7
    N = len(cols)
    angles = [n / float(N) * 2 * pi for n in range(N)]
    angles.append(2 * pi)

    values_mean = [*df_index[cols].mean()]
    values_mean.append(values_mean[0])
    x_labels = [dict_labels[col] for col in cols]

    total = df_index.shape[0]
    sub_cols = 8
    sub_rows = ceil(total / sub_cols)

    fig = plt.figure(figsize=(20, 10))

    counter = 0
    for r in range(sub_rows):
        for c in range(sub_cols):
            values = list(df_index.loc[counter, cols])
            values.append(values[0])
            title = df_index.loc[counter, "region"]
            counter += 1
            if counter <= total:
                ax = plt.subplot2grid((sub_rows, sub_cols), (r, c), polar=True)
                draw_spider(ax, angles, values, values_mean, x_labels)
                ax.set_title(title, pad=17, fontsize=9)

    plt.subplots_adjust(wspace=0.45, hspace=0.45)
    if save:
        plt.savefig(
            FIGURES / f"00_index_gen_v3.{FORMAT}",
            dpi=300,
            bbox_inches="tight",
            pad_inches=0.3,
            transparent=False,
        )


def draw_profile_gen(df_index, cols, reg_index, save=False):
    """Створює графік для області `reg_index` з оцінками параметрів верхнього рівня


    Parameters
    ----------
    df_index: pd.DataFrame
        Таблиця з розрахованим індексом
    cols: list[str]
        Колонки верхнього параметрів рівня
    reg_index: int
        номер індексу таблиці області, яку слід візуалізувати
    save: bool, defaults `False`
        Чи слід зберігати зображення в ``reports/figures``
    """
    rcParams["font.size"] = 12
    fig = plt.figure(figsize=(6, 4))

    values_mean = df_index[cols].mean().sort_index(ascending=False)
    values = df_index.loc[reg_index, cols].sort_index(ascending=False)
    x_labels = [dict_labels[col] for col in cols]
    x_labels.reverse()
    # title = df_index.loc[reg_index, "region"]

    colors = []
    for i in range(values_mean.shape[0]):
        if values[i] >= values_mean[i]:
            colors.append("#007f86")
        elif values[i] < values_mean[i]:
            colors.append("#a3550f")

    ax = plt.subplot(111)
    delete_frame(ax)

    for ind in range(values_mean.shape[0]):
        ax.plot(
            [values_mean[ind], values[ind]],
            [values_mean.index[ind], values_mean.index[ind]],
            color="black",
            zorder=0,
        )
        diff = values[ind] - values_mean[ind]
        ax.annotate(
            str(round(diff, 1)),
            xy=(values[ind] - diff / 2, ind + 0.35),
            ha="center",
            va="center",
            color=colors[ind],
            fontsize=8,
        )
        ax.annotate(
            str(round(values[ind], 1)),
            xy=(values[ind], ind - 0.4),
            ha="center",
            va="center",
            fontsize=8,
        )

    ax.scatter(values_mean, values_mean.index, color="gray", zorder=1, s=35)
    ax.scatter(values, values.index, color=colors, zorder=2, alpha=1, s=35)

    # ax.set_title(title+' область',pad=10)
    ax.set_yticklabels(x_labels)
    ax.set_xlim(0, 10)
    ax.set_ylim(-1, 8)
    ax.set_xlim(-1, 11)

    if save:
        plt.savefig(
            FIGURES / f"01_region_profile_gen_{reg_index}.{FORMAT}",
            dpi=300,
            bbox_inches="tight",
            pad_inches=0.3,
            transparent=False,
        )

    plt.show()
    plt.close()


def draw_profile_det(df_index, cols, reg_index, save=False):
    """Створює графік для області `reg_index` з оцінками параметрів нижнього рівня


    Parameters
    ----------
    df_index: pd.DataFrame
        Таблиця з розрахованим індексом
    cols: list[str]
        Колонки нижнього параметрів рівня
    reg_index: int
        номер індексу таблиці області, яку слід візуалізувати
    save: bool, defaults `False`
        Чи слід зберігати зображення в ``reports/figures``

    """
    rcParams["font.size"] = 12

    x_labels = [dict_labels[col] for col in cols]
    total = len(x_labels)
    sub_cols = 4
    sub_rows = ceil(total / sub_cols)

    fig = plt.figure(figsize=(22, 10))
    counter = 0
    for r in range(sub_rows):
        for c in range(sub_cols):
            title = x_labels[counter]
            counter += 1
            if counter <= total:
                cols_lower = df_index.loc[
                    :, df_index.columns.str.contains("p" + str(counter))
                ].columns
                values_mean = df_index[cols_lower].mean().sort_index(ascending=False)
                values_mean_all = list(
                    np.zeros(MAX_PARAMS - values_mean.shape[0])
                ) + list(values_mean)
                index_labels_all = [
                    "" for i in range(MAX_PARAMS - values_mean.shape[0])
                ] + list(values_mean.index)
                values_reg = df_index.loc[reg_index, cols_lower].sort_index(
                    ascending=False
                )
                values_reg = values_reg.map(lambda x: x + 0.0000001 if x == 0 else x)
                values_reg_all = list(
                    np.zeros(MAX_PARAMS - values_reg.shape[0])
                ) + list(values_reg)

                colors = []
                for i in range(len(values_mean_all)):
                    if values_reg_all[i] >= values_mean_all[i]:
                        colors.append("#007f86")
                    elif values_reg_all[i] < values_mean_all[i]:
                        colors.append("#a3550f")

                ax = plt.subplot2grid((sub_rows, sub_cols), (r, c))
                delete_frame(ax)
                for ind in range(len(values_mean_all)):
                    ax.plot(
                        [values_mean_all[ind], values_reg_all[ind]],
                        [ind, ind],
                        color="black",
                        zorder=0,
                    )
                    if values_reg_all[ind] > 0:
                        diff = values_reg_all[ind] - values_mean_all[ind]
                        ax.annotate(
                            str(round(diff, 2)),
                            xy=(values_reg_all[ind] - diff / 2, ind + 0.3),
                            ha="center",
                            va="center",
                            color=colors[ind],
                            fontsize=8,
                        )
                        ax.annotate(
                            str(round(values_reg_all[ind], 2)),
                            xy=(values_reg_all[ind], ind - 0.35),
                            ha="center",
                            va="center",
                            fontsize=8,
                        )
                ax.scatter(
                    values_mean_all,
                    [i for i in range(MAX_PARAMS)],
                    s=[i if i == 0 else 35 for i in values_mean_all],
                    color="gray",
                    zorder=1,
                )
                ax.scatter(
                    values_reg_all,
                    [i for i in range(MAX_PARAMS)],
                    s=[i if i == 0 else 35 for i in values_reg_all],
                    color=colors,
                    zorder=2,
                )
                ax.set_yticks([i for i in range(10)])
                ax.set_yticklabels(index_labels_all)
                ax.set_xlim(-0.1, 1.1)
                ax.set_title(title, pad=17)

    title = df_index.loc[reg_index, "region"] + " область: загальний профіль"
    fig.suptitle(title, fontsize=22, weight="bold", alpha=0.95)
    plt.subplots_adjust(top=0.89, wspace=0.3, hspace=0.3)
    if save:
        plt.savefig(
            FIGURES / f"02_region_profile_det_{reg_index}.{FORMAT}",
            dpi=300,
            bbox_inches="tight",
            pad_inches=0.3,
            transparent=False,
        )
    plt.show()
    plt.close()


def draw_rankings(df_index, kvartal="III", save=False):
    """Створює відсортований барчарт з остаточними оцінками.


    Parameters
    ----------
    df_index: pd.DataFrame
        Таблиця з розрахованим індексом
    kvartal: str
        Номер кварталу для винесення в заголовок візуалізації
    save: bool, defaults `False`
        Чи слід зберігати зображення в ``reports/figures``
    """
    fig = plt.figure(figsize=(22, 10))
    ax = plt.subplot(111)
    delete_frame(ax)

    df_index_hist = df_index[["region", "I"]].sort_values(by="I").reset_index(drop=True)

    colors = ["#a3550f", "#f2dd05", "#007f86"]
    colors_list = (
        [colors[0] for r in range(3)]
        + [colors[1] for y in range(df_index_hist.shape[0] - 6)]
        + [colors[2] for g in range(3)]
    )

    ax.barh(df_index_hist["region"], df_index_hist["I"], color=colors_list)
    for i in df_index_hist.index:
        ax.annotate(
            int(df_index_hist.loc[i, "I"]),
            xy=(df_index_hist.loc[i, "I"] - 2.2, df_index_hist.loc[i, "region"]),
            c="white",
            va="center",
        )
        ax.set_xlim(0, 100)

    fig.suptitle(
        f"Індекс оцінки ОДА за {kvartal} квартал 2020 року",
        fontsize=22,
        weight="bold",
        alpha=0.95,
    )
    plt.subplots_adjust(top=0.96)
    if save:
        plt.savefig(
            FIGURES / f"00_index_ranking_v3.{FORMAT}",
            dpi=300,
            bbox_inches="tight",
            pad_inches=0.3,
            transparent=False,
        )
    plt.show()
    plt.close()


def dynamic_rankings(df, value, value_colour, change, change_colour, save=False):
    """Створює відсортований барчарт з абсолютною оцінкою та показує
    динаміку відносно минулого кварталу.


    Parameters
    ----------
    df: pd.DataFrame
        Таблиця з розрахованим індексом
    value: pd.Series
        Колонка з абсолютною оцінкою за квартал
    value_color : pd.Series
        Колонка з кольорами для основного барчарту
    change : pd.Series
        Колонка з різницею абсолютної оцінки відносно минулого кварталу
    change_colour: pd.Series
        Колонка з кольорами для точкової діаграми
    save: bool, defaults `False`
        Чи слід зберігати зображення в ``reports/figures``
    """
    OFFSETS = {"min": 2.3, "max": 0.3, "xlim_min": -10, "xlim_max": 10}

    fig, (ax1, ax2) = plt.subplots(
        nrows=1,
        ncols=2,
        figsize=(22, 10),
        sharey=True,
        gridspec_kw={
            "wspace": 0,
            "width_ratios": [3, 1],
        },
    )

    ax1.spines["top"].set_color("none")
    ax1.spines["left"].set_color("none")
    ax1.spines["right"].set_color("none")

    # rankings
    ax1.barh(df["region"], df[value], color=df[value_colour])
    ax1.barh(
        df["region"],
        df[value].max() - df[value],
        left=df[value],
        color="gray",
        alpha=0.1,
    )
    for idx in df.index:
        ax1.annotate(
            df.loc[idx, value].round(2),
            xy=(df.loc[idx, value] - 2.2, df.loc[idx, "region"]),
            c="white",
            va="center",
            weight="bold",
        )

    # dynamics
    ax2.axvline(0, color="gray", alpha=0.5)
    ax2.hlines(df["region"], 0, df[change], color="gray", alpha=0.5)
    ax2.scatter(df[change], df["region"], color=df[change_colour])
    for idx in df.index:
        data = df.loc[idx, change]
        xpos = data - OFFSETS.get("min") if data < 0 else data + OFFSETS.get("max")
        ax2.annotate(data.round(2), xy=(xpos, df.loc[idx, "region"]))

    # axes
    ax2.set_xlim(OFFSETS.get("xlim_min"), OFFSETS.get("xlim_max"))
    ax1.set_title(
        "Абсолютна оцінка області за сукупністю показників", loc="left", style="italic"
    )
    ax2.set_title(
        "Зміна абсолютної оцінки відносно минулого кварталу",
        loc="right",
        style="italic",
    )
    ax2.axes.set_axis_off()

    fig.suptitle(
        "Індекс оцінки ОДА за 3 квартал 2020 року",
        fontsize=22,
        weight="bold",
        alpha=0.95,
    )
    if save:
        plt.savefig(
            FIGURES / "ranking_with_dynamics.jpeg",
            dpi=300,
            bbox_inches="tight",
            pad_inches=0.3,
            transparent=False,
        )
    plt.show()
    plt.close()


def draw_boxplot(ax, data, numbers):
    """Створює boxplot


    Parameters
    ----------
    ax: matplotlib.axes._subplots.AxesSubplot
        Тло візуалізації
    data: pd.DataFrame
        Таблиця з розрахованим індексом
    numbers: list
        Перелік колонок, які слід ігнорувати
    """
    ax.boxplot(data.values, vert=False, sym="")
    for index, col in enumerate(data, start=1):
        if col not in numbers:
            arr = data[col]
            y_noise = np.zeros_like(arr)
            y_noise[
                :,
            ] = index
            ax.scatter(arr.values, y_noise, alpha=0.5, color="#007f86", s=10)


def draw_boxplot_dist(df_index, cols, save=False):
    """Створює зображення з розподілом показників нижнього рівня.
    Обгортка для `draw_boxplot`


    Parameters
    ----------
    df_index: pd.DataFrame
        asd
    cols: list[str]
        asd
    reg_index: int
        asd
    save: bool, defaults `False`
        asd
    """

    numbers = [*range(10)]

    x_labels = [dict_labels[col] for col in cols]
    total = len(x_labels)
    sub_cols = 4
    sub_rows = ceil(total / sub_cols)

    fig = plt.figure(figsize=(22, 10))
    counter = 0
    for r in range(sub_rows):
        for c in range(sub_cols):
            title = x_labels[counter]
            counter += 1

            df_cur = df_index.loc[:, df_index.columns.str.contains(f"p{counter}")]
            df_cur = df_cur[df_cur.columns.sort_values(ascending=False)]
            if df_cur.shape[1] < 10:
                df_empty = pd.concat(
                    [
                        pd.Series(np.zeros(df_cur.shape[0]))
                        for i in range(10 - len(df_cur.columns))
                    ],
                    axis=1,
                )
                df_all = pd.concat([df_empty, df_cur], axis=1)
            else:
                df_all = df_cur

            ax = plt.subplot2grid((sub_rows, sub_cols), (r, c))
            delete_frame(ax)
            draw_boxplot(ax, df_all, numbers)
            ax.set_yticklabels(["" if i in numbers else i for i in df_all.columns])
            ax.set_title(title, pad=17)

    title = "Розподіл значень за показниками нижнього рівня"
    fig.suptitle(title, fontsize=22, weight="bold", alpha=0.95)
    plt.subplots_adjust(top=0.89, wspace=0.3, hspace=0.3)
    if save:
        plt.savefig(
            FIGURES / f"01_params_dist.{FORMAT}",
            dpi=300,
            bbox_inches="tight",
            pad_inches=0.3,
            transparent=False,
        )
    plt.show()
    plt.close()
