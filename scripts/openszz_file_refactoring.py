import csv
import json
import sys
from os import path
from typing import List, Tuple, Dict


def get_oracle(filename: str) -> Tuple[Dict[str, List[Tuple[str, str, int]]], List[str]]:
    bic_list = dict()
    unique_keys = []
    unique_repos = set()
    with open(filename) as json_file:
        file_json = json.load(json_file)
        for obj in file_json:
            bics = obj['inducing_commit_hash']
            fix = obj['fix_commit_hash']
            repo = obj['repo_name']
            id = obj['id']
            for bic in bics:
                if bic in bic_list:
                    bic_list[bic].append((fix, repo, id))
                else:
                    bic_list[bic] = [(fix, repo, id)]
                unique_keys.append(repo + '_' + fix + '_' + bic)
            unique_repos.add(repo)

    assert len(unique_keys) == len(set(unique_keys))
    return bic_list, unique_keys


class MyObj:
    def __init__(self, id: int, repo_name: str, fix_commit_hash: List[str], bug_commit_hash: List[str], earliest_issue_date: str, issue_urls: List[str], language: List[str], inducing_commit_hash: List[str] = []):
        self.id = id
        self.repo_name = repo_name
        self.fix_commit_hash = fix_commit_hash
        self.bug_commit_hash = bug_commit_hash
        self.earliest_issue_date = earliest_issue_date
        self.issue_urls = issue_urls
        self.language = language
        self.inducing_commit_hash = inducing_commit_hash


if __name__ == "__main__":
    oracle = sys.argv[1] # "out/bugfix_commits_issues_only.json"
    open_res_folder = sys.argv[2] # "out/openszz-issue/"
    json_res_file = sys.argv[3] # "out/bic_open_bugfix_commits_issues_only.json"

    with open(json_res_file, 'w') as json_out_file:
        new_json = []

        with open(oracle) as json_in_file:
            file_json = json.load(json_in_file)

            for obj in file_json:
                my_json = obj
                my_list = []
                filename_bic = open_res_folder + my_json['repo_name'].replace('/', '_') + "_BugInducingCommits.csv"
                if path.exists(filename_bic):
                    file_bic = open(filename_bic, 'r', newline='', encoding="utf-8")
                    bic_reader = csv.DictReader(file_bic, delimiter=';')
                    for bic_row in bic_reader:
                        if bic_row['bugFixingId'] == my_json['fix_commit_hash'] and bic_row['bugInducingId'] not in my_list:
                            my_list.append(bic_row['bugInducingId'])
                    file_bic.close()
                my_json['inducing_commit_hash'] = my_list
                new_json.append(my_json)

        json.dump(new_json, json_out_file)
