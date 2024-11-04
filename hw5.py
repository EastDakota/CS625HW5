import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

# Setting up Global Variables
DATASET="https://www2.census.gov/library/publications/2010/compendia/statab/130ed/tables/11s0012.xls"
GLOBAL_BASIC_INFO = ['State', 'Post office abbreviation', '2-digit ANSI code']
plt.rcParams['figure.figsize']=(8,8)


def refine_data(df):
    # Making local copy to manipulate
    local_df = df.copy()
    
    column_names = list(local_df.iloc[2])
    for i, name in enumerate(column_names):
        if "(" in name:
            column_names[i] = name[:name.find("(")-1]
    local_df.columns = column_names
    
    # Rip out formatting made by people who hate Computer Scientists
    # https://sparkbyexamples.com/pandas/pandas-drop-first-three-rows-of-a-dataframe/#:~:text=drop()%20to%20Delete%20First,directly%20to%20the%20existing%20DataFrame.
    local_df = local_df[3:]
    local_df = local_df[local_df['1995'] > 0]
    local_df = local_df[local_df['2-digit ANSI code'] != '(X)']
    
    # Dropping 'United States' and 'District of Columbia' from list of states
    local_df.drop(local_df.index[local_df['2-digit ANSI code'] == '00'], inplace=True)
    local_df.drop(local_df.index[local_df['2-digit ANSI code'] == '11'], inplace=True)

    # Resetting index
    local_df.reset_index(inplace=True)
    local_df.drop('index', axis=1, inplace=True)
    return local_df

def render(title):
    plt.get_current_fig_manager().window.geometry(("+100+100"))
    plt.tight_layout()
    plt.savefig(title)
    plt.show()
    plt.clf()
    
def question1(df):
    query_info = ['1970', '1985', '1995', '2009']
    basic_info = GLOBAL_BASIC_INFO.copy()
    basic_info.extend(query_info)
    
    requested_columns = df[basic_info]

    #
    # CREATING THE PLOT (USING SEABORN)
    #
    
    sns.boxplot(data=requested_columns)
    
    # Plot Formatting
    X_TITLE = "Year"
    Y_TITLE = "Distribution of Populations among states"
    PLOT_TITLE = f"{Y_TITLE} by {X_TITLE}"
    plt.title(PLOT_TITLE)
    plt.xlabel(X_TITLE)
    plt.ylabel(Y_TITLE)
    render('Distribution_of_Populations_among_states_Years-1970-1985-1995-2009.png')

def question2(df, num_bins=25):
    # Copying data
    local_df = df.copy()
    
    # Creating query and defining dataframe based on query
    requested_year = '1960'
    query = GLOBAL_BASIC_INFO.copy()
    query.append(requested_year)
    local_df = local_df[query]    
    
    #
    # Defining the plot (USING SEABORN)
    #
    sns.histplot(data=local_df[requested_year], bins=num_bins, color='blue', edgecolor='black')
    
    #
    # Plot Formatting
    #
    
    # Defining axis labels and title
    X_TITLE = "Population"
    Y_TITLE = "Number of states that fall within each bin"
    PLOT_TITLE = f"{Y_TITLE} by {X_TITLE} in {requested_year}"
    
    # Setting title and axis labels
    plt.title(PLOT_TITLE)
    plt.xlabel(X_TITLE)
    plt.ylabel(Y_TITLE)

    # Setting x and y label sets
    plt.xticks(list(np.histogram(np.asarray(local_df[requested_year]), bins=num_bins)[1]), rotation=68)
    plt.yticks(list(range(0,14)))
    render('Population_Histogram_in_1960.png')

def question3(df):
    # Copying data
    local_df = df.copy()
    query_info = ['1960', '2009']
    basic_info = GLOBAL_BASIC_INFO.copy()
    basic_info.extend(query_info)
    local_df = local_df[basic_info]
    X_LABEL = "Cumulative Frequency of observed population"
    Y_LABEL = "Population"
    PLOT_TITLE = "Cumulative Distribution Frequency of Population among States 1960 and 2009"
    sns.ecdfplot(y=local_df[query_info[0]], label=str(query_info[0]))
    sns.ecdfplot(y=local_df[query_info[1]], label=str(query_info[1]))    
    
    plt.title(PLOT_TITLE)
    plt.xlabel(X_LABEL)
    plt.ylabel(Y_LABEL)
    plt.legend(title='Year')
    render("Cumulative_Distribution_Frequency_of_Population_among_States_1960_and_2009.png")

# Average rate of change of population growth
def exploration1(df):
    # Filter out non-decade columns
    decade_columns = [col for col in df.columns if col.isdigit()]
    df_decades = df[['State'] + decade_columns].copy()
    
    # Calculate the decade-over-decade percentage change
    df_pct_change = df_decades.set_index('State').pct_change(axis=1) * 100
    
    # Calculate the average growth rate per state across all available decades
    avg_growth_rate = df_pct_change.mean(axis=1).sort_values()
    
    # Select the top 5 and bottom 5 states by average growth rate
    top_5_states = avg_growth_rate.tail(10)
    bottom_5_states = avg_growth_rate.head(10)
    
    # Prepare data for plotting
    growth_summary = pd.concat([top_5_states, bottom_5_states]).reset_index()
    growth_summary.columns = ['State', 'Avg_Growth_Rate']
    growth_summary = growth_summary.sort_values(by='Avg_Growth_Rate', ascending=False)
    growth_summary['Avg_Growth_Rate'] = round(growth_summary['Avg_Growth_Rate'], 3)
    
    # # Plotting the top 5 and bottom 5 states by average growth rate
    plt.figure(figsize=(12, 8))
    
    # https://www.geeksforgeeks.org/how-to-show-values-on-seaborn-barplot/
    ax = sns.barplot(data=growth_summary, x='Avg_Growth_Rate', y='State', palette="coolwarm", hue='State')
    for i in ax.containers:
        ax.bar_label(i,)

    plt.title('Top 5 and Bottom 5 States by Average Population Growth Rate (1960-Present)')
    plt.xlabel('Average Growth Rate (%)')
    plt.ylabel('State')
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    render('Top_5_and_Bottom_5_States_by_Average_Population_Growth_Rate_(1960-Present).png')
    


# Rate of population change vs Population size in the 10 largest states
def exploration2(df):
    largest_states = ['Alaska', 'Texas']
    # print(df)
    # df_a = df[df['State'].isin(largest_states)]
    
    # Filter out non-decade columns
    top_pop_2009 = (sorted(list(df['2009']))[::-1])[0:10]
    pop_cutoff = top_pop_2009[9] - 1
    df_top_states_2009 = df[df['2009'] > pop_cutoff]
    decade_columns = [col for col in df_top_states_2009.columns if col.isdigit()]
    df_decades = df_top_states_2009[['State'] + decade_columns].copy()
    
    top_pop_1960 = (sorted(list(df['1960']))[::-1])[0:10]
    pop_cutoff = top_pop_1960[9] - 1
    df_top_states_1960 = df[df['1960'] > pop_cutoff]
    decade_columns = [col for col in df_top_states_1960.columns if col.isdigit()]
    df_decades = df_top_states_1960[['State'] + decade_columns].copy()
    
    print(df_top_states_1960['State'])
    print(df_top_states_2009['State'])
    
    
    
###
### Main Driver
###
def main():
    # Reading in and formatting data
    df = pd.read_excel(DATASET)
    df = refine_data(df)
    
    # Part 1: Three Charts
    question1(df)
    question2(df)
    question3(df)

    # Part 2: Exploration
    exploration1(df)
    # exploration2(df)
    
if __name__ == "__main__":
    main()