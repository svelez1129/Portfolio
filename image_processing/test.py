#!/usr/bin/env python3

import os
import pickle
import hashlib

import lab
import pytest

TEST_DIRECTORY = os.path.dirname(__file__)


def object_hash(x):
    return hashlib.sha512(pickle.dumps(x)).hexdigest()


def compare_images(im1, im2):
    assert set(im1.keys()) == {
        "height",
        "width",
        "pixels",
    }, "Incorrect keys in dictionary"
    assert im1["height"] == im2["height"], "Heights must match"
    assert im1["width"] == im2["width"], "Widths must match"
    assert (
        len(im1["pixels"]) == im1["height"] * im1["width"]
    ), "Incorrect number of pixels"
    assert all(isinstance(i, int) for i in im1["pixels"]), "Pixels must all be integers"
    assert all(
        0 <= i <= 255 for i in im1["pixels"]
    ), "Pixels must all be in the range from [0, 255]"
    pix_incorrect = (None, None)
    for ix, (i, j) in enumerate(zip(im1["pixels"], im2["pixels"])):
        if i != j:
            pix_incorrect = (ix, abs(i - j))
    assert pix_incorrect == (None, None), (
        "Pixels must match.  Incorrect value at location %s (differs from expected by %s)"
        % pix_incorrect
    )


def test_load():
    result = lab.load_greyscale_image(
        os.path.join(TEST_DIRECTORY, "test_images", "centered_pixel.png")
    )
    expected = {
        "height": 11,
        "width": 11,
        "pixels": [0]*60 + [255] + [0]*60,
    }
    compare_images(result, expected)


def test_inverted_1():
    im = lab.load_greyscale_image(
        os.path.join(TEST_DIRECTORY, "test_images", "centered_pixel.png")
    )
    result = lab.inverted(im)
    expected = {
        "height": 11,
        "width": 11,
        "pixels": [255]*60 + [0] + [255]*60
    }
    compare_images(result, expected)


def test_inverted_2():
    original = {
        "height": 1,
        "width": 4,
        "pixels": [26, 78, 139, 221],
    }
    result = lab.inverted(original)
    expected = {
        "height": 1,
        "width": 4,
        "pixels": [229, 177, 116, 34],
    }
    compare_images(result, expected)


@pytest.mark.parametrize("fname", ["mushroom", "twocats", "chess"])
def test_inverted_images(fname):
    inpfile = os.path.join(TEST_DIRECTORY, "test_images", "%s.png" % fname)
    expfile = os.path.join(TEST_DIRECTORY, "test_results", "%s_invert.png" % fname)
    im = lab.load_greyscale_image(inpfile)
    oim = object_hash(im)
    result = lab.inverted(im)
    expected = lab.load_greyscale_image(expfile)
    assert object_hash(im) == oim, "Be careful not to modify the original image!"
    compare_images(result, expected)


@pytest.mark.parametrize("kernsize", [1, 3, 7])
@pytest.mark.parametrize("fname", ["mushroom", "twocats", "chess"])
def test_blurred_images(kernsize, fname):
    inpfile = os.path.join(TEST_DIRECTORY, "test_images", "%s.png" % fname)
    expfile = os.path.join(
        TEST_DIRECTORY, "test_results", "%s_blur_%02d.png" % (fname, kernsize)
    )
    input_img = lab.load_greyscale_image(inpfile)
    input_hash = object_hash(input_img)
    result = lab.blurred(input_img, kernsize)
    expected = lab.load_greyscale_image(expfile)
    assert (
        object_hash(input_img) == input_hash
    ), "Be careful not to modify the original image!"
    compare_images(result, expected)


def test_blurred_black_image():
    # REPLACE THIS with your 1st test case from section 5.1
    original = {
        "height": 6,
        "width": 5,
        "pixels": [0] * 6 * 5,
    }
    input_hash = object_hash(original)
    # testing for size 3
    result = lab.blurred(original, 3)
    assert (
        object_hash(original) == input_hash
    ), "Be careful not to modify the original image!"
    compare_images(result, original)
    # testing for size 9
    result = lab.blurred(original, 9)
    assert (
        object_hash(original) == input_hash
    ), "Be careful not to modify the original image!"
    compare_images(result, original)


