# Import necessary libraries
from pydriller import *
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from dateutil.relativedelta import relativedelta
import csv
import os

#--------------------------------------------------------------------------------------------------------------

# Insert the paths to the repositories you want to analyse:

repo_paths = [
    'https://github.com/cab202/quty',
    'https://github.com/jupyter/jupyter',
    'https://github.com/Kanaries/Rath',
    'https://github.com/jupyterhub/jupyterhub',
    'https://github.com/trimstray/the-book-of-secret-knowledge'
]

#--------------------------------------------------------------------------------------------------------------

# Extract the name of the repository from the URL and create an appropriately named folder

def extract_github_name(url):
    URL_parts = url.split('/')
    try:
        index = URL_parts.index('github.com')
        return URL_parts[index + 1] + "-" + URL_parts[index + 2]# Return name after 'github.com'
    except (ValueError, IndexError):
        return "Invalid URL or username not found"

def create_folder(name):
    try:
        os.makedirs(name, exist_ok=True)    
        print(f"Folder '{name}' created successfully.")
    except OSError as error:
        print(f"Error creating folder '{name}': {error}")

# --------------------------------------------------------------------------------------------------------------

# Extract data from set repositories

def extract_commits(repo_path):
    commits_data = []
    print(f"Extracting data from repository: {repo_path}...")
    try:
        for commit in Repository(repo_path).traverse_commits():
            if commit.in_main_branch == True and commit.merge == False:
                commit_data = {
                    'Hash': commit.hash,
                    'Commit Message': commit.msg,
                    'Author Name': commit.author.name,
                    'Author Email': commit.author.email,
                    'Committor Name': commit.committer.name,
                    'Committor Email': commit.committer.email,
                    'Author Date': commit.author_date,
                    'Author Timezone': commit.author_timezone,                           
                    'Committor Date': commit.committer_date,
                    'Committor Timezone': commit.committer_timezone,
                    # 'Branches': commit.branches, # Redundant given in_main_branch is True always
                    'in_main_branch': commit.in_main_branch, # Arguably redundant given in_main_branch is always true
                    'merge': commit.merge, # Arguably redundant given merge is always false
                    'modified_files': [file.filename for file in commit.modified_files],
                    'parents': commit.parents,
                    # 'project_name': commit.project_name, # This is redundant data
                    # 'project_path': commit.project_path, # This is redundant data
                    'deletions': commit.deletions,
                    'insertions': commit.insertions,
                    'lines': commit.lines,
                    'files': commit.files,
                    'dmm_unit_size': commit.dmm_unit_size,
                    'dmm_unit_complexity': commit.dmm_unit_complexity,
                    'dmm_unit_interfacing': commit.dmm_unit_interfacing
                }  
                commits_data.append(commit_data)
        print(f"Repository {repo_path} extracted successfully.\n")
    except Exception as e:
        print(f"Error processing repository {repo_path}: {e}")
    return commits_data

#--------------------------------------------------------------------------------------------------------------

# Plots of data

def commits_by_authors(df, github_name):
    plt.figure()

    # Plot the number of commits per author (top 10)
    df['Author Name'].value_counts()[:10].plot(kind='bar')

    plt.xlabel('Author')
    plt.ylabel('Number of Commits')
    plt.title(f"Number of Commits per Author for {github_name}")
    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.4)

    plt.savefig(os.path.join(github_name, f"{github_name}_commits_per_author.png"), bbox_inches='tight')
    print(f"Commits per author for {github_name} plotted successfully.")
    plt.close() 

def plot_commit_impact_by_top_authors(df, github_name):
    plt.figure()

    top_authors = df['Author Name'].value_counts().nlargest(10).index

    # Filter the DataFrame to include only the top 10 contributors
    top_authors_df = df[df['Author Name'].isin(top_authors)]

    # Aggregate insertions and deletions for each of the top contributors
    author_impact = top_authors_df.groupby('Author Name').agg({'insertions': 'sum', 'deletions': 'sum'})
    author_impact.plot(kind='bar', stacked=True)

    plt.xlabel('Author')
    plt.ylabel('Lines Changed (Insertions + Deletions)')
    plt.title(f"Commit Impact by Top 10 Authors for {github_name}")
    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.4)

    plt.savefig(os.path.join(github_name, f"{github_name}_commit_impact_by_top_authors.png"))
    print(f"Commit impact by top 10 authors for {github_name} plotted successfully.")
    plt.close()


#--------------------------------------------------------------------------------------------------------------

# Analysis of data

# Commit Message Analysis

def length_of_title_score(title):
    length = len(title)
    if length == 0 or length > 72: return 1
    elif length <= 10: return 2
    elif length <= 30: return 3
    elif length <= 50: return 4
    else: return 5

def title_ends_with_dots(title):
    return 2 if title.endswith('.') else 1

def title_first_character_capital(title):
    return 2 if title and title[0].isupper() else 1


def calculate_commit_scores(commit_message):
    # Assume the first line of commit_message is the title
    title = commit_message.split('\n', 1)[0]    
        
    # Calculate scores using the defined functions
    scores = {
        'length_of_title': length_of_title_score(title),
        'title_ends_with_dots': title_ends_with_dots(title),
        'title_first_character_capital': title_first_character_capital(title),
        # Calculate other scores if useful??? Ask Gowri?
    }
    
    # Calculate the average score for this commit message
    average_score = sum(scores.values()) / len(scores)
    scores['average_score'] = average_score
    return scores



