import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def load_data(filepath):
    df = pd.read_csv(filepath)
    df['datetime'] = pd.to_datetime(df['time'], unit='s')
    df.set_index('datetime', inplace=True)
    df = df.drop(columns=['time'], errors='ignore')
    return df

def calculate_default_levels(df, window_periods, shift_periods):
    shifted_high = df['high'].shift(periods=shift_periods)
    df['default_res'] = shifted_high.rolling(window=window_periods).max()
    shifted_low = df['low'].shift(periods=shift_periods)
    df['default_sup'] = shifted_low.rolling(window=window_periods).min()
    return df

def generate_signals(df):
    df['long_signal'] = np.where(df['close'] < df['default_sup'].shift(1), df['close'], np.nan)
    df['short_signal'] = np.where(df['close'] > df['default_res'].shift(1), df['close'], np.nan)
    return df

def plot_results(df):
    plt.figure(figsize=(15, 8))
    ax = plt.gca()

    df['open'].plot(ax=ax, style='b-', drawstyle='steps-post', label='Open Price', alpha=0.7)
    df['default_res'].plot(ax=ax, style='r--', drawstyle='steps-post', label='Pseudo Resistance')
    df['default_sup'].plot(ax=ax, style='g--', drawstyle='steps-post', label='Pseudo Support')
    df['long_signal'].plot(ax=ax, style='g^', markersize=8, label='Long Signal (Breakout)', linewidth=0)
    df['short_signal'].plot(ax=ax, style='rv', markersize=8, label='Short Signal (Breakdown)', linewidth=0)

    plt.title('Market Data with Pseudo Support/Resistance & Signals')
    plt.xlabel('Time')
    plt.ylabel('Price')
    plt.legend(title='Legend', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True)
    plt.tight_layout(rect=[0, 0, 0.8, 1]) 

    plt.show()

if __name__ == '__main__':
    
    window_periods = 60
    shift_periods = 1
    csv_filepath = 'bit2.csv'

    df = load_data(csv_filepath)
    df = calculate_default_levels(df, window_periods, shift_periods)
    df = generate_signals(df)
    plot_results(df)