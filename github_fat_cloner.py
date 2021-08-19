import os
import shutil
import subprocess
from typing import Tuple

from github import Github
import git

QUERY_STR = "language:java fork:false"
MIN_LINES_NBR = 200000
MIN_NBR_CONTRIBUTORS = 3
MIN_NBR_COMMITS = 20

REPOS_PATH = "../../input_data/java_codebases_real"
TMP_CLONE_LOCATION = "/tmp/"


class CloneProgressPrinter(git.remote.RemoteProgress):
    def update(self, op_code, cur_count, max_count=None, message=''):
        print(f'Cloning progress : {(cur_count / max_count * 100):.2f}% {"(" + message + ")" if message else ""}')


def get_repo_name_from_url(repo_url: str) -> str:
    split_repo_url = repo_url.split("/")
    return f"{split_repo_url[-2]}_{split_repo_url[-1][:-4]}"


def clone_repo(repo_url: str, output_dir: str):
    print(f"Cloning {repo_url.split('/')[-1][:-4]}...")
    git.Repo.clone_from(repo_url, output_dir, progress=CloneProgressPrinter(), multi_options=["--depth=1"])
    shutil.rmtree(os.path.join(output_dir, ".git"))
    print(f"{repo_url} cloned.")


def del_repo(repo_dir: str):
    shutil.rmtree(repo_dir)


def count_loc_in_dir(repo_dir: str) -> int:
    loc_lines = subprocess.check_output("cloc --include-lang 'Java' " + repo_dir, shell=True).decode("utf-8").split("\n")
    JAVA_LINE_IDX = 8

    if len(loc_lines) < JAVA_LINE_IDX:
        return 0

    blank_loc, comment_loc, code_loc = [int(x) for x in loc_lines[JAVA_LINE_IDX].split()[2:]]

    return blank_loc + comment_loc + code_loc


def search_and_clone(github_api_instance: Github) -> Tuple[int, int, bool]:
    nbr_repos_found = 0
    total_nbr_repos = 0
    should_stop = False

    # Sorting by last updated to get new results instead of always the same ones
    for repo in github_api_instance.search_repositories(QUERY_STR, sort="updated"):
        total_nbr_repos += 1
        try:
            final_output_dir = os.path.join(REPOS_PATH, get_repo_name_from_url(repo.clone_url))
            if os.path.isdir(final_output_dir):
                print(f"{final_output_dir} already exists, skipping.")
                continue

            tmp_output_dir = os.path.join(TMP_CLONE_LOCATION, get_repo_name_from_url(repo.clone_url))
            clone_repo(repo.clone_url, tmp_output_dir)

            if count_loc_in_dir(tmp_output_dir) < MIN_LINES_NBR or \
                    repo.get_contributors().totalCount < MIN_NBR_CONTRIBUTORS or\
                    repo.get_commits().totalCount < MIN_NBR_COMMITS:
                del_repo(tmp_output_dir)
                continue

            shutil.move(tmp_output_dir, final_output_dir)
            print("Accepted repository" + repo.clone_url)
            nbr_repos_found += 1
        except KeyboardInterrupt:
            should_stop = True
            break

    return nbr_repos_found, total_nbr_repos, should_stop


def main():
    github_api_instance = Github(os.environ["GITHUB_TOKEN"])

    if not os.path.isdir(REPOS_PATH):
        os.mkdir(REPOS_PATH)

    nbr_repos_found = 0
    total_nbr_repos = 0

    while 1:
        search_res_found, search_res_total, should_stop = search_and_clone(github_api_instance)
        nbr_repos_found += search_res_found
        total_nbr_repos += search_res_total
        if should_stop:
            break

    print(f"{nbr_repos_found} found, out of {total_nbr_repos} repos.")


if __name__ == "__main__":
    main()
