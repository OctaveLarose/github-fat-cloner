import os
from github import Github


def main():
    g = Github(os.environ["GITHUB_TOKEN"])

    MIN_LINES_NBR = 150000

    nbr_repos_found = 0
    for repo in g.search_repositories("language:java"):
        try:
            print(repo.name)
            # print(repo)
            print(repo.get_languages())
            repo_languages = repo.get_languages()
            if len(repo_languages) != 1 or repo_languages["Java"] < MIN_LINES_NBR:
                pass
            print(f"{repo.name} passes")
            nbr_repos_found += 1
        except KeyboardInterrupt:
            break

    print(f"{nbr_repos_found} found.")


if __name__ == "__main__":
    main()
