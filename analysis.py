import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import re
import warnings


warnings.simplefilter("ignore", category=FutureWarning)

# ------------------------------------------------------------------------------------------

# Extraction Functions

def load_and_aggregate_data(current_dir):
    all_analysis_data = []
    all_commits_data = []
    folder_counter = 0
    for folder in os.listdir(current_dir):
        folder_path = os.path.join(current_dir, folder)
        if os.path.isdir(folder_path):
            analysis_file = os.path.join(folder_path, folder + '_analysis.csv')
            commits_file = os.path.join(folder_path, folder + '_commits.csv')
            try:
                if os.path.exists(analysis_file) and os.path.getsize(analysis_file) > 0:
                    analysis_df = pd.read_csv(analysis_file)
                    # Check if the repository has more than one contributor
                    # if analysis_df['Number of Contributors'].iloc[0] > 1:
                    all_analysis_data.append(analysis_df)
                    if os.path.exists(commits_file) and os.path.getsize(commits_file) > 0:
                        all_commits_data.append(pd.read_csv(commits_file))
                        folder_counter += 1
            except pd.errors.EmptyDataError:
                print(f"Empty or invalid data in {analysis_file} or {commits_file}")
    combined_analysis_data = pd.concat(all_analysis_data, ignore_index=True)
    combined_commits_data = pd.concat(all_commits_data, ignore_index=True)
    return combined_analysis_data, combined_commits_data, folder_counter



# ------------------------------------------------------------------------------------------

# Helper Functions

def clean_extension(extension):
    # Remove invisible or non-printable characters
    cleaned_extension = re.sub(r'\s+', '', extension)  # Removes any whitespace characters
    cleaned_extension = re.sub(r'[^\.\w]', '', cleaned_extension)  # Removes any non-word characters except for dot
    return cleaned_extension.lower()

# Reference - https://gist.github.com/mmorrison/4138298 

timezones = [
	{'name': 'MIT', 'info': 'Midway Islands Time', 'seconds': -39600},
	{'name': 'MIT', 'info': 'Hawaii Standard Time', 'seconds': -36000},
	{'name': 'AKST', 'info': 'Alaska Standard Time', 'seconds': -32400},
	{'name': 'AKDT', 'info': 'Alaska Daylight Savings Time', 'seconds': -28800},
	{'name': 'PST', 'info': 'Pacific Standard Time', 'seconds': -28800},
	{'name': 'PDT', 'info': 'Pacific Daylight Savings Time', 'seconds': -25200},
	{'name': 'MST', 'info': 'Mountain Standard Time', 'seconds': -25200, 'country': "United States"},
	{'name': 'MDT', 'info': 'Mountain Daylight Savings Time', 'seconds': -21600},
	{'name': 'CST', 'info': 'Central Standard Time', 'seconds': -21600, 'country': "United States"},
	{'name': 'CDT', 'info': 'Central Daylight Savings Time', 'seconds': -18000},
	{'name': 'EST', 'info': 'Eastern Standard Time', 'seconds': -18000},
	{'name': 'EDT', 'info': 'Eastern Daylight Savings Time', 'seconds': -14400},
	{'name': 'PRT', 'info': 'Puerto Rico and US Virgin Islands Time', 'seconds': -14400},
	{'name': 'CNT', 'info': 'Canada Newfoundland Time', 'seconds': -12600},
	{'name': 'AGT', 'info': 'Argentina Standard Time', 'seconds': -10800},
	{'name': 'BET', 'info': 'Brazil Standard Time', 'seconds': -10800},
	{'name': 'CAT', 'info': 'Central Africa Time', 'seconds': -3600},
	{'name': 'WET', 'info': 'Western European Time', 'seconds': 0},
	{'name': 'GMT', 'info': 'Greenwich Mean Time', 'seconds': 0},
	{'name': 'UTC', 'info': 'Universal Coordinated Time', 'seconds': 0},
	{'name': 'BST', 'info': 'British Summer Time', 'seconds': 3600, 'country': "United Kingdom"},
	{'name': 'WEST', 'info': 'Western European Summer Time', 'seconds': 3600},
	{'name': 'CET', 'info': 'Central European Time', 'seconds': 3600},
	{'name': 'CEST', 'info': 'Central European Summer Time', 'seconds': 7200},
	{'name': 'EET', 'info': 'Eastern European Time', 'seconds': 7200},
	{'name': 'EEST', 'info': 'Eastern European Summer Time', 'seconds': 10800},
	{'name': 'ATT', 'info': '(Arabic) Egypt Time', 'seconds': 7200},
	{'name': 'EAT', 'info': 'Eastern Africa Time', 'seconds': 10800},
	{'name': 'MET', 'info': 'Middle East Time', 'seconds': 12600},
	{'name': 'NET', 'info': 'Near East Time', 'seconds': 14400},
	{'name': 'PLT', 'info': 'Pakistan Lahore Time', 'seconds': 18000},
	{'name': 'IST', 'info': 'India Standard Time', 'seconds': 19800},
	{'name': 'BST', 'info': 'Bangladesh Standard Time', 'seconds': 21600, 'country': "Bangladesh"},
	{'name': 'CTT', 'info': 'China Taiwan Time', 'seconds': 28800},
	{'name': 'HKT', 'info': 'Hong Kong Standard Time', 'seconds': 28800},
	{'name': 'CST', 'info': 'China Standard Time', 'seconds': 28800, 'country': "China"},
	{'name': 'MST', 'info': 'Malaysia Standard Time', 'seconds': 28800, 'country': "Malaysia"},
	{'name': 'SST', 'info': 'Singapore Standard Time', 'seconds': 28800, 'country': "Singapore"},
	{'name': 'AWST', 'info': 'Australia Western Time', 'seconds': 28800},
	{'name': 'JST', 'info': 'Japan Standard Time', 'seconds': 32400},
	{'name': 'KST', 'info': 'Korea Standard Time', 'seconds': 32400},
	{'name': 'ACST', 'info': 'Australian Central Time', 'seconds': 34200},
	{'name': 'AEST', 'info': 'Australian Eastern Time', 'seconds': 36000},
	{'name': 'AEDT', 'info': 'Australian Eastern Daylight Time', 'seconds': 39600},
	{'name': 'SST', 'info': 'Solomon Standard Time', 'seconds': 39600, 'country': "Solomon"},
	{'name': 'NZST', 'info': 'New Zealand Standard Time', 'seconds': 43200},
	{'name': 'NZDT', 'info': 'New Zealand Daylight Savings Time', 'seconds': 46800}
]


