import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def plot_heatmap(ax, df):
    """
    Plot a heatmap on the given axes using the provided DataFrame.

    Parameters:
    ax (matplotlib.axes.Axes): The axes on which to plot the heatmap.
    df (pandas.DataFrame): The DataFrame containing the data to be plotted.

    Returns:
    matplotlib.axes.Axes: The modified axes object with the heatmap plot.
    """
    types = df['AMR'].unique()
    color_map = {0: '#41B6C4', 1: '#C7E9B4', -1: '#0C2C84'}

    # Map each unique 'WF' value to a unique integer
    y_values = df['WF'].unique()
    y_map = {y: i for i, y in enumerate(y_values)}
    df['WF'] = df['WF'].map(y_map)

    for i, type_ in enumerate(types):
        d = df[df["AMR"] == type_]
        y = d["WF"]
        x = [i] * len(y)
        color = d["Value"].map(color_map)
        ax.scatter(x, y, color=color, s=2000)  # Increase size of circles

        # Add text for each dot
        for xi, yi, value in zip(x, y, d["Value"]):
            ax.text(xi, yi, str(value), ha='center', va='center', color='white', fontsize=20)  # Decrease fontsize to 20

    ax.set_frame_on(False)
    ax.set_axisbelow(True)
    ax.set_xticks(np.arange(len(types)))
    ax.set_xticklabels(types, rotation=45, fontsize=20, fontdict={'fontstyle':'italic'})  # Set fontstyle to italic
    ax.set_yticks(np.arange(len(y_values)))
    ax.set_yticklabels(y_values, fontsize=20)  # Increase fontsize to 18
    ax.tick_params(size=0, colors="0.3")
    ax.set_xlabel("Workflow Comparison", loc="right")
    ax.yaxis.set_label_coords(-0.1,0.5)  # Move y-axis closer to the graph
    ax.set_ylim(-1, len(y_values))  # Adjust y-axis limits

    return ax

df = pd.read_csv('YourData.csv')
fig, ax = plt.subplots(figsize=(40, 8))  # Adjust figure height
plot_heatmap(ax, df)
plt.subplots_adjust(left=0.1)  # Adjust the left margin
plt.savefig('heatmap.png', dpi=300, bbox_inches='tight')  # Save figure in high resolution
plt.show()