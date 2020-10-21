# -*- coding: utf-8 -*-
""" 
API для візуалізацій, модифікований код Остапа з версії за 2 квартал 2020 року.
"""
import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt 
from matplotlib import rcParams, gridspec
from math import ceil, pi
from utils import ROOT


MAX_PARAMS = 10
FIGURES = ROOT / "reports" / "figures"
dict_labels = {
        'P1':'економіка',
        'P2':'бюджет',
        'P3':'приватизація',
        'P4':'будівництво',
        'P5':'екологія',
        'P6':"освіта та здоров'я",
        'P7':'соцзахист',
        'P8':'праця'
    }


def delete_frame(ax):
    ax.spines['top'].set_color('none')
    ax.spines['bottom'].set_color('none')
    ax.spines['left'].set_color('none')
    ax.spines['right'].set_color('none')


def draw_spider(ax,angles,values,values_mean,cols):
    """ """
    rot_angles = [0,-45,90,45,0,-45,90,45,0]
    
    ax.set_rlabel_position(0)
    ax.set_theta_offset(pi / 2)
    ax.set_theta_direction(-1)

    yticks = [*range(0,12,2)]
    locs, labels = plt.xticks(angles[:-1], cols, color='grey', size=10,rotation=90)
    plt.yticks(yticks, [])
    
    plt.grid(color='#E8E8E8')
    ax.axis([0, angles[-1], 0, 10])
    ax.fill(angles, values_mean, color='gray', alpha=0.05)
    ax.plot(angles, values, linewidth=1, linestyle='solid',color='#2f3f60')
    for i,j in zip(angles,values):
        ax.annotate(str(round(j,1)),xy=(i,j+1.3), ha='center', va='center')
    
    
    plt.gcf().canvas.draw()
    for label, angle in zip(labels, rot_angles):
        x,y = label.get_position()
        ax.text(x,y, label.get_text(), transform=label.get_transform(),
                      ha=label.get_ha(), va=label.get_va(), color='grey', rotation=angle)
    ax.set_xticklabels([])


def draw_multiple_spiders(df_index, cols, save=False):
    """ """
    rcParams['font.size'] = 7
    N = len(cols)
    angles = [n / float(N) * 2 * pi for n in range(N)]
    angles.append(2 * pi)

    values_mean = [*df_index[cols].mean()]
    values_mean.append(values_mean[0])
    x_labels = [dict_labels[col] for col in cols]

    total = df_index.shape[0]
    sub_cols = 8
    sub_rows = ceil(total/sub_cols)

    fig = plt.figure(figsize=(20,10))
    
    counter = 0
    for r in range(sub_rows):
        for c in range(sub_cols):
            values = list(df_index.loc[counter,cols])
            values.append(values[0])
            title = df_index.loc[counter,'region']
            counter += 1
            if counter <= total:
                ax = plt.subplot2grid((sub_rows,sub_cols), (r,c), polar=True)
                draw_spider(ax, angles, values, values_mean, x_labels)
                ax.set_title(title, pad=17, fontsize=9)

    plt.subplots_adjust(wspace = 0.45, hspace = 0.45)
    if save:
        plt.savefig(
            FIGURES / '00_index_gen_v3.jpeg', 
            dpi=300, bbox_inches='tight', 
            pad_inches=0.3, transparent=False
        )


