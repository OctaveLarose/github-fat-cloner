import os
import shutil

from github import Github
import git

QUERY_STR = "language:java fork:false"
MIN_LINES_NBR = 200000
MIN_NBR_CONTRIBUTORS = 3
MIN_NBR_COMMITS = 20

REPOS_PATH = "../../../../../java_codebases"

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


def main():
    g = Github(os.environ["GITHUB_TOKEN"])

    if not os.path.isdir(REPOS_PATH):
        os.mkdir(REPOS_PATH)

    nbr_repos_found = 0
    total_nbr_repos = 0
    for repo in g.search_repositories(QUERY_STR):
        total_nbr_repos += 1
        try:
            output_dir = os.path.join(REPOS_PATH, get_repo_name_from_url(repo.clone_url))
            if os.path.isdir(output_dir):
                print(f"{output_dir} already exists, skipping cloning.")
                continue

            repo_languages = repo.get_languages()
            if len(repo_languages) != 1 or repo_languages["Java"] < MIN_LINES_NBR:
                continue
            if repo.get_contributors().totalCount < MIN_NBR_CONTRIBUTORS:
                continue
            if repo.get_commits().totalCount < MIN_NBR_COMMITS:
                continue
            clone_repo(repo.clone_url, output_dir)
            nbr_repos_found += 1
        except KeyboardInterrupt:
            break

    print(f"{nbr_repos_found} found, out of {total_nbr_repos} repos.")


if __name__ == "__main__":
    main()
