import os
import shutil

from github import Github
import git

MIN_LINES_NBR = 150000
REPOS_PATH = "./repos"
QUERY_STR = "language:java"


class CloneProgressPrinter(git.remote.RemoteProgress):
    def update(self, op_code, cur_count, max_count=None, message=''):
        print(f'Cloning progress : {(cur_count / max_count * 100):.2f}% {"(" + message + ")" if message else ""}')


def get_repo_name_from_url(repo_url: str) -> str:
    split_repo_url = repo_url.split("/")
    return f"{split_repo_url[-2]}_{split_repo_url[-1][:-4]}"


def clone_repo(repo_url: str, repos_path: str):
    output_dir = os.path.join(repos_path, get_repo_name_from_url(repo_url))
    if os.path.isdir(output_dir):
        print(f"{output_dir} already exists, skipping cloning.")
        return

    print(f"Cloning {repo_url.split('/')[-1][:-4]}...")
    git.Repo.clone_from(repo_url, output_dir, progress=CloneProgressPrinter(), multi_options=["--depth=1"])
    shutil.rmtree(os.path.join(output_dir, ".git"))
    print(f"{repo_url} cloned.")


def main():
    g = Github(os.environ["GITHUB_TOKEN"])

    if not os.path.isdir(REPOS_PATH):
        os.mkdir(REPOS_PATH)

    nbr_repos_found = 0
    for repo in g.search_repositories(QUERY_STR):
        try:
            repo_languages = repo.get_languages()
            if len(repo_languages) != 1 or repo_languages["Java"] < MIN_LINES_NBR:
                pass

            clone_repo(repo.clone_url, REPOS_PATH)
            nbr_repos_found += 1
        except KeyboardInterrupt:
            break

    print(f"{nbr_repos_found} found.")


if __name__ == "__main__":
    main()
