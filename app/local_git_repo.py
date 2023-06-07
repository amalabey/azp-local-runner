from git import Repo


class LocalGitRepository():
    def __init__(self, repo_path):
        self.repo_path = repo_path

    def get_active_branch_name(self):
        try:
            repo = Repo(self.repo_path)
            return repo.active_branch.name
        except Exception as e:
            print("Error: Unable to get remote branch name.", str(e))
            return None

    def get_git_username(self):
        try:
            repo = Repo(self.repo_path)
            git_username = repo.config_reader().get_value('user', 'name')
            return git_username
        except Exception as e:
            print("Error: Unable to get git username.", str(e))
            return None
