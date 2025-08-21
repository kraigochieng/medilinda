from typing import List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from IPython.display import display
# def categorical_eda(df: pd.DataFrame, columns: List):
#     for column in columns:
#         print(column)
#         df__categorical_count = df.groupby(column).size().reset_index(name="count")

#         # print(":" * 25)
#         # print(df[column].value_counts(normalize=True).round(3))
#         sns.barplot(data=df__categorical_count, y=column, x="count", orient="h")
#         plt.show()


def categorical_eda(df: pd.DataFrame, columns: List[str], target_column=str):
    for column in columns:
        df__categorical_count = df.groupby(column).size().reset_index(name="count")

        
        df__categorical_count_per_target = pd.crosstab(
            df[column], df[target_column], normalize="index"
        )

        display(df__categorical_count_per_target)
        # df__categorical_count_per_target = df__categorical_count_per_target.loc[df__categorical_count[column]]

        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        sns.barplot(
            data=df__categorical_count, y=column, x="count", ax=axes[0], orient="h"
        )
        axes[0].set_title(f"Count of {column}")
        axes[0].set_xlabel("Count")
        axes[0].set_ylabel(column)

        df__categorical_count_per_target.plot(kind="barh", stacked=True, ax=axes[1])

        axes[1].set_title(f"Proportion of {column} by {target_column}")
        axes[1].set_xlabel("Count")
        axes[1].set_ylabel(column)
        # To maintain ordering
        axes[1].invert_yaxis()

        plt.tight_layout()

        # Show the plots
        plt.show()


def numerical_eda(df: pd.DataFrame, columns: List[str], target_column: str):
    for column in columns:
        fig, axes = plt.subplots(1, 3, figsize=(14, 6))

        q1 = df[column].quantile(0.01)
        q3 = df[column].quantile(0.99)

        filtered_df = df[(df[column] >= q1) & (df[column] <= q3)]

        sns.kdeplot(data=filtered_df, x=column, ax=axes[0], fill=True)

        axes[0].set_title(f"Distribution of {column}")

        sns.kdeplot(
            data=filtered_df,
            x=column,
            hue=target_column,
            ax=axes[1],
            common_norm=False,
            fill=True,
        )