def gini_coefficient(commit_counts):

    # There must be at least one non-zero value for the Gini coefficient to be defined
    if len(commit_counts) == 0 or np.all(commit_counts == 0):
        return 0.0

    commit_counts = np.sort(commit_counts)
    cum_commits = np.cumsum(commit_counts)
    cum_prop = cum_commits / cum_commits[-1]
    cum_pop = np.arange(1, len(cum_commits) + 1) / len(commit_counts)

    # Gini coefficient calculation (where 1 signifies equal commits per committer and vice versa)
    gini = 1 - (2 / len(commit_counts)) * np.sum(cum_pop - cum_prop)
    return gini



def calculate_commit_frequency(df):
    df['Author Date'] = pd.to_datetime(df['Author Date'])

    # Calculate the total time span of the commits
    time_span = df['Author Date'].max() - df['Author Date'].min()

    # Calculate frequencies
    days = time_span.days

    if days == 0:
        days = 1

    commits_per_day = len(df) / days
    weeks = days / 7
    months = days / 30  # Approximation
    commits_per_week = len(df) / weeks
    commits_per_month = len(df) / months

    return commits_per_day, commits_per_week, commits_per_month


def calculate_percentage_with_5_or_more_commits(df):
    author_commit_counts = df['Author Name'].value_counts()
    contributors_with_5_or_more = author_commit_counts[author_commit_counts >= 5]
    percentage = (len(contributors_with_5_or_more) / len(author_commit_counts)) * 100
    return percentage

#--------------------------------------------------------------------------------------------------------------

# Main function to run the analysis on each repository
def main():
    print("----------------------------------------------------------------")
    for repo_path in repo_paths:
        github_name = extract_github_name(repo_path)
        csv_filename = f"{github_name}_commits.csv"
        analysis_csv_filename = f"{github_name}_analysis.csv"
        csv_path = os.path.join(github_name, csv_filename)
        analysis_csv_path = os.path.join(github_name, analysis_csv_filename)

        if not os.path.exists(csv_path):
            commits_data = extract_commits(repo_path)
            create_folder(github_name)
            # Export data to CSV
            with open(csv_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=commits_data[0].keys())
                writer.writeheader()
                writer.writerows(commits_data)
                print(f"Data exported to CSV successfully in {csv_path}.\n")
        else:
            print(f"CSV file {csv_path} already exists. Skipping data extraction.\n")

        # Perform analysis on the commits data
        print(f"Starting data analysis for {github_name}...\n")
        df = pd.read_csv(csv_path)
        perform_analysis(df, github_name, analysis_csv_path)
        print("----------------------------------------------------------------")


def perform_analysis(df, github_name, analysis_csv_path):

    commits_by_authors(df, github_name)
    plot_commit_impact_by_top_authors(df, github_name)

    # Calculate the Gini coefficient
    author_commit_counts = df['Author Name'].value_counts().values
    gini_index = gini_coefficient(author_commit_counts)
    # print(f"The Gini coefficient for commits per author in {github_name} is: {gini_index}")

    # Calculate the number of unique contributors
    num_contributors = df['Author Name'].nunique()
    # print(f"Number of unique contributors in {github_name}: {num_contributors}")
    
    # Calculate commit frequency
    cpd, cpw, cpm = calculate_commit_frequency(df)
    # print(f"Average commits per day in {github_name}: {cpd:.2f}")
    # print(f"Average commits per week in {github_name}: {cpw:.2f}")
    # print(f"Average commits per month in {github_name}: {cpm:.2f}")

    # Calculate the percentage of contributors with 5 or more commits
    perc_with_5_or_more = calculate_percentage_with_5_or_more_commits(df)
    # print(f"Percentage of contributors with 5 or more commits in {github_name}: {perc_with_5_or_more:.2f}%\n")

    # Average Commit Size
    average_commit_size = (df['lines']).mean()
    # print(f"Average commit size in {github_name}: {average_commit_size:.2f}")

    # Count the number of unique timezones
    unique_timezones_count = df['Author Timezone'].nunique()
    # print(f"Number of unique timezones: {unique_timezones_count}")

    # # Calculate commit message scores
    commit_scores = df['Commit Message'].apply(calculate_commit_scores)
    scores_df = pd.DataFrame(list(commit_scores))
    average_scores = scores_df.mean()

    # Calculate the duration of project
    earliest_commit_date = df['Author Date'].min()
    latest_commit_date = df['Author Date'].max()
    duration = relativedelta(latest_commit_date, earliest_commit_date)

    # Prepare data for analysis CSV
    analysis_data = {
        'Project Name': github_name,
        'Project Duration (Years and Months)': f"{duration.years} years and {duration.months} months",
        'Gini Coefficient': gini_index,
        'Number of Contributors': num_contributors,
        'Average Commits per Day': cpd,
        'Average Commits per Week': cpw,
        'Average Commits per Month': cpm,
        'Percentage with >= 5 Commits': perc_with_5_or_more,
        'Average Commit Size': average_commit_size,
        'Number of Unique Timezones': unique_timezones_count,
        'Average Title Length': average_scores['length_of_title'],
        'Average Title Ends with Fullstop': average_scores['title_ends_with_dots'],
        'Average Title First Character Capital': average_scores['title_first_character_capital'],
        'Average Score': average_scores['average_score']
        # Add additional analysis data as needed
    }

    # Write analysis data to a new CSV file
    with open(analysis_csv_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=analysis_data.keys())
        writer.writeheader()
        writer.writerow(analysis_data)
        print(f"Analysis data exported to CSV successfully in {analysis_csv_path}") 

# Run the script
main()