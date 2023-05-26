import sqlite3
import pandas as pd

import plotly.express as px


def get_df_from_database():
    connection = sqlite3.connect('testDB.db')
    df = pd.read_sql_query('SELECT * FROM sources', connection)
    connection.close()
    return df


def get_color_discrete_map(df):
    colors_dict = df[['reason', 'color']]. \
                    drop_duplicates(). \
                    set_index('reason')['color']. \
                    to_dict()
    return colors_dict


def get_base_info(df):
    base_info = {}
    base_info['client_name'] = df['client_name'].unique()[0]
    base_info['shift_day'] = df['shift_day'].unique()[0]
    base_info['endpoint_name'] = df['endpoint_name'].unique()[0]
    state_begin = df['state_begin'].min().split(' ')
    state_end = df['state_end'].max().split(' ')
    base_info['begin'] = beautiful_date(state_begin)
    base_info['end'] = beautiful_date(state_end)
    return base_info


def beautiful_date(some_state):
    date, time = some_state[0], some_state[1]
    date = date.split('-')[::-1]
    new_date = '.'.join(date)
    time = time[:-4]
    beautiful_date = f'{time} ({new_date})'
    return beautiful_date


def get_pie_fig(df):
    dff = df. \
            groupby(['reason', 'color'], as_index=False). \
            aggregate({'duration_hour': 'sum'}). \
            sort_values(by='duration_hour', ascending=False)

    colors_list = dff.color.to_list()

    fig = px.pie(
        dff, values='duration_hour',
        names='reason', color='color',
        color_discrete_sequence=colors_list,
        labels={
            'reason': 'Состояние',
            'duration_hour': 'Продолжительность состояния \
                              в часах за все время',
            'color': 'цвет состояния'
        },
    )
    return fig


def get_timeline_fig(df):
    fig = px.timeline(
        df, x_start='state_begin',
        x_end='state_end', color='reason',
        y="endpoint_name", color_discrete_map=get_color_discrete_map(df),
        hover_data=[
            'state', 'reason', 'duration_min',
            'operator', 'shift_name', 'shift_day'
        ],
        labels={
            'state': 'Состояние',
            'reason': 'Причина',
            'state_begin': 'Начало',
            'state_end': 'Конец',
            'duration_min': 'Длительность',
            'shift_day': 'Сменный день',
            'shift_name': 'Смена',
            'operator': 'Оператор',
            'endpoint_name': 'Точка учета'
        }
    )
    return fig
