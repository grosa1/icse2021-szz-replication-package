import json
from typing import Set, Tuple, List
import seaborn as sb
import matplotlib.pyplot as plt

base_path = "out/"

model_names = ["B-SZZ", "AG-SZZ", "L-SZZ", "R-SZZ", "MA-SZZ", "RA-SZZ*", "SZZ@PYD", "SZZ@UNL", "SZZ@OPN"]

java_filter = ["RA-SZZ*", "SZZ@OPN"]

model_list_all = ["bic_b_bugfix_commits_all.new.json",
                  "bic_ag_bugfix_commits_all.json",
                  "bic_l_bugfix_commits_all.json",
                  "bic_r_bugfix_commits_all.json",
                  "bic_ma_bugfix_commits_all.json",
                  "bic_ra_bugfix_commits_all.json",
                  "bic_pd_bugfix_commits_all.json",
                  "bic_unleashed_bugfix_commits_all.json",
                  "bic_open_bugfix_commits_all.json"]

model_list_all_issue_filter = ["bic_b_bugfix_commits_all.issue-filter.json",
                               "bic_ag_bugfix_commits_all.issue-filter.json",
                               "bic_l_bugfix_commits_all.issue-filter.json",
                               "bic_r_bugfix_commits_all.issue-filter.json",
                               "bic_ma_bugfix_commits_all.issue-filter.json",
                               "bic_ra_bugfix_commits_all.issue-filter.json",
                               "bic_pd_bugfix_commits_all.issue-filter.json",
                               "bic_unleashed_bugfix_commits_all.issue-filter.json",
                               "bic_open_bugfix_commits_all.issue-filter.json"]

model_list_issue_only = ["bic_b_bugfix_commits_issues_only.new.json",
                         "bic_ag_bugfix_commits_issues_only.json",
                         "bic_l_bugfix_commits_issues_only.json",
                         "bic_r_bugfix_commits_issues_only.json",
                         "bic_ma_bugfix_commits_issues_only.json",
                         "bic_ra_bugfix_commits_issues_only.json",
                         "bic_pd_bugfix_commits_issues_only.json",
                         "bic_unleashed_bugfix_commits_issues_only.json",
                         "bic_open_bugfix_commits_issues_only.json"]

model_list_issue_only_issue_filter = ["bic_b_bugfix_commits_issues_only.issue-filter.json",
                                      "bic_ag_bugfix_commits_issues_only.issue-filter.json",
                                      "bic_l_bugfix_commits_issues_only.issue-filter.json",
                                      "bic_r_bugfix_commits_issues_only.issue-filter.json",
                                      "bic_ma_bugfix_commits_issues_only.issue-filter.json",
                                      "bic_ra_bugfix_commits_issues_only.issue-filter.json",
                                      "bic_pd_bugfix_commits_issues_only.issue-filter.json",
                                      "bic_unleashed_bugfix_commits_issues_only.issue-filter.json",
                                      "bic_open_bugfix_commits_issues_only.issue-filter.json"]

# Set one here
# prefix = "all-"
# prefix = "all-filter-"
# prefix = "issue-only-"
# prefix = "issue-only-filter-"
prefixes = ["all-", "all-filter-", "issue-only-", "issue-only-filter-"]


class MyResults:
    def __init__(self, bic_actual: List[str], bic_correct_identified: List[str], bic_wrong_identified: List[str], input_file, model_name):
        self.bic_actual = set(bic_actual)
        self.bic_correct_identified = set(bic_correct_identified)
        self.bic_wrong_identified = set(bic_wrong_identified)

        self.input_file = input_file
        self.model_name = model_name


class CorrectSzz:
    def __init__(self, percentage: float, unique: int, abs: int):
        self.percentage = percentage
        self.unique = unique
        self.abs = abs


def build_key(repo: str, fix: str, bic: str, langs: [str]) -> str:
    lang = '_$_'.join(langs)
    return repo + '_!_' + fix + '_!_' + bic + '_!_' + lang


