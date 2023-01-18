import pytest
import os
import shutil
from src.video_compress import VideoCompressor


TEST_DIRECTORY = "tst/asset"
DEST_DIRECTORY = "tst/destination"
PROC_DIRECTORY = "tst/process"
DELETE_TEST_DIRECTORY = "tst/deltest"
TEST_VIDEO_PATH = "tst/asset/test_1.mp4"
TEST_VIDEO_PATH_2 = "tst/asset/test_2.mp4"
TEST_CREATE_VIDEO_PATH = "tst/asset/test_1_compressed.mp4"
TEST_CREATE_VIDEO_PATH_2 = "tst/asset/test_2_compressed.mp4"
TEST_DEST_VIDEO_PATH = "tst/destination/test_1_compressed.mp4"
TEST_DEST_VIDEO_PATH_2 = "tst/destination/test_2_compressed.mp4"


@pytest.fixture
def compressor():
    os.mkdir(DEST_DIRECTORY)
    os.mkdir(PROC_DIRECTORY)
    yield VideoCompressor(source=TEST_DIRECTORY, preset="medium")
    if os.path.isfile(TEST_CREATE_VIDEO_PATH):
        os.remove(TEST_CREATE_VIDEO_PATH)
    if os.path.isfile(TEST_CREATE_VIDEO_PATH_2):
        os.remove(TEST_CREATE_VIDEO_PATH_2)
    shutil.rmtree(DEST_DIRECTORY)
    shutil.rmtree(PROC_DIRECTORY)


def test_compress_video(compressor):
    original_size = os.path.getsize(TEST_VIDEO_PATH)
    compressor.compress_video(TEST_VIDEO_PATH, TEST_CREATE_VIDEO_PATH)
    assert(os.path.isfile(TEST_CREATE_VIDEO_PATH))
    compressed_size = os.path.getsize(TEST_CREATE_VIDEO_PATH)
    assert(original_size > compressed_size)


def test_compress_video_args(compressor):
    original_size = os.path.getsize(TEST_VIDEO_PATH)
    compressor.compress_video(TEST_VIDEO_PATH, TEST_CREATE_VIDEO_PATH, preset="medium")
    original_size = os.path.getsize(TEST_VIDEO_PATH)
    less_compressed_size = os.path.getsize(TEST_CREATE_VIDEO_PATH)
    os.remove(TEST_CREATE_VIDEO_PATH)

    compressor.compress_video(TEST_VIDEO_PATH, TEST_CREATE_VIDEO_PATH, crf=28, preset="slower")
    more_compressed_size = os.path.getsize(TEST_CREATE_VIDEO_PATH)
    os.remove(TEST_CREATE_VIDEO_PATH)
    assert(original_size > less_compressed_size)
    assert(less_compressed_size > more_compressed_size)


def test_scale_down_video(compressor):
    scale_compressor = VideoCompressor(source=TEST_DIRECTORY, scale=0.5)
    scale_compressor.run()
    ow, oh = VideoCompressor.get_dimension(TEST_VIDEO_PATH)
    nw, nh = VideoCompressor.get_dimension(TEST_CREATE_VIDEO_PATH)
    assert(ow == 2*nw) # this isn't strictly always true for all video
    assert(oh == 2*nh) # as resized video dimension have to be even.


def test_compressor_targets(compressor):
    compressor.get_targets()
    assert(len(compressor.targets) == 2)
    assert("test_1.mp4" in compressor.targets)
    assert("test_2.mp4" in compressor.targets)


def test_compressor_same_dir(compressor):
    compressor = VideoCompressor(source=TEST_DIRECTORY)
    compressor.run()
    assert(os.path.isfile(TEST_CREATE_VIDEO_PATH))
    assert(os.path.isfile(TEST_CREATE_VIDEO_PATH_2))
    orig_size_1 = os.path.getsize(TEST_VIDEO_PATH)
    orig_size_2 = os.path.getsize(TEST_VIDEO_PATH_2)
    new_size_1 = os.path.getsize(TEST_CREATE_VIDEO_PATH)
    new_size_2 = os.path.getsize(TEST_CREATE_VIDEO_PATH_2)
    assert(orig_size_1 > new_size_1)
    assert(orig_size_2 > new_size_2)


def test_compressor_destination_dir(compressor):
    test_dest_compressor = VideoCompressor(source=TEST_DIRECTORY, destination=DEST_DIRECTORY, preset="medium")
    test_dest_compressor.run()
    compressor.run()
    assert(os.path.isfile(TEST_DEST_VIDEO_PATH))
    assert(os.path.isfile(TEST_DEST_VIDEO_PATH_2))
    assert(len(os.listdir(DEST_DIRECTORY)) == 2)
    orig_comp_size_1 = os.path.getsize(TEST_CREATE_VIDEO_PATH)
    orig_comp_size_2 = os.path.getsize(TEST_CREATE_VIDEO_PATH_2)
    dest_comp_size_1 = os.path.getsize(TEST_DEST_VIDEO_PATH)
    dest_comp_size_2 = os.path.getsize(TEST_DEST_VIDEO_PATH_2)
    assert(orig_comp_size_1 == dest_comp_size_1)
    assert(orig_comp_size_2 == dest_comp_size_2)


def test_compressor_process_dir(compressor):
    test_proc_compressor = VideoCompressor(source=TEST_DIRECTORY, destination=DEST_DIRECTORY, process_dir=PROC_DIRECTORY, preset="medium")
    test_proc_compressor.run()
    compressor.run()
    assert(os.path.isfile(TEST_DEST_VIDEO_PATH))
    assert(os.path.isfile(TEST_DEST_VIDEO_PATH_2))
    assert(len(os.listdir(DEST_DIRECTORY)) == 2)
    assert(len(os.listdir(PROC_DIRECTORY)) == 0)
    orig_comp_size_1 = os.path.getsize(TEST_CREATE_VIDEO_PATH)
    orig_comp_size_2 = os.path.getsize(TEST_CREATE_VIDEO_PATH_2)
    dest_comp_size_1 = os.path.getsize(TEST_DEST_VIDEO_PATH)
    dest_comp_size_2 = os.path.getsize(TEST_DEST_VIDEO_PATH_2)
    assert(orig_comp_size_1 == dest_comp_size_1)
    assert(orig_comp_size_2 == dest_comp_size_2)


def test_compressor_delete_original(compressor):
    shutil.copytree(TEST_DIRECTORY, DELETE_TEST_DIRECTORY)
    test_del_compressor = VideoCompressor(source=DELETE_TEST_DIRECTORY, delete_original=True)
    test_del_compressor.run()
    del_dir_files = os.listdir(DELETE_TEST_DIRECTORY)
    assert(len(del_dir_files) == 3)
    assert(all(["compressed" in f for f in del_dir_files if f.endswith(".mp4")]))
    shutil.rmtree(DELETE_TEST_DIRECTORY)