# ------------------------------------------------------------------------------------------

# Visualisation Functions

def gini_coefficient_distribution(analysis_data, current_directory):
    try:
        gini_plot_path = os.path.join(current_directory, 'gini_coefficient_distribution.png')
        plt.figure()
        # Reverse the Gini Coefficient values so that 1 is the no equality and 0 is the full equality
        plt.hist((1-analysis_data['Gini Coefficient']), bins=50, color='blue', alpha=0.7, edgecolor='black')
        plt.title('Distribution of Gini Coefficients Across Repositories')
        plt.xlabel('Gini Coefficient')
        plt.ylabel('Number of Repositories')
        plt.grid(axis='y', alpha=0.75)
        plt.savefig(gini_plot_path)
        plt.close()
        print("Gini Coefficeint Plot Saved Successfully")
    except Exception as e:
        print("Gini Coefficeint Plot Failed to Save")


def contributors_distribution(analysis_data, current_directory):
    try:
        contributors_plot_path = os.path.join(current_directory, 'contributors_distribution.png')
        plt.figure(figsize=(12, 6))
        sns.histplot(analysis_data['Number of Contributors'], bins=50, kde=False)
        plt.yscale('log')
        plt.title('Distribution of Number of Contributors (Log Scale)')
        plt.xlabel('Number of Contributors')
        plt.ylabel('Log Frequency')
        plt.grid(True, which="both", ls="--", linewidth=0.5)
        plt.savefig(contributors_plot_path)
        plt.close()
        print("Contributors Plot Saved Successfully")
    except Exception as e:
        print("Contributors Plot Failed to Save")


def weekly_commits(commits_data, current_directory):
    try:
        weekly_commits_plot_path = os.path.join(current_directory, 'weekly_commits.png')
        commits_data['Author Date'] = pd.to_datetime(commits_data['Author Date'], utc=True, errors='coerce')
        commits_data.dropna(subset=['Author Date'], inplace=True)
        commits_data.set_index('Author Date', inplace=True)
        weekly_commits = commits_data.resample('W').size()
        
        plt.figure(figsize=(14, 7))
        plt.plot(weekly_commits.index, weekly_commits.values, marker='o', linestyle='-')
        plt.title('Weekly Commit Activity Over Time')
        plt.xlabel('Week')  
        plt.ylabel('Number of Commits')
        plt.grid(True)
        plt.savefig(weekly_commits_plot_path)
        plt.close()
        print("Weekly Commits Plot Saved Successfully")
    except Exception as e:
        print("Weekly Commits Plot Failed to Save")

