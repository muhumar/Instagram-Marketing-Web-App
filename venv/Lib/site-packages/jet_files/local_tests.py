# Purpose of this file is to test the local version of the version control
# RESULTS array stores either "PASSED" or the error message,
#  depending on the result of the test
# At the end, the python file prints the RESULT array,
#  and gives a count of the error messages
import os
import shutil
from jet_files import helper_functions, init, add, commit_changeset
from jet_files import branch as b

RESULTS = []
EXPECTED_RESULT = "No changes found"
cwd = os.getcwd()
base_tests_path = os.path.join(os.path.dirname(os.path.realpath(__file__))
                               + '/../')
directory = os.path.join(cwd + '/tests_test_directory/')
file1 = os.path.join(directory + 'one.py')
file2 = os.path.join(directory + 'one/two.py')
file3 = os.path.join(directory + 'one/one.py')
file4 = os.path.join(directory + 'three.py')
file5 = os.path.join(directory + 'four.py')
file6 = os.path.join(directory + 'five/five.py')
file7 = os.path.join(directory + 'five/six/seven/eight/six.py')


def test_same_files():
    test_list = ['1',
                 '2',
                 '3',
                 '4',
                 '5']
    for test in test_list:
        diff = helper_functions.diff(os.path.join(base_tests_path
                                     + 'jet_files/tests/diff/same/'
                                       '%s/before.py' % test),
                                     os.path.join(base_tests_path
                                     + "jet_files/tests/diff/same/"
                                       "%s/after.py" % test))

        if diff == EXPECTED_RESULT:
            RESULTS.append("Passed")
        else:
            RESULTS.append("Same Test '%s' Failed" % test)
            RESULTS.append("Tried to open file %s" % os.path.join(
                base_tests_path
                + 'jet_files/tests/diff/same/%s/before.py' % test))
            RESULTS.append("Expected %s" % EXPECTED_RESULT)
            RESULTS.append("Received:\n %s" % diff)


def test_different_files():
    number_of_tests = 20
    for test in range(0, number_of_tests + 1):
        diff = helper_functions.diff(os.path.join(base_tests_path
                                     + 'jet_files/tests/diff/different'
                                       '/%s/before.py' % test),
                                     os.path.join(base_tests_path
                                     + "jet_files/tests/diff/different"
                                       "/%s/after.py" % test))

        answer = helper_functions.reform_file(os.path.join(base_tests_path
                                              + 'jet_files/tests/diff/'
                                                'different/'
                                                '%s/before.py' % test),
                                              diff.splitlines())

        difference = helper_functions.diff(os.path.join(base_tests_path
                                           + 'jet_files/tests/diff/different'
                                             '/%s/after.py'
                                           % test),
                                           answer)

        if difference == EXPECTED_RESULT:
            RESULTS.append("Passed")
        else:
            RESULTS.append("Different Test '%s' Failed" % test)


def test_diff_algorithm():
    print ("Testing diff algorithm")
    try:
        test_same_files()
    except Exception as e:
        print (e)
        RESULTS.append('FAILED DIFF')
    try:
        test_different_files()
    except Exception as e:
        print (e)
        RESULTS.append('FAILED DIFF')


def test_merges():
    number_of_tests = 15
    for i in range(1, number_of_tests + 1):
        parent_filename = os.path.join(base_tests_path
                                       + 'jet_files/tests/merge/%s/parent.py'
                                       % i)
        with open(parent_filename, 'r') as myFile:
            parent = myFile.read().splitlines()
        file1_filename = os.path.join(base_tests_path
                                      + 'jet_files/tests/merge/%s/file1.py'
                                      % i)
        with open(file1_filename, 'r') as myFile:
            fileone = myFile.read().splitlines()
        file2_filename = os.path.join(base_tests_path
                                      + 'jet_files/tests/merge/%s/file2.py'
                                      % i)
        with open(file2_filename, 'r') as myFile:
            filetwo = myFile.read().splitlines()
        result_filename = os.path.join(base_tests_path
                                       + 'jet_files/tests/merge/'
                                         '%s/expected_result.py' % i)
        with open(result_filename, 'r') as myFile:
            expected_result = myFile.read().splitlines()
        result = helper_functions.fix_file("irrelevant",
                                           parent, fileone, filetwo, test=True)
        split_result = result[0].splitlines()
        if helper_functions.diff(split_result, expected_result) \
                == EXPECTED_RESULT \
                or helper_functions.diff(result, expected_result)\
                == EXPECTED_RESULT:
            RESULTS.append('Passed')
        else:
            RESULTS.append("Merging Test '%s' Failed" % i)