def test_blurred_centered_pixel():
    # loads in centered pixel image
    img_c = lab.load_greyscale_image("test_images/centered_pixel.png")
    input_hash = object_hash(img_c)
    # blurred img_c for size 3 255 in center
    expected3 = { # expected result of applying size n=3
        "height": img_c["height"],
        "width": img_c["width"],
        "pixels": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   28, 28, 28, 0, 0, 0, 0, 0, 0, 0, 0,
                   28, 28, 28, 0, 0, 0, 0, 0, 0, 0, 0,
                   28, 28, 28, 0, 0, 0, 0, 0, 0, 0, 0, 
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                   0, 0, 0, 0],
    }
    # blurred img for size 5 255 in center
    expected5 = { # expected result of applying size n=5
        "height": img_c["height"],
        "width": img_c["width"],
        "pixels": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 10, 10, 
                   10, 10, 0, 0, 0, 0, 0, 0, 10, 10, 10, 10, 
                   10, 0, 0, 0, 0, 0, 0, 10, 10, 10, 10, 10, 
                   0, 0, 0, 0, 0, 0, 10, 10, 10, 10, 10, 0, 0,
                   0, 0, 0, 0, 10, 10, 10, 10, 10, 0, 0, 0, 
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0]
    }
    # testing for size 3
    result = lab.blurred(img_c, 3)
    assert (
        object_hash(img_c) == input_hash
    ), "Be careful not to modify the original image!"
    compare_images(result, expected3)
    # testing for size 5
    result = lab.blurred(img_c, 5)
    assert (
        object_hash(img_c) == input_hash
    ), "Be careful not to modify the original image!"
    compare_images(result, expected5)


@pytest.mark.parametrize("kernsize", [1, 3, 9])
@pytest.mark.parametrize("fname", ["mushroom", "twocats", "chess"])
def test_sharpened_images(kernsize, fname):
    inpfile = os.path.join(TEST_DIRECTORY, "test_images", "%s.png" % fname)
    expfile = os.path.join(
        TEST_DIRECTORY, "test_results", "%s_sharp_%02d.png" % (fname, kernsize)
    )
    input_img = lab.load_greyscale_image(inpfile)
    input_hash = object_hash(input_img)
    result = lab.sharpened(input_img, kernsize)
    expected = lab.load_greyscale_image(expfile)
    assert (
        object_hash(input_img) == input_hash
    ), "Be careful not to modify the original image!"
    compare_images(result, expected)


@pytest.mark.parametrize("fname", ["mushroom", "twocats", "chess"])
def test_edges_images(fname):
    inpfile = os.path.join(TEST_DIRECTORY, "test_images", "%s.png" % fname)
    expfile = os.path.join(TEST_DIRECTORY, "test_results", "%s_edges.png" % fname)
    input_img = lab.load_greyscale_image(inpfile)
    input_hash = object_hash(input_img)
    result = lab.edges(input_img)
    expected = lab.load_greyscale_image(expfile)
    assert (
        object_hash(input_img) == input_hash
    ), "Be careful not to modify the original image!"
    compare_images(result, expected)


def test_edges_centered_pixel():
    centered_img = {
        "height": 11,
        "width": 11,
        "pixels": [0] * 11 * 11,
    }
    centered_img["pixels"][60] = 255  # Set the center pixel to white
    input_hash = object_hash(centered_img)
    result = lab.edges(centered_img)
    assert (
        object_hash(centered_img) == input_hash
    ), "Be careful not to modify the original image!"
    # Expected result
    print(result)
    expected = {
        "height": 11,
        "width": 11,
        "pixels": [
           	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 255, 255, 255, 0, 0, 0, 0,
                   0, 0, 0, 0, 255, 0, 255, 0, 0, 0, 0,
                   0, 0, 0, 0, 255, 255, 255, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        ],
    }
    compare_images(result, expected)


if __name__ == "__main__":
    import sys

    res = pytest.main(["-k", " or ".join(sys.argv[1:]), "-v", __file__])
