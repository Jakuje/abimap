import filecmp
import os
from distutils import dir_util

import yaml
from pytest import fixture

from symbol_version import symbol_version


@fixture
def datadir(tmpdir, request):
    '''
    Fixture responsible for searching a folder with the same name of test
    module in the \'data\' directory and, if available, moving all contents
    to a temporary directory so tests can use them freely.
    '''
    filename = request.module.__file__
    test_dir, _ = os.path.splitext(filename)

    # Get the parent directory and the test module name
    parent_dir = os.path.dirname(test_dir)
    test_name = os.path.basename(test_dir)

    # Insert the "data" to search in the data directory
    data_dir = os.path.join(parent_dir, "data", test_name)

    # If there are data for such test, copy to a temporary directory
    if os.path.isdir(data_dir):
        dir_util.copy_tree(data_dir, str(tmpdir))

    return tmpdir


@fixture
def testcases(datadir):
    """
    Returns the test cases for a given test
    """
    input_list = datadir.listdir()

    all_tests = []

    # Read the testcases from the YAML files
    for test_input in input_list:
        if os.path.isfile(str(test_input)):
            _, file_type = os.path.splitext(str(test_input))
            if file_type.lower() == ".yml" or file_type.lower() == ".yaml":
                with open(str(test_input), 'r') as stream:
                    try:
                        all_tests.extend(yaml.load(stream))
                    except yaml.YAMLError as e:
                        print(e)

    return all_tests


class cd:
    """Class used to manage the working directory"""
    def __init__(self, new_path):
        self.new_path = str(new_path)

    def __enter__(self):
        self.saved_path = os.getcwd()
        os.chdir(self.new_path)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.saved_path)


def run_tc(tc, datadir, capsys):
    """
    Run a command test case (for update and new commands)

    :param tc: The tescase
    :param datadir: The path to the directory where the test input are
    :param capsys: The output capture fixture
    """

    # Change directory to the temporary directory
    with cd(datadir):
        # Get a parser
        parser = symbol_version.get_arg_parser()

        tc_in = tc["input"]
        tc_out = tc["output"]

        # Parse the testcase arguments
        args = parser.parse_args(tc_in["args"])

        # TODO Using args.input to give the input from stdin
        if not args.input:
            if tc_in["stdin"]:
                args.input = tc_in["stdin"]

        # Call the function
        args.func(args)

        # If there is an expected output file
        if tc_out["file"]:
            if args.out:
                assert filecmp.cmp(args.out, tc_out["file"], shallow=False)
            else:
                # Fail
                assert 0

        # Capture stdout and stderr
        out, err = capsys.readouterr()

        # If there is an expected output to stdout
        if tc_out["stdout"]:
            with open(tc_out["stdout"], "r") as tcout:
                expected = tcout.read()
                assert out == expected
        else:
            if out:
                # Fail
                assert 0

        # If there is an expected output to stderr (e.g. warnings)
        if tc_out["stderr"]:
            if err:
                with open(tc_out["stderr"], "r") as tcerr:
                    expected = tcerr.read()
                    assert err == expected
            else:
                print("Expected output in stderr")
                # Fail
                assert 0
        else:
            if err:
                print("Unexpected output in stderr")
                # Fail
                assert 0
