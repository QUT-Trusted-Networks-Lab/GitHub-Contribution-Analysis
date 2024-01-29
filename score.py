import os
import pandas as pd
import re
import matplotlib.pyplot as plt

# --------------------------------------------------------------------------------------

# Helper Functions

def normalize_with_max(series, max_value):
    return series / max_value

def calculate_commits_per_day_score(avg_commits_per_day):
    if avg_commits_per_day > 1:
        return 1
    elif avg_commits_per_day > 0.75:
        return 0.75
    elif avg_commits_per_day > 0.5:
        return 0.5
    elif avg_commits_per_day > 0.25:
        return 0.25
    else:
        return 0
    
def calculate_gini_committers_score(gini_coefficient, committers_score):
    return gini_coefficient * committers_score


def calculate_committers_score(total_committers):
    if total_committers >= 100:
        return 1.0  
    elif total_committers >= 50:
        return 0.75  
    elif total_committers >= 25:
        return 0.5  
    elif total_committers >= 10:
        return 0.25  
    else:
        return 0 

def calculate_project_duration_score(duration_str):
    # Use regular expressions to find numbers before 'years' and 'months'
    year_matches = re.search(r'(\d+)\s+years?', duration_str)
    month_matches = re.search(r'(\d+)\s+months?', duration_str)

    years = int(year_matches.group(1)) if year_matches else 0
    months = int(month_matches.group(1)) if month_matches else 0

    total_years = years + months / 12

    if total_years < 1:
        return 0
    elif total_years < 2:
        return 0.25
    elif total_years < 3:
        return 0.5
    elif total_years < 4:
        return 0.75
    else:
        return 1

def calculate_commit_size_score(avg_commit_size):
    if avg_commit_size >= 100:
        return 1.0
    elif avg_commit_size >= 75:
        return 0.75
    elif avg_commit_size >= 50:
        return 0.5
    elif avg_commit_size >= 25:
        return 0.25
    else:
        return 0
    
def calculate_weighted_scores(scores_df, columns, weights):
    for column in columns[1:]:  # Exclude 'Folder Name'
        if column in weights:  # Check if the column has a defined weight
            weighted_column = column + ' Weighted'
            scores_df[weighted_column] = scores_df[column] * weights[column]
    return scores_df


def calculate_overall_quality_score(scores_df, weights):
    weighted_columns = [col + ' Weighted' for col in weights]

    scores_df['Overall Quality Score'] = scores_df[weighted_columns].sum(axis=1).round(3)
    return scores_df

def save_scores_to_csv(scores_df, filename):
    scores_df.to_csv(filename, index=False)

# --------------------------------------------------------------------------------------

# Calculating Scores

def calculate_scores(analysis_df):
    # Gini Coefficient
    gini_coefficient = analysis_df['Gini Coefficient'].iloc[0]

    # Project Duration
    project_duration_str = analysis_df['Project Duration (Years and Months)'].iloc[0]
    project_duration_score = calculate_project_duration_score(project_duration_str)

    # Average Commits per Day
    avg_commits_per_day = analysis_df['Average Commits per Day'].iloc[0]
    commits_per_day_score = calculate_commits_per_day_score(avg_commits_per_day)

    # Average Score
    average_score = analysis_df['Average Score'].iloc[0]

    # Total Committers
    total_committers = analysis_df['Number of Contributors'].iloc[0]
    committers_score = calculate_committers_score(total_committers)

    # Average Commit Size
    avg_commit_size = analysis_df['Average Commit Size'].iloc[0]
    commit_size_score = calculate_commit_size_score(avg_commit_size)

    gini_committers_score = calculate_gini_committers_score(gini_coefficient, committers_score)

    return gini_coefficient, project_duration_score, commits_per_day_score, average_score, committers_score, commit_size_score, gini_committers_score


# --------------------------------------------------------------------------------------

# Plotting Functions

def plot_quality_score_distribution(scores_df,current_directory):
    try:
        quality_score_distribution = os.path.join(current_directory, 'overall_quality_distribution.png')
        plt.figure(figsize=(12, 8))  # Increased figure size
        plt.hist(scores_df['Overall Quality Score'], bins=20, range=(0, 1), edgecolor='black')

        plt.xlabel('Overall Quality Score', fontsize=16)
        plt.ylabel('Number of Repositories', fontsize=16)
        plt.title('Distribution of Overall Quality Scores Across Repositories', fontsize=20)

        plt.savefig(quality_score_distribution)
        plt.close()
    except:
        print("Error plotting quality score distribution")

# --------------------------------------------------------------------------------------


def main():
    all_scores = []
    columns = ['Folder Name', 'Gini Coefficient', 'Project Duration Score', 'Normalized Avg Commits/Day', 'Average Score', 'Total Committers', 'Average Commit Size', 'Gini-Committers Score']

    weights = {
        'Project Duration Score': 0.2,
        'Normalized Avg Commits/Day': 0.2,
        'Average Score': 0.1,
        'Average Commit Size': 0.1,
        'Gini-Committers Score': 0.4,  # Adjusted weight for the new combined score
    }

    print('-- Repository Quality Scores --')
    print('Calculating scores...')

    for root, dirs, files in os.walk('.'):
        folder_name = os.path.basename(root)
        for file in files:
            if file.endswith('_analysis.csv'):
                analysis_path = os.path.join(root, file)
                analysis_df = pd.read_csv(analysis_path)
                scores = calculate_scores(analysis_df)
                all_scores.append((folder_name,) + scores)

    print('Saving scores to CSV...')

    scores_df = pd.DataFrame(all_scores, columns=columns)
    scores_df['Average Score'] = normalize_with_max(scores_df['Average Score'], 7)

    scores_df = calculate_weighted_scores(scores_df, columns, weights)
    scores_df = calculate_overall_quality_score(scores_df, weights)

    save_scores_to_csv(scores_df, 'repository_quality_scores.csv')

    print('Plotting quality score distribution...')

    current_directory = os.getcwd()
    plot_quality_score_distribution(scores_df, current_directory)

    print('Done!')


# --------------------------------------------------------------------------------------

# Run the main function
    
if __name__ == '__main__':
    main()