def test_merging():
    print ("Testing merging algorithm")
    try:
        test_merges()
    except Exception as e:
        RESULTS.append('FAILED MERGING')
        print (e)


def test_get_jet_directory():
    expected_jet_directory = os.path.join(cwd + '/tests_test_directory')
    jet_directory = helper_functions.get_jet_directory()
    if jet_directory == expected_jet_directory:
        RESULTS.append("Passed")
    else:
        RESULTS.append("Failed get jet directory. Received %s, should be %s"
                       % (jet_directory, expected_jet_directory))


def setup():
    os.mkdir(directory)

    with open(file1, 'w') as myFile:
        myFile.write(file1)

    os.mkdir(os.path.join(directory + 'one/'))
    with open(file2, 'w') as myFile:
        myFile.write(file2)

    with open(file3, 'w') as myFile:
        myFile.write(file3)

    with open(file4, 'w') as myFile:
        myFile.write(file4)

    with open(file5, 'w') as myFile:
        myFile.write(file5)

    os.mkdir(os.path.join(directory + 'five/'))
    os.mkdir(os.path.join(directory + 'five/six/'))
    os.mkdir(os.path.join(directory + 'five/six/seven/'))
    os.mkdir(os.path.join(directory + 'five/six/seven/eight/'))

    with open(file6, 'w') as myFile:
        myFile.write(file6)

    with open(file7, 'w') as myFile:
        myFile.write(file7)

    os.chdir(directory)
    init.init()


def clear_up():
    shutil.rmtree(directory)
    os.chdir(cwd)


def test_current_files():
    expected_files = [file1, file2, file3, file4, file5, file6, file7]
    current_files = helper_functions.get_current_files(None)
    for f in expected_files:
        if f not in current_files:
            RESULTS.append("Failed current files")
        else:
            RESULTS.append("Passed")
    if not len(expected_files) == len(current_files):
        RESULTS.append("Failed current files length check")
    else:
        RESULTS.append("Passed")


def test_get_new_commit_number(expected_result):
    new_commit = helper_functions.get_new_commit_number()
    if not expected_result == new_commit:
        RESULTS.append("Failed get new commit")
    else:
        RESULTS.append("Passed")


def test_stored_files():
    expected_files = [file1, file2, file3, file4, file5, file6, file7]
    stored_files = helper_functions.get_stored_files(None)
    for f in expected_files:
        if f not in stored_files:
            RESULTS.append("Failed stored files")
        else:
            RESULTS.append("Passed")
    if not len(expected_files) == len(stored_files):
        RESULTS.append("Failed stored files length check")
    else:
        RESULTS.append("Passed")


def test_get_stored_hash():
    files = [file1, file2, file3, file4, file5, file6, file7]
    for f in files:
        file1hash = helper_functions.checksum_md5(f)
        stored_hash = helper_functions.get_stored_hash(f, None)
        if not file1hash == stored_hash:
            RESULTS.append("Failed stored hash")
        else:
            RESULTS.append("Passed")


def test_get_new_files_in_changeset(expected_result):
    new_files = helper_functions.get_new_files_in_changeset(None)
    if not len(new_files) == expected_result:
        RESULTS.append("Failed new files in changeset")
    else:
        RESULTS.append("Passed")


def test_get_deleted_files_in_changeset(expected_result):
    deleted_files = helper_functions.get_deleted_files_in_changeset(None)
    if not len(deleted_files) == expected_result:
        RESULTS.append("Failed deleted files in changeset")
    else:
        RESULTS.append("Passed")


