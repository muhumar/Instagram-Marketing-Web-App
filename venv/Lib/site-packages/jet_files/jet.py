import sys
from jet_files import (
    status,
    push,
    pull,
    list_commits,
    commit_changeset,
    init,
    add,
    merge,
    help_text,
    local_tests,
    login,
    revert,
    hook,
    branch,
    diff,
    conflicts,
    setup,
    stash
)

# Possible commands people could type
# Matched up with the appropriate function call

commands = {
    "add": add.run,
    "push": push.run,
    "pull": pull.run,
    "commit": commit_changeset.run,
    "merge": merge.run,
    "status": status.run,
    "init": init.run,
    "help": help_text.run,
    "list": list_commits.run,
    "test": local_tests.run,
    "login": login.run,
    "hook": hook.run,
    "branch": branch.run,
    "revert": revert.run,
    "switch": branch.switch,
    "branches": branch.display,
    "diff": diff.run,
    "delete": branch.delete_branch,
    "resolve": conflicts.resolve,
    "conflicts": conflicts.list_conflicts,
    "setup": setup.run,
    "clone": pull.clone,
    "stash": stash.run,
    "unstash": stash.unstash,
}


def run():
    try:
        commands[sys.argv[1]]()
    except KeyError:
        print ("Invalid Command - Please see www.jetvc.co.uk/documentation/ "
               "for more info!")
    except IndexError:
        print ("Not enough arguments")