def draw_profile_gen(df, cols, reg_index, save=False):
    """ """
    rcParams['font.size'] = 12
    fig = plt.figure(figsize=(6,4))
    
    values_mean = df_index[cols].mean().sort_index(ascending=False)
    values = df_index.loc[reg_index,cols].sort_index(ascending=False)
    x_labels = [dict_labels[col] for col in cols]
    x_labels.reverse()
    title = df_index.loc[reg_index,'region']

    colors = []
    for i in range(values_mean.shape[0]):
        if values[i] >= values_mean[i]:
            colors.append('#007f86')
        elif values[i] < values_mean[i]:
            colors.append('#a3550f')

    ax = plt.subplot(111)
    delete_frame(ax)

    for ind in range(values_mean.shape[0]):
        ax.plot([values_mean[ind],values[ind]],[values_mean.index[ind],values_mean.index[ind]],color='black',zorder=0)
        diff = values[ind]-values_mean[ind]
        ax.annotate(str(round(diff,1)),xy=(values[ind]-diff/2,ind+0.35), ha='center', va='center',color=colors[ind],fontsize=8)
        ax.annotate(str(round(values[ind],1)),xy=(values[ind],ind-0.4), ha='center', va='center',fontsize=8)

    ax.scatter(values_mean,values_mean.index,color='gray',zorder=1,s=35)
    ax.scatter(values,values.index,color=colors,zorder=2,alpha=1,s=35)

    #ax.set_title(title+' область',pad=10)
    ax.set_yticklabels(x_labels)
    ax.set_xlim(0,10)
    ax.set_ylim(-1,8)
    ax.set_xlim(-1,11)

    if save:
        plt.savefig(
            FIGURES / f'01_region_profile_gen_{reg_index}.jpeg',
            dpi=300, bbox_inches='tight', pad_inches=0.3,
            transparent = False
        )

    plt.show()
    plt.close()
    

def draw_profile_det(df,cols,reg_index, save=False):
    """ """    
    rcParams['font.size'] = 12

    x_labels = [dict_labels[col] for col in cols]
    total = len(x_labels)
    sub_cols = 4
    sub_rows = ceil(total/sub_cols)

    fig = plt.figure(figsize=(22,10))
    counter = 0
    for r in range(sub_rows):
        for c in range(sub_cols):
            title = x_labels[counter]
            counter += 1
            if counter <= total:
                cols_lower = df_index.loc[:,df_index.columns.str.contains('p'+str(counter))].columns
                values_mean = df_index[cols_lower].mean().sort_index(ascending=False)
                values_mean_all = list(np.zeros(MAX_PARAMS-values_mean.shape[0]))+list(values_mean)
                index_labels_all = ['' for i in range(MAX_PARAMS-values_mean.shape[0])]+list(values_mean.index)
                values_reg = df_index.loc[reg_index,cols_lower].sort_index(ascending=False)
                values_reg = values_reg.map(lambda x: x+0.0000001 if x==0 else x)
                values_reg_all = list(np.zeros(MAX_PARAMS-values_reg.shape[0]))+list(values_reg)

                colors = []
                for i in range(len(values_mean_all)):
                    if values_reg_all[i] >= values_mean_all[i]:
                        colors.append('#007f86')
                    elif values_reg_all[i] < values_mean_all[i]:
                        colors.append('#a3550f')

                ax = plt.subplot2grid((sub_rows,sub_cols), (r,c))
                delete_frame(ax)
                for ind in range(len(values_mean_all)):
                    ax.plot([values_mean_all[ind],values_reg_all[ind]],[ind,ind],color='black',zorder=0)
                    if values_reg_all[ind]>0:
                        diff = values_reg_all[ind]-values_mean_all[ind]
                        ax.annotate(str(round(diff,2)),xy=(values_reg_all[ind]-diff/2,ind+0.3), ha='center', va='center',color=colors[ind],fontsize=8)
                        ax.annotate(str(round(values_reg_all[ind],2)),xy=(values_reg_all[ind],ind-0.35), ha='center', va='center',fontsize=8)
                ax.scatter(values_mean_all,[i for i in range(MAX_PARAMS)],s=[i if i==0 else 35 for i in values_mean_all],color='gray',zorder=1)
                ax.scatter(values_reg_all,[i for i in range(MAX_PARAMS)],s=[i if i==0 else 35 for i in values_reg_all],color=colors,zorder=2)
                ax.set_yticks([i for i in range(10)])
                ax.set_yticklabels(index_labels_all)
                ax.set_xlim(-0.1,1.1)
                ax.set_title(title,pad=17)

    title = df_index.loc[reg_index,'region'] + ' область: загальний профіль'
    fig.suptitle(title, fontsize=22, weight='bold', alpha=0.95)
    plt.subplots_adjust(top=0.89, wspace=0.3, hspace=0.3)
    if save:
        plt.savefig(
            FIGURES / f'02_region_profile_det_{reg_index}.jpeg',
            dpi=300, bbox_inches='tight', pad_inches=0.3,
            transparent = False
        )
    plt.show()
    plt.close()


