from typing import Dict, List
from dataclasses import dataclass


########################################################
#######Exceptions to be raised by SimpleFS methods######
########################################################
class FSException(Exception):
    pass


class NoEnoughSpaceRemainingException(FSException):
    pass


class FileAlreadyExist(FSException):
    pass


class FileDoesNotExists(FSException):
    pass


########################################################
########################################################


@dataclass
class File:
    def __init__(self, name: str, blocks: List[int]):
        self.name: str = name
        self.blocks: List[int] = blocks


@dataclass
class SimpleFS:

    def __init__(self, block_count: int, block_size: int):
        self.block_count: int = block_count
        self.block_size: int = block_size
        self.blocks: List[str] = ["" for _ in range(block_count)]
        self.empty_blocks: List[int] = [x for x in range(self.block_count)]
        self.files: Dict[str, File] = {}

    def read(self, filename: str):
        if filename in self.files:
            file_blocks = self.files[filename].blocks
            content = "".join(self.blocks[block_index] for block_index in file_blocks)
            return content
        else:
            raise FileDoesNotExists

    def write(self, filename, content):
        if filename in self.files:
            raise FileAlreadyExist
        content_blocks = [
            content[i : i + self.block_size]
            for i in range(0, len(content), self.block_size)
        ]
        content_blocks_size = len(content_blocks)
        if len(self.empty_blocks) < content_blocks_size:
            raise NoEnoughSpaceRemainingException
        start_index = -1
        for i in range(len(self.empty_blocks) - content_blocks_size + 1):
            if self.empty_blocks[i : i + content_blocks_size] == list(
                range(self.empty_blocks[i], self.empty_blocks[i] + content_blocks_size)
            ):
                start_index = i
                break

        if start_index == -1:
            self.__defragment()
            start_index = self.empty_blocks[0]

        allocated_blocks = self.empty_blocks[
            start_index : start_index + content_blocks_size
        ]
        self.files[filename] = File(filename, allocated_blocks)
        for i, block_index in enumerate(allocated_blocks):
            self.blocks[block_index] = content_blocks[i]
        del self.empty_blocks[start_index : start_index + content_blocks_size]

    def delete(self, filename):
        if filename in self.files:
            for block_index in self.files[filename].blocks:
                self.blocks[block_index] = ""
                self.empty_blocks.append(block_index)
                self.empty_blocks.sort()
            del self.files[filename]
        else:
            raise FileDoesNotExists
    def __defragment(self):
        new_blocks = ["" for _ in range(self.block_count)]
        new_empty_blocks = [x for x in range(self.block_count)]
        new_files = {}
        new_empty_blocks_index = 0
        for _, file in self.files.items():
            for block_index in file.blocks:
                new_blocks[new_empty_blocks[new_empty_blocks_index]] = self.blocks[block_index]
                new_empty_blocks_index += 1
        self.blocks = new_blocks
        self.empty_blocks = new_empty_blocks
        self.files = new_files