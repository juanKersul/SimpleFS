from pytest import fixture, raises, mark

from main import *


@fixture
def file_system_one_file():
    fs = SimpleFS(4, 3)
    f1_dot_txt = File(name="file.txt", blocks=[0, 2])
    fs.blocks = ["abc", "", "d", ""]
    fs.files = {"f1.txt": f1_dot_txt}
    fs.empty_blocks = [1, 3]
    yield fs


@fixture
def file_system_two_files():
    fs = SimpleFS(6, 4)
    f1_dot_txt = File(name="f1.txt", blocks=[0, 2])
    f2_dot_txt = File(name="f2.txt", blocks=[1, 4, 5])

    fs.blocks = ["1234", "abcd", "56", "", "efgh", "ijkl"]
    fs.files = {"f1.txt": f1_dot_txt, "f2.txt": f2_dot_txt}
    fs.empty_blocks = [3]
    yield fs


##########################
#### Test read
##########################
def test_read_file1(file_system_one_file: SimpleFS):
    assert file_system_one_file.read("f1.txt") == "abcd"


def test_read_file2(file_system_two_files):
    assert file_system_two_files.read("f1.txt") == "123456"
    assert file_system_two_files.read("f2.txt") == "abcdefghijkl"


def test_read_non_existing_file(file_system_two_files: SimpleFS):
    with raises(FileDoesNotExists):
        file_system_two_files.read("f3.txt")


##########################
#### Test delete
##########################


def test_delete_non_existing_fs(file_system_one_file: SimpleFS):
    with raises(FileDoesNotExists):
        file_system_one_file.delete("non_existing")


def test_delete_existing_fs(file_system_one_file: SimpleFS):
    file_system_one_file.delete("f1.txt")
    assert len(file_system_one_file.empty_blocks) == 4
    with raises(FileDoesNotExists):
        file_system_one_file.read("file.txt")


##########################
#### Test write
##########################
@mark.parametrize("data", ("ab", "abc", "abcde", "abcdef"))
def test_write(file_system_one_file: SimpleFS, data):
    file_system_one_file.write("f2.txt", data)
    assert file_system_one_file.read("f2.txt") == data


def test_write_non_enough_space(file_system_one_file: SimpleFS):
    with raises(NoEnoughSpaceRemainingException):
        file_system_one_file.write("f2.txt", "abcdefg")


def test_write_existing_file(file_system_two_files: SimpleFS):
    with raises(FileAlreadyExist):
        file_system_two_files.write("f2.txt", "abcdefg")


def test_simple_fs_read_write_behavior():
    fs = SimpleFS(3, 8)
    assert len(fs.blocks) == 3

    fs.write("file.txt", "dataxyz123")
    assert len(fs.files) == 1
    file_ = fs.files["file.txt"]
    assert len(file_.blocks) == 2

    b1, b2 = file_.blocks
    assert fs.blocks[b1] == "dataxyz1"
    assert fs.blocks[b2] == "23"

    assert fs.read("file.txt") == "dataxyz123"