def draw_rankings(df_index, kvartal="III", save=False):
    """ """
    fig = plt.figure(figsize=(22,10))
    ax = plt.subplot(111)
    delete_frame(ax)
    
    df_index_hist = df_index[['region','I']].sort_values(by='I').reset_index(drop=True)
    
    colors = ['#a3550f','#f2dd05','#007f86']
    colors_list = [colors[0] for r in range(3)] + [colors[1] for y in range(df_index_hist.shape[0]-6)] + [colors[2] for g in range(3)]

    ax.barh(df_index_hist['region'], df_index_hist['I'],color=colors_list)
    for i in df_index_hist.index:
        ax.annotate(int(df_index_hist.loc[i,'I']),xy=(df_index_hist.loc[i,'I']-2.2,df_index_hist.loc[i,'region']), c='white', va='center')
        ax.set_xlim(0,100)
    
    fig.suptitle(f'Індекс оцінки ОДА за {kvartal} квартал 2020 року', fontsize=22, weight='bold', alpha=0.95)
    plt.subplots_adjust(top=0.96)
    if save:
        plt.savefig(
            FIGURES / '00_index_ranking_v3.jpeg',
            dpi=300, bbox_inches='tight', pad_inches=0.3,
            transparent = False
        )
    plt.show()
    plt.close()


def draw_boxplot(ax, data, numbers):    
    """ Boxplot with points. """
    ax.boxplot(data.values, vert=False, sym='')
    for index, col in enumerate(data, start=1):
        if col not in numbers:
            arr = data[col]
            y_noise = np.zeros_like(arr)
            y_noise[:,] = index
            ax.scatter(arr.values, y_noise, alpha=0.5, color='#007f86', s=10)


def draw_boxplot_dist(df, cols, save=False):
    """ """
    
    numbers = [*range(10)]
    x_labeles = [dict_labels[col] for col in cols]
    
    x_labels = [dict_labels[col] for col in cols]
    total = len(x_labels)
    sub_cols = 4
    sub_rows = ceil(total/sub_cols)
    
    fig = plt.figure(figsize=(22,10))
    counter = 0
    for r in range(sub_rows):
        for c in range(sub_cols):
            title = x_labels[counter]
            counter += 1
            
            df_cur = df_index.loc[:,df_index.columns.str.contains(f"p{counter}")]
            df_cur = df_cur[df_cur.columns.sort_values(ascending=False)]
            if df_cur.shape[1]<10:
                df_empty = pd.concat([pd.Series(np.zeros(df_cur.shape[0])) for i in range(10-len(df_cur.columns))],axis=1)
                df_all = pd.concat([df_empty,df_cur],axis=1)
            else:
                df_all = df_cur
            
            ax = plt.subplot2grid((sub_rows,sub_cols), (r,c))
            delete_frame(ax)
            draw_boxplot(ax, df_all, numbers)
            ax.set_yticklabels(['' if i in numbers else i for i in df_all.columns])
            ax.set_title(title,pad=17)
    
    title = 'Розподіл значень за показниками нижнього рівня'
    fig.suptitle(title, fontsize=22, weight='bold', alpha=0.95)
    plt.subplots_adjust(top=0.89, wspace=0.3, hspace=0.3)
    if save:
        plt.savefig(
            FIGURES / '01_params_distr.jpeg',
            dpi=300, bbox_inches='tight', pad_inches=0.3,
            transparent = False
        )
    plt.show()
    plt.close()


# def example(path):
#     df_index = pd.read_csv(path)
#     cols = df_index.loc[:,df_index.columns.str.contains('P')].columns

#     draw_multiple_spiders(df_index, cols, save=True)
#     draw_profile_gen(df_index, cols, 0, save=True)
#     draw_profile_det(df_index, cols, 0, save=True)
#     draw_boxplot_dist(df_index, cols, save=True)
#     draw_rankings(df_index, save=True)