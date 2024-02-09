# Replication package

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.5876817.svg)](https://doi.org/10.5281/zenodo.5876817)

### [NOTE 1: For new studies involving PySZZ, please use the updated version of the tool (PySZZ v2)](https://github.com/grosa1/pyszz_v2)
### [NOTE 2: The code used for the commit mining phase is available here](https://github.com/grosa1/bugfix-commits-miner)
------------------

## Evaluating SZZ Implementations Through a Developer-informed Oracle: Replication package

- `analyzed_projects_all.csv` contains in CSV format the list of all cloned projects at the time of this study.
    - `repo_name` is the repository name;
    - `last_checkout` is the hash of the last commit available at the time of the clone, and;
    - `date` is the date of the latest available commit.
    
- `detailed-database` is a folder containing the two complete datasets we defined.
    - `overall.json` contains all the instances of our dataset (1,930);
    - `language-filtered.json` contains 1,115 instances involving files in the following languages: C, Python, C++, JavaScript, Java, PHP, Ruby, and C#.
    Both these datasets are JSON arrays. Each element has the following structure:
        - `id` is a unique ID used during the construction phase, it is a univocal value for every entry;
        - `repository` is the repository name as hosted in GitHub (owner/project-name);
        - `fix` contains information about the fix, including:
            - `commit`: meta-data about the commit, including:
                - `hash`: commit hash;
                - `message`: commit message;
                - `author`: commit author;
                - `url`: GitHub API URL with complete information about the commit;
            - `files`: an array of files modified in the fix commit; each element provides:
                - `name`: name of the modified file after the commit (this is not the complete path, just the file name);
                - `old_path`/`new_path`: the path of the file before and after the commit;
                - `lang`: extension of the file (indicating the programming language);
                - `lines_added`/`lines_deleted`: lists of line numbers added/deleted;
                - `change_type`: type of change (one of the following: "MODIFY"/"ADD"/"RENAME"/"DELETE");
        - `bugs` contains the list of bug-inducing-commits for the fix; each element includes:
            - `commit`: meta-data about the commit, including:
                - `hash`: commit hash;
                - `message`: commit message;
                - `author`: commit author;
                - `url`: GitHub API URL with complete information about the commit;
            - `files`: an array of files modified in the fix commit; each element provides:
                - `name`: name of the modified file after the commit (this is not the complete path, just the file name);
                - `old_path`/`new_path`: the path of the file before and after the commit;
                - `lang`: extension of the file (indicating the programming language);
                - `lines_added`/`lines_deleted`: lists of line numbers added/deleted;
                - `change_type`: type of change (one of the following: "MODIFY"/"ADD"/"RENAME"/"DELETE");
        - `issue_urls` is a list of URLs of issues referenced in the fix commit;
        - `earliest_issue_date` is the date of the earliest issue referenced in the fix commit (YYYY-MM-DDTHH:MM:SS);
        - `best_scenario_issue_date` represents the date of an ideal issue reported for the bug; it is the date of the last bug-inducing commit incremented by 60 seconds (YYYY-MM-DDTHH:MM:SS).
        
- `json-input-raw` is a folder containing four datasets used as input for our experimentations, derived from `language-filtered.json`.
    - `bugfix_commits_all.json` and `bugfix_commits_issues_only.json` contain 1,115 and 129 instances in JSON format, respectively. 
    - `bugfix_commits_all_java.json` and `bugfix_commits_issues_only_java.json` contain 80 and 10 instances in JSON format, respectively.  
    These datasets represent the input list of the selected fix commits and its relative list of bug-inducing commits, other than the following additional information used in our SZZ evaluation.
        - `id` is a unique ID used during the construction phase, it is a univocal value for every entry;
        - `repo_name` is the repository name as hosted in GitHub;
        - `fix_commit_hash` is the commit's hash of the selected fix;
        - `bug_commit_hash` is a list of bug-inducing commits;
        - `earliest_issue_date` is a string containing the timestamp of the earliest issue (YYYY-MM-DDTHH:MM:SS);
        - `best_scenario_issue_date` represents the date of an ideal issue reported for the bug; it is the date of the last bug-inducing commit incremented by 60 seconds (YYYY-MM-DDTHH:MM:SS);
        - `issue_urls` is a list of URLs of issues referenced in the fix commit;
        - `language` is a list of the programming languages of the files impacted by the fix commit.
    
- `cloned` is a placeholder folder where git repositories must be copied (or cloned) to replicate this work. See the instructions below.

- `json-output-raw` is a folder containing a list of JSON files containing our pre-calculated results for each SZZ algorithm. 

- `scripts` is a folder that contains all scripts created to post-process or analyze our data.

- `tools` is a folder that contains a snapshot of developed codes. For new studies, please use the extended version [PySZZ v2](https://github.com/grosa1/pyszz_v2).

- `results` is a folder that contains all calculated metrics, such as Precision, Recall, F-measure, etc.

## How to generate the pre-calculated results
The following are the instructions needed to execute our suite of tools and generate our results. This example refers to the B-SSZ variant, but any other algorithm can be reproduced by changing the input arguments as detailed in the original guide. See `tools/pyszz.zip` for more instructions.

- _Preparing input data._ As the first step you need to clone the git repository of every project. You can rely on the following approach.
    - As an alternative, you can clone into `cloned` folder each repository and then checkout the list of commit's hashes contained in `analyzed_projects_all.csv` and `analyzed_projects_issues_only.csv`. This recreates the exact same conditions of our experiment. 

- _Running SZZ._ [PySZZ](https://github.com/grosa1/pyszz) (see `tools/pyszz.zip` for a replication snapshot, and check the reported URL for the latest version) is a free open-source suite of tools used to implement in Python all SZZ major variants.
You can run a specific variant by passing a pre-defined `yml` file or experiment with custom inputs. E.g., `conf/bszz.yml` activates B-SZZ variant.

``python3 main.py json-input-raw/bugfix_commits_all.json conf/bszz.yml cloned`` runs B-SZZ algorithm.

Where:
 - `json-input-raw/bugfix_commits_all.json` is the input list of fixes;
 - `conf/bszz.yml` is a pre-defined list of settings used to activate a specific variant (see `tools/pyszz.zip` for more details);
 -  `cloned` is the folder containing a list of pre-cloned repositories.


NOTE. SZZUnleashed and OpenSZZ are not part of PySZZ suite. We adapted the original implementations to our input formats.
- The [SZZUnleashed](https://github.com/wogscpar/SZZUnleashed) implementation has been forked to handle our input formant and add parallel support [SZZUnleashed-adapted
](https://github.com/intersimone999/SZZUnleashed-adapted) (See `tools/szz-unleashed.zip` as a snapshot of our adapter)
- The [OpenSZZ](https://github.com/clowee/OpenSZZ) implementation has been forked to exclude the Jira filter [OpenSZZ](https://github.com/lucapascarella/OpenSZZ) (See `tools/open-szz.zip` as a snapshot of our adapter) 
OpenSZZ needs post-processing to adapt the generated results to our JSON format. See below _OpenSZZ post-processing script_

Both snapshots `tools/szz-unleashed.zip` and `tools/open-szz.zip` contain the instructions to use our adapters. 

## Post-processing for issue date filtering
`json-output-raw` contains a list of JSON files generated by each SZZ variant.

Specifically, `bic_<algorithm-name>_bugfix_commits_all.json` and `bic_<algorithm-name>_bugfix_commits_issues_only.json` refer to the output of `<algorithm-name>` SZZ variant.
Instead, `bic_<algorithm-name>_bugfix_commits_all-filter.json` and `bic_<algorithm-name>_bugfix_commits_issues_only-filter.json` is the post-filtered output when the filter on issue data is applied.

We use `ruby postfilter.rb <json-output> <cloned>` to post-process `bic_<algorithm-name>_bugfix_commits_all.json` and `bic_<algorithm-name>_bugfix_commits_issues_only.json` and generate `bic_<algorithm-name>_bugfix_commits_all-filter.json` and `bic_<algorithm-name>_bugfix_commits_issues_only-filter.json`, as a reduced list of datapoints filter by issue's date.
- `postfilter.rb` is our ruby script used to parse the output of any SZZ algorithm to filter out BIC commits that do not respect the issue date condition.
- `<json-output>` is the input folder containing the list of JSON files produced by PySZZ;
- `<cloned>` is the path to the pre-cloned (or checked out) repositories.

## Recall, Precision, F-measure, and Overlap

`overlap.py` is a Python script with embedded input paths that can be used to calculate Recall, Precision, F-measure, and overlap.
You may need to adapt `base_path` global variable to point to your result's directory. E.g., `base_path = "json-output-raw/"` analyzes the study's results.

This tool produces:

- `<dataset>-recall-precision.csv` lists Precision, Recall, F-measure, total number of correct instances (our oracle), and total number of identified instances;
 - `<dataset>-overlap_vi_vj.csv` lists the overlap, the total number of BIC uniquely identified, the total number of correctly identified, and the union of all BIC correctly identified by all models;
- `<dataset>-overlap_vi_but_others.csv` is a CSV version of the heatmap for the overlap comparison.
- `<dataset>-not-identified.csv` summarizes the not found BICs;

- `<dataset>-heatmap.pdf` as reported in the manuscript.
- `wrong` is a subfolder with a list of CSV files containing the wrongly identified BIC with a link to GitHub FIX commit.

### OpenSZZ post-processing script

OpenSZZ produces three files for each analyzed instance. E.g., `AIFDR_inasafe_BugFixingCommit.csv`, `AIFDR_inasafe_BugInducingCommits.csv`, and `AIFDR_inasafe.txt`.

To transform all these CSV files in a single JSON file compatible to `overlap.py` we create a small script `openszz_file_refactoring.py`.

`python3 openszz_file_refactoring.py <oracle> <openszz-issue> <bic_open_bugfix_commits_issues_only.json>`

Where:
 - `<oracle>` is the list of fixes. E.g., `json-input-raw/bugfix_commits_all.json`;
 - `<openszz-issue>` is the folder path where openSZZ produces its results;
 - `<bic_open_bugfix_commits_issues_only.json>` is the destination file output where to store in JSON format openSZZ bug-inducing commits;