def test_get_changed_files_in_changeset(expected_result):
    changed_files = helper_functions.get_changed_files_in_changeset(None)
    if not len(changed_files) == expected_result:
        RESULTS.append("Failed changed files in changeset")
    else:
        RESULTS.append("Passed")


def test_get_deleted_files(expected_result):
    deleted_files = helper_functions.get_deleted_files(None, None)
    if len(deleted_files) == expected_result:
        RESULTS.append('Passed')
    else:
        RESULTS.append('Failed deleted files test')


def test_get_changed_files(changed_file):
    changed_files = helper_functions.get_changed_files(None, None)
    if changed_file == 0:
        if len(changed_files) == 0:
            RESULTS.append("Passed")
        else:
            RESULTS.append("Failed amount of changed files")
    else:
        if len(changed_files) == 1:
            RESULTS.append("Passed")
        else:
            RESULTS.append("Failed amount of changed files")
        if changed_files[0] == changed_file:
            RESULTS.append("Passed")
        else:
            RESULTS.append("Failed which file was changed")


def test_get_file_change_number(filename, branch):
    result = helper_functions.get_file_change_number(branch, 1, filename)
    expected_result = 0

    if result == expected_result:
        RESULTS.append('Passed')
    else:
        RESULTS.append('Incorrect file change number')


def test_get_last_complete_file(branch):
    result, commit = helper_functions.get_last_complete_file(branch, file7)
    expected_result, commit_number = [file7], 0

    if result == expected_result:
        RESULTS.append('Passed')
    else:
        RESULTS.append('Failed last complete file. Received %s' % result)

    if commit == commit_number:
        RESULTS.append('Passed')
    else:
        RESULTS.append('Failed last complete file. Received %s' % commit)


def test_get_file_at(commit, expected_result, branch):
    result = helper_functions.get_file_at(branch, commit, file7)
    if result == expected_result:
        RESULTS.append('Passed')
    else:
        RESULTS.append("Failed 'get file at' test")


def test_get_highest_commit(expected_result, branch):
    result = helper_functions.get_highest_commit(branch)
    if result == expected_result:
        RESULTS.append('Passed')
    else:
        RESULTS.append('Get highest commit failed. Got %s, expected %s'
                       % (result, expected_result))


def test_hashing_algorithm_is_unique():
    # Used to debug, not really needed anymore...
    tests = [
        ["", "", "", "", "", ""],
        ["", "", "", "", ""],
        [""],
        []
    ]
    checksums = []
    for i in range(0, len(tests)):
        filename = os.path.join(directory + 'test%s' % i)
        with open(filename, 'w') as myFile:
            for line in tests[i]:
                myFile.write("%s\n" % line)
        checksums.append(helper_functions.checksum_md5(filename))
        os.remove(filename)

    if len(checksums) > len(set(checksums)):
        RESULTS.append("Checksum has a bug")
    else:
        RESULTS.append("Passed")


def test_filtering_files_by_jet_ignore():
    test_filenames = [
        'one.py',
        'one.py~',
        'one.pyc',
        '/home/.jet/test',
        '.jet/test',
        '/home/.jet',
        os.getcwd() + 'nope/one.py',
    ]
    expected_result = [
        'one.py'
    ]
    filters = [
        '*~',
        '*.pyc',
        'nope/',
        '*.jet*',
    ]
    with open(os.path.join(directory + '/.jet_ignore'), 'w') as myFile:
        for line in filters:
            myFile.write("%s\n" % line)
    result = helper_functions.filter_files_by_ignore(test_filenames)
    for f in expected_result:
        if f in result:
            RESULTS.append('Passed')
        else:
            RESULTS.append('Failed jet ignore')
    if len(expected_result) == len(result):
        RESULTS.append('Passed')
    else:
        RESULTS.append('Failed length test for jet ignore')