def commit_size_distribution(commits_data, current_directory):
    try:  
        commit_size_plot_path = os.path.join(current_directory, 'commit_size_distribution.png')
        commits_data['Commit Size'] = commits_data['insertions'] + commits_data['deletions']

        plt.figure(figsize=(12, 6))
        sns.boxplot(x=commits_data['Commit Size'])
        plt.title('Distribution of Commit Sizes')
        plt.xlabel('Commit Size')
        plt.xlim(0, commits_data['Commit Size'].quantile(0.95))  # Limit x-axis to 95th percentile for better visibility
        plt.savefig(commit_size_plot_path)
        plt.close()
        print("Commit Size Plot Saved Successfully")
    except Exception as e:
        print("Commit Size Plot Failed to Save")


def geographic_diversity(commits_data, current_directory):
    try:
        geographic_diversity_plot_path = os.path.join(current_directory, 'geographic_diversity.png')
        
        # Ensure the 'Author Timezone' column is treated as categorical data for better plotting
        commits_data['Author Timezone'] = commits_data['Author Timezone'].astype('category')

        plt.figure(figsize=(14, 7))
        timezone_counts = commits_data['Author Timezone'].value_counts()
        sns.barplot(x=timezone_counts.values, y=timezone_counts.index)
        plt.title('Geographic Diversity of Contributors')
        plt.xlabel('Number of Commits')
        plt.ylabel('Timezone')
        plt.tight_layout() 
        plt.savefig(geographic_diversity_plot_path)
        plt.close()
        print("Geographic Diversity Plot Saved Successfully")
    except Exception as e:
        print(f"Geographic Diversity Plot Failed to Save: {e}")


# Come back to this, work out how to convert correctly

# def geographic_diversity(commits_data, current_directory):
#     try:
#         geographic_diversity_plot_path = os.path.join(current_directory, 'geographic_diversity.png')

#         # Map the timezone offsets to their codes
#         timezone_map = {tz['seconds']: tz['name'] for tz in timezones}
#         commits_data['Timezone Code'] = commits_data['Author Timezone'].map(timezone_map)

#         # Plot the number of commits by timezone code
#         plt.figure(figsize=(14, 7))
#         timezone_counts = commits_data['Timezone Code'].value_counts()
#         sns.barplot(x=timezone_counts.index, y=timezone_counts.values)
#         plt.title('Geographic Diversity of Contributors')
#         plt.xlabel('Timezone Code')
#         plt.ylabel('Number of Commits')
#         plt.xticks(rotation=90)  # Rotate the x labels for better readability
#         plt.tight_layout()  # Adjust the layout to fit everything
#         plt.savefig(geographic_diversity_plot_path)
#         plt.close()
#         print("Geographic Diversity Plot Saved Successfully")
#     except Exception as e:
#         print(f"Geographic Diversity Plot Failed to Save: {e}")



def file_types(commits_data, current_directory):
    try:
        file_types_plot_path = os.path.join(current_directory, 'file_types.png')
        file_types = Counter()

        for files in commits_data['modified_files']:
            # Split the files, clean extensions, and convert to lower case
            files = [clean_extension(os.path.splitext(file)[1]) for file in files.split()]
            # Filter out entries that are empty or just a period
            files = [file for file in files if file and file != '.']
            file_types.update(files)

        # Select the top_n most common file types
        top_file_types = file_types.most_common(5)

        # Create a DataFrame from the top file types
        file_types_df = pd.DataFrame(top_file_types, columns=['File Extension', 'Count'])

        # Plotting
        plt.figure(figsize=(10, 8))
        sns.barplot(x='Count', y='File Extension', data=file_types_df, orient='h')
        plt.title(f'Most Commonly Changed File Types in Commits (Top 5)')
        plt.xlabel('Count')
        plt.ylabel('File Extension')
        plt.tight_layout()
        plt.savefig(file_types_plot_path)
        plt.close()
        print("File Types Plot Saved Successfully\n")

    except Exception as e:
        print("File Types Plot Failed to Save")
# ------------------------------------------------------------------------------------------
    
def main():
    current_directory = os.getcwd()
    analysis_data, commits_data, folder_count = load_and_aggregate_data(current_directory)  # Load and aggregate data

    print("----------------------------------------")
    print("Analysis of Data Extracted:")
    print(f"Total number of repositories: {folder_count}")
    print(f"Total number of commits across all repositories: {len(commits_data)}")

    print("----------------------------------------")
    print("Visualisations:\n")

    
    gini_coefficient_distribution(analysis_data, current_directory)  # Visualisation 1
    contributors_distribution(analysis_data, current_directory)  # Visualisation 2
    weekly_commits(commits_data, current_directory)  # Visualisation 3
    commit_size_distribution(commits_data, current_directory)  # Visualisation 4
    geographic_diversity(commits_data, current_directory)  # Visualisation 5
    file_types(commits_data, current_directory)  # Visualisation 6

    print("Saved all visualisations successfully")
    print("----------------------------------------")

# ------------------------------------------------------------------------------------------

# Run the main function  
    
if __name__ == '__main__':
    main()
