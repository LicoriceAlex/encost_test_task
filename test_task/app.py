from dash import html, Output, Input, State, dcc
from dash_extensions.enrich import (DashProxy,
                                    ServersideOutputTransform,
                                    MultiplexerTransform)
import dash_mantine_components as dmc

from services import (get_base_info, get_df_from_database,
                      get_pie_fig, get_timeline_fig)

df = get_df_from_database()
base_info = get_base_info(df)


dropdown_filter = dcc.Dropdown(
    id='reason_filter',
    options=sorted(df.reason.unique().tolist()),
    placeholder='Выберите причину состояния оборудования и нажмите кнопку \
                 (по умолчанию будут выбраны все причины)',
    multi=True
)


TOP_CARD_STYLE = dict(
    withBorder=True,
    shadow="sm",
    radius="md",
    style={'height': '500px'}
)

LOW_CARD_STYLE = dict(
    withBorder=True,
    shadow="sm",
    radius="md",
    style={'height': '440px'}
)


class EncostDash(DashProxy):
    def __init__(self, **kwargs):
        self.app_container = None
        super().__init__(transforms=[ServersideOutputTransform(),
                                     MultiplexerTransform()], **kwargs)


app = EncostDash(name=__name__)


def get_layout():
    return html.Div([
        dmc.Paper([
            dmc.Grid([
                dmc.Col([
                    dmc.Card([
                        dcc.Markdown(f'''
                            # Клиент: {base_info.get('client_name')}
                            ### Сменный день: {base_info.get('shift_day')}
                            ### Точка учета: {base_info.get('endpoint_name')}
                            ### Начало периода: {base_info.get('begin')}
                            ### Конец периода: {base_info.get('end')}
                            '''),
                        html.Div(dropdown_filter),
                        dmc.Button(
                            'Фильтровать',
                            id='button_filter')],
                        **TOP_CARD_STYLE)
                ], span=6),
                dmc.Col([
                    dmc.Card([
                        dcc.Graph(figure=get_pie_fig(df),
                                  style={'width': '90vh', 'height': '50vh'})
                        ],
                        **TOP_CARD_STYLE)
                ], span=6),
                dmc.Col([
                    dmc.Card([
                        dcc.Graph(id='reason_timeline')],
                        **LOW_CARD_STYLE)
                ], span=12),
            ], gutter="xl",)
        ])
    ])


app.layout = get_layout()


@app.callback(
    Output(component_id='reason_timeline', component_property='figure'),
    Input(component_id='button_filter', component_property='n_clicks'),
    State(component_id='reason_filter', component_property='value'),
    prevent_initial_call=True
)
def update_reason_timeline(click, value):
    if not value:
        data_frame = df
    else:
        data_frame = df.loc[df['reason'].isin(value)]

    fig = get_timeline_fig(data_frame)
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