def test_relative():
    currentwd = '/home/connor/development/project/jet/tests/test_directory/'
    filename = [
        '/home/connor/development/project/jet/tests/test_directory/one',
        '/home/connor/development/project/jet/tests/other/one',
        '/home/connor/development/project/jet/other/other2/one',
        '/home/connor/development/project/jet/tests/test_directory/folder/one',
        '/home/connor/development/project/jet/tests/test_directory/f/a/b/one',
        '/home/connor/development/project/jet/tests/one',
        'one',
    ]
    expected_answer = [
        'one',
        '../other/one',
        '../../other/other2/one',
        'folder/one',
        'f/a/b/one',
        '../one',
        '../../../../../../../one'
    ]
    for i in range(0, len(filename)):
        if helper_functions.relative(filename[i],
                                     currentwd) == expected_answer[i]:
            RESULTS.append("Passed")
        else:
            RESULTS.append("Failed relative. Got '%s', expected '%s'"
                           % (helper_functions.relative(filename[i],
                                                        currentwd),
                              expected_answer[i]))


def test_branch(branch):
    test_get_jet_directory()
    test_current_files()
    test_stored_files()
    test_get_new_commit_number(1)
    test_get_stored_hash()
    test_get_new_files_in_changeset(0)
    test_get_deleted_files_in_changeset(0)
    test_get_changed_files_in_changeset(0)
    test_get_deleted_files(0)
    test_get_changed_files(0)
    test_get_last_complete_file(branch)
    test_get_file_at('0', expected_result=[file7], branch=branch)

    os.remove(file7)
    test_get_deleted_files(1)

    new_contents1 = ["", "", "", "", file7, "", "", file7, "", ""]
    with open(file7, 'w') as myFile:
        for line in new_contents1:
            myFile.write("%s\n" % line)
    test_get_changed_files(file7)
    test_get_highest_commit("0", branch)

    add.add(verbose=False)
    test_get_changed_files_in_changeset(1)
    commit_changeset.commit("This is a test message", verbose=False)
    test_get_highest_commit("1", branch)
    test_get_changed_files(0)
    test_get_file_change_number(file7, branch)
    test_get_last_complete_file(branch)
    test_get_file_at('1', expected_result=new_contents1, branch=branch)

    os.remove(file6)
    random_new_file = os.path.join(directory + 'random')
    with open(random_new_file, 'w') as myFile:
        myFile.write("lol")
    helper_functions.revert(branch, '0')
    test_get_file_at('0', [file7], branch)
    test_stored_files()

    new_contents2 = ["", "", "", "", "", ""]
    with open(file7, 'w') as myFile:
        for line in new_contents2:
            myFile.write("%s\n" % line)

    add.add(verbose=False)
    commit_changeset.commit("This is a test message", verbose=False)

    test_get_file_at("2", expected_result=new_contents2, branch=branch)
    test_get_file_at('1', expected_result=new_contents1, branch=branch)
    test_get_file_at('0', expected_result=[file7], branch=branch)

    test_get_changed_files(0)
    test_get_deleted_files(0)
    test_get_new_commit_number(3)
    test_current_files()


def test_common_functions():
    print ("Testing common functions")
    setup()
    try:
        test_branch('master')

        clear_up()
        setup()
        b.branch('test_branch')
        test_branch('test_branch')

        clear_up()
        setup()
        b.branch('test_branch')
        b.branch('second_test_branch')
        test_branch('second_test_branch')

        clear_up()
        setup()
        b.branch('test_branch')
        b.branch('second_test_branch')
        b.branch('third_test_branch')
        test_branch('third_test_branch')

        test_filtering_files_by_jet_ignore()
        test_relative()
        test_hashing_algorithm_is_unique()
    except Exception as e:
        RESULTS.append('FAILED')
        print (e)
    clear_up()


def test_dependencies():
    try:
        import requests
        RESULTS.append('Passed')
    except Exception as e:
        RESULTS.append('Failed importing requests')
        print (e)


def run():
    print ("Beginning tests...")
    test_dependencies()

    test_diff_algorithm()
    test_merging()
    test_common_functions()

    print ("Results:")
    number_of_tests = len(RESULTS)
    passed = 0
    for result in RESULTS:
        if result == 'Passed':
            passed += 1
            print (helper_functions.BColors.GREEN +
                "    Passed" + helper_functions.BColors.ENDC)
        else:
            print (helper_functions.BColors.RED +
                "    %s" % result + helper_functions.BColors.ENDC)

    print ("Passed %s out of %s tests" % (passed, number_of_tests))
