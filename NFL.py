import pandas as pd
import numpy as np

def rename_columns(df):
    df = df.rename(columns={
        'Tm':'Team',
        'W':'Wins',
        'L':'Losses',
        'W-L%':'Winning %',
        'PF':'Points For',
        'PA':'Points Against',
        'PD':'Points Differential',
        'MV':'Margin of Victory',
        'SoS':'Strength of Schedule',
        'SRS':'Simple Rating System',
        'OSRS':'Offense SRS',
        'DSRS':'Defense SRS'
    })
    return df

def made_playoffs(df):
    df['Wild Card'] = np.where(df['Team'].str.contains(r'\+'), 'Yes', 'No')
    df['Division Winner'] = np.where(df['Team'].str.contains(r'\*'), 'Yes', 'No')
    df['Made Playoffs'] = np.where(df['Team'].str.contains(r'[*+]'), 'Yes', 'No')
    return df

def clean_names(df):
    df['Team'] = df['Team'].str.replace(r'[*+]', '', regex=True)
    return df

def get_file_data(year, league):
    file_name = f'season data/{year} - {league}.csv'
    df = pd.read_csv(file_name)
    df = rename_columns(df)
    df = made_playoffs(df)
    df = clean_names(df)
    return df

def made_divisonal_series(df, year):
    playoffs = pd.read_csv(f'season data/{year} - playoffs.csv')
    made_divisional_teams = playoffs.loc[
        (playoffs['Week'] == 'Division'),
        ['Winner/tie', 'Loser/tie']
    ].values.flatten()
    df['Made Divisonal Series'] = np.where(df['Team'].isin(made_divisional_teams), 'Yes', 'No')
    return df

def made_conference_finals(df, year):
    playoffs = pd.read_csv(f'season data/{year} - playoffs.csv')
    made_conf_teams = playoffs.loc[
        (playoffs['Week'] == 'ConfChamp'),
        ['Winner/tie', 'Loser/tie']
    ].values.flatten()
    df['Made Conference Finals'] = np.where(df['Team'].isin(made_conf_teams), 'Yes', 'No')
    return df

def made_superbowl(df, year):
    playoffs = pd.read_csv(f'season data/{year} - playoffs.csv')
    made_superbowl_teams = playoffs.loc[
        (playoffs['Week'] == 'SuperBowl'),
        ['Winner/tie', 'Loser/tie']
    ].values[0]
    df['Made Super Bowl'] = np.where(df['Team'].isin(made_superbowl_teams), 'Yes', 'No')
    return df

def won_superbowl(df, year):
    playoffs = pd.read_csv(f'season data/{year} - playoffs.csv')
    superbowl_winner = playoffs.loc[
        (playoffs['Week'] == 'SuperBowl'),
        'Winner/tie'
    ].values
    df['Won Super Bowl'] = np.where(df['Team'].isin(superbowl_winner), 'Yes', 'No')
    return df

def off_def_ranks(df):
    df['Offense Rank'] = df['Points For'].rank(method='first', ascending=False).astype('int64')
    df['Defense Rank'] = df['Points Against'].rank(method='first', ascending=True).astype('int64')
    df['Combined Rank'] = (df['Offense Rank'] + df['Defense Rank'])/2
    return df

def combine_nfc_afc_data(year):
    afc = get_file_data(year, 'afc')
    nfc = get_file_data(year, 'nfc')
    df = pd.concat([afc, nfc])
    df = df.reset_index(drop=True)
    df = off_def_ranks(df)
    df = made_divisonal_series(df, year)
    df = made_conference_finals(df, year)
    df = won_superbowl(df, year)
    df = made_superbowl(df, year)
    df['Season'] = year
    df = df[['Season' ,'Team', 'Points For', 'Points Against', 'Offense Rank', 'Defense Rank', 'Combined Rank', 'Made Playoffs', 'Division Winner', 'Wild Card', 'Made Divisonal Series', 'Made Conference Finals', 'Made Super Bowl', 'Won Super Bowl']]
    return df

def get_data_multiple_years(start, end):
    dfs = pd.DataFrame()
    for year in range(start, end+1):
        df = combine_nfc_afc_data(year)
        dfs = pd.concat([dfs, df])
    return dfs

final_df = get_data_multiple_years(2000, 2023)

final_df.loc[final_df['Made Super Bowl']=='Yes']