def get_correct(input_file: str, output_file: str, model_name: str) -> MyResults:
    bic_actual = list()
    bic_correct_identified = list()
    bic_wrong_identified = list()

    with open(output_file, 'w') as out_file:
        out_file.write("id,repo,fix,bic,link \n")
        with open(input_file, 'r') as json_file:
            file_json = json.load(json_file)
            for obj in file_json:
                langs = obj['language']
                fix = obj['fix_commit_hash']
                repo = obj['repo_name']
                oracle_bics = obj['bug_commit_hash']
                pred_bics = obj['inducing_commit_hash'] if 'inducing_commit_hash' in obj else []

                if model_name not in java_filter or (model_name in java_filter and 'java' in langs):
                    # Add all actual BIC
                    for bic in oracle_bics:
                        bic_actual.append(build_key(repo, fix, bic, langs))
                    # Add predicted BIC
                    for bic in pred_bics:
                        # if model_name != "SZZ@UNL" or (model_name == "SZZ@UNL" and len(pred_bics) < 10):
                        if bic in oracle_bics:
                            bic_correct_identified.append(build_key(repo, fix, bic, langs))
                        else:
                            bic_wrong_identified.append(build_key(repo, fix, bic, langs))
                            link = "https://github.com/" + obj['repo_name'] + "/commit/" + obj['fix_commit_hash']
                            out_file.write("{},{},{},{},{}\n".format(obj['id'], obj['repo_name'], obj['fix_commit_hash'], bic, link))
    print("TP: {} FP: {}".format(len(bic_correct_identified), len(bic_wrong_identified)))
    return MyResults(bic_actual, bic_correct_identified, bic_wrong_identified, input_file, model_name)


def get_all_correct_but_i(results: List[MyResults], but: int) -> Set[str]:
    correct = set()
    for i in range(len(results)):
        if i != but:
            correct |= results[i].bic_correct_identified
    # if java_filter:
    #     correct = set([c for c in correct if "java" in c])
    return correct


# def get_correct_j(results: List[MyResults], index: int) -> Set[str]:
#     return results[index].bic_correct_identified
#

def get_f1(precision: float, recall: float) -> float:
    if precision != 0 and recall != 0:
        return 2 * (precision * recall / (precision + recall))
    else:
        return 0.0


