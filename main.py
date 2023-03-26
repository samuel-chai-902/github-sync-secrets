from os import getcwd
from os.path import exists, expanduser
from argparse import ArgumentParser
from subprocess import run, check_output


def get_files_for_sync(secret_name, appended):
    search_files = []
    file_name = expanduser("{}/{}".format(getcwd(), secret_name))

    if not exists(file_name):
        raise FileNotFoundError("The file {} does not exist.".format(file_name))

    search_files.append(file_name)

    for file in appended:
        file = expanduser(file)
        if not exists(file):
            continue
        else:
            search_files.append(file)

    return search_files


def get_current_repo_name():
    output = check_output(["git", "rev-parse", "--show-toplevel"], text=True)
    repo_path = output.strip()
    repo_name = repo_path.split("/")[-1]
    return repo_name


def parse_secrets_file(upload_files):
    secret_dict = {}
    for f in upload_files:

        with open(f, "r") as file:
            for line in file:
                if "=" not in line:
                    continue
                line = line.replace(" ", "").replace("\"", "").replace("'", "")
                secret_name = line.split("=")[0].upper()
                secret_value = line.split("=")[1]
                secret_dict[secret_name] = secret_value

    return secret_dict


def sync_secret_to_github(secret_name, secret_value, owner, repository):
    cmd = f"gh secret set {secret_name} --repo {owner}/{repository} --body '{secret_value}'"
    print(cmd)
    run(cmd, shell=True, check=True, text=True)


if __name__ == "__main__":


    parser = ArgumentParser()
    parser.add_argument('-s', '--secrets', dest='secrets', default='.env', help="The file name to create secrets for.")
    parser.add_argument('-r', '--repository', dest='repo', help="The name of the repository to import to.")
    parser.add_argument('-a', '--append-files', dest="appended", action="append", type=str,
                        help="Add more files for upload -- ex. ~/.aws/credentials.")
    parser.add_argument('-o', '--owner', dest="owner", required=True, help="The owner of the repository.")

    args = vars(parser.parse_args())

    owner = args["owner"]

    files = get_files_for_sync(args["secrets"], args["appended"])

    if args["repo"] is not None:
        repo = args["repo"]
    else:
        repo = get_current_repo_name()

    secrets = parse_secrets_file(files)

    for key, value in secrets.items():
        sync_secret_to_github(key, value, owner, repo)