if __name__ == "__main__":

    for prefix in prefixes:
        if prefix == "all-":
            models_to_test = model_list_all
        elif prefix == "all-filter-":
            models_to_test = model_list_all_issue_filter
        elif prefix == "issue-only-":
            models_to_test = model_list_issue_only
        elif prefix == "issue-only-filter-":
            models_to_test = model_list_issue_only_issue_filter
        else:
            models_to_test = ''

        # Get all metrics for each model
        results_per_model = []
        for i in range(len(models_to_test)):
            out_wrongly_file = 'out/wrong/' + prefix + model_names[i] + '-wrongly_identified.csv'
            results_per_model.append(get_correct(base_path + models_to_test[i], out_wrongly_file, model_names[i]))

        # NOTE for Python
        # | => Union between sets. E.g., a = {1,2,3} b = {3,4} print(b - a) => {1, 2, 3, 4}
        # & => Intersection between sets. E.g., a = {1,2,3} b = {3,4} print(b - a) => {3}
        # - => Setminus between sets. E.g., a = {1,2} b = {3,4,5} print(b - a) => {1}

        # Calculate overlap vi intersected vj
        corrects_vi_vj = []
        for i in range(len(results_per_model)):
            corrects_j = []
            for j in range(len(results_per_model)):
                correct_i = results_per_model[i].bic_correct_identified
                correct_j = results_per_model[j].bic_correct_identified
                if model_names[i] in java_filter or model_names[j] in java_filter:  # Apply Java only filter
                    correct_i = set([c for c in correct_i if "java" in c])
                    correct_j = set([c for c in correct_j if "java" in c])
                if len(correct_i | correct_j) != 0:
                    correct_vivj = len(correct_i & correct_j) / len(correct_i | correct_j)
                else:
                    correct_vivj = 0.0
                corrects_j.append(correct_vivj)
            corrects_vi_vj.append(corrects_j)

        # Calculate overlap vi but others
        corrects_vi_but_others = []  # Correct_vi,
        for i in range(len(results_per_model)):
            correct_i = results_per_model[i].bic_correct_identified

            correct_others = get_all_correct_but_i(results_per_model, i)
            if model_names[i] in java_filter:  # Apply Java only filter
                correct_others = set([c for c in correct_others if "java" in c])
            correct_vi_others = len(correct_i - correct_others) / len(correct_i | correct_others)
            corrects_vi_but_others.append(CorrectSzz(correct_vi_others, len(correct_i - correct_others), len(correct_i | correct_others)))

        # Calculate recall and precision
        recalls = []
        precisions = []
        corrects = []
        identifieds = []
        for res in results_per_model:
            # All actual correct
            correct = res.bic_actual
            # All identified (both correct and wrong)
            identified = res.bic_correct_identified | res.bic_wrong_identified

            recall = len(correct & identified) / len(correct)
            recalls.append(recall)

            precision = len(correct & identified) / len(identified) if len(identified) != 0 else 0.0
            precisions.append(precision)

            corrects.append(correct)
            identifieds.append(identified)

        # Print recall and precision
        with open('out/' + prefix + 'recall-precision.csv', 'w') as out_file:
            out_file.write("model,recall,precision,fmeasure,correct (TP+FN),identified (TP+FP)\n")
            for i in range(0, len(recalls)):
                precision = precisions[i]
                recall = recalls[i]
                f1 = get_f1(precision, recall)
                print("{:<10} Recall: {:<4.2f}, Precision: {:<4.2f}, F1: {:.2f}, Correct (TP+FN): {:>4}, Identified (TP+FP): {:>4}".format(model_names[i], recall, precision, f1, len(corrects[i]), len(identifieds[i])))
                out_file.write("{},{:.2f},{:.2f},{:.2f},{},{}\n".format(model_names[i], recall, precision, f1, len(corrects[i]), len(identifieds[i])))

        # Print overlap vi intersected vj
        with open('out/' + prefix + 'overlap_vi_vj.csv', 'w') as out_file:
            for model in model_names:
                out_file.write("{},".format(model))
            out_file.write("\n")

            i = 0
            for correct_vi in corrects_vi_vj:
                j = 0
                for correct_vj in correct_vi:
                    print("C{}{}: {:<8.2f}".format(i + 1, j + 1, correct_vj), sep='', end='')
                    out_file.write("{:.2f},".format(correct_vj))
                    j += 1
                out_file.write("\n")
                print()
                i += 1

            heat_map = sb.heatmap(corrects_vi_vj, cmap="YlGnBu", xticklabels=model_names, yticklabels=model_names, annot=True, vmin=0, vmax=1)
            # heat_map.set_title("Overlap")
            plt.tick_params(labelcolor='black', labelsize='small', width=1)
            plt.tick_params(top=True, bottom=False, labeltop=True, labelbottom=False)
            # plt.yticks(rotation=-45)
            plt.xticks(rotation=90)
            # plt.ylim(0, len(corrects_vi_vj))
            # plt.xlim(0, len(corrects_vi_vj))
            # plt.show()
            plt.savefig('out/' + prefix + 'heatmap.pdf', dpi=300, bbox_inches='tight')
            plt.close()

        # Print overlap vi but others
        with open('out/' + prefix + 'overlap_vi_but_others.csv', 'w') as out_file:
            out_file.write("model,overlap,unique,tp,all\n")
            count = 0
            for correct_vi_others in corrects_vi_but_others:
                ci = len(results_per_model[count].bic_correct_identified)
                print("Overlap {:>9}: {:<6.2} Unique: {:<3}  Tot: {}/{}".format(model_names[count], correct_vi_others.percentage, correct_vi_others.unique, ci, correct_vi_others.abs))
                out_file.write("{},{:.2},{},{},{}\n".format(model_names[count], correct_vi_others.percentage, correct_vi_others.unique, ci, correct_vi_others.abs))
                count += 1

        # Get a list of bug inducing that any model identifies
        identified_all = set()
        correct_all = set()
        for result in results_per_model:
            identified_all |= result.bic_correct_identified
            correct_all |= result.bic_actual
            # print("Model: {} => {}".format(result.model_name, len(correct_all)))
        assert correct_all == results_per_model[0].bic_actual
        # correct_all = results_per_model[0].bic_actual

        with open('out/' + prefix + 'not-identified.csv', 'w') as out_file:
            out_file.write("repo,fix,bic,link\n")
            not_identified = correct_all - identified_all
            for elem in not_identified:
                repo, fix, bic, langs = elem.split('_!_')
                link = 'https://github.com/' + repo + '/commit/' + fix
                out_file.write("{},{},{},{}\n".format(repo, fix, bic, link))
