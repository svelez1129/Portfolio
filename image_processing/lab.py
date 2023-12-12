"""
6.101 Lab 1:
Image Processing
"""

#!/usr/bin/env python3

import math

from PIL import Image

# NO ADDITIONAL IMPORTS ALLOWED!


def get_pixel(image, row, col, edge_effect=None):
    """
    Returns the pixel for the given image, and includes an edge effect if specified,
    if not, it just returns the pixel according to the rows and columns given
    """
    # print(row, col)
    if row >= image["height"] or row < 0 or col >= image["width"] or col < 0:
        if edge_effect == "zero":
            return 0
        elif edge_effect == "extend":
            # if row < 0:  # if row is above image, it goes to zero
            #     row = 0
            row = max(row,0)
            if row >= image["height"]:  # if row is below image, it goes to bottom
                row = image["height"] - 1
            # if col < 0:  # if col is left image, it goes to zero
            #     col = 0
            col = max(col,0)
            if col >= image["width"]:  # if col is left image, it goes to rightmost
                col = image["width"] - 1
            return image["pixels"][(row * image["width"] + col)]
        elif edge_effect == "wrap":
            row -= (row // image["height"]) * image["height"]  # gets wrap image row
            col -= (col // image["width"]) * image["width"]  # gets wrap image col
            return image["pixels"][row * image["width"] + col]
    # print("outside", row, col)
    return image["pixels"][int(row * image["width"] + col)]


def set_pixel(image, row, col, color):
    image["pixels"][row * image["width"] + col] = color


def apply_per_pixel(image, func):
    """
    applies a function to each pixel inside of image
    """
    result = {
        "height": image["height"],
        "width": image["width"],
        "pixels": [0] * image["height"] * image["width"],
    }
    for row in range(image["height"]):
        for col in range(image["width"]):
            color = get_pixel(image, row, col)
            new_color = func(color)
            set_pixel(result, row, col, new_color)
    return result


def inverted(image):
    """
    returns a copy of the image but inverted, which means if the pixel
    is 0 then it turns into 255, if its 1 then 254, 2 then 253, etc.
    """
    return apply_per_pixel(image, lambda color: 255 - color)


# HELPER FUNCTIONS


def correlate(image, kern, boundary_behavior):
    """
    Compute the result of correlating the given image with the given kernel.
    `boundary_behavior` will one of the strings "zero", "extend", or "wrap",
    and this function will treat out-of-bounds pixels as having the value zero,
    the value of the nearest edge, or the value wrapped around the other edge
    of the image, respectively.

    if boundary_behavior is not one of "zero", "extend", or "wrap", return
    None.

    Otherwise, the output of this function should have the same form as a 6.101
    image (a dictionary with "height", "width", and "pixels" keys), but its
    pixel values do not necessarily need to be in the range [0,255], nor do
    they need to be integers (they should not be clipped or rounded at all).

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.

    DESCRIBE YOUR KERNEL REPRESENTATION HERE

    My kernel is a 1D array that represents a 2D array, similar to image["pixels"]
    """
    new_image = {}
    new_image["height"] = image["height"]
    new_image["width"] = image["width"]
    new_image["pixels"] = []
    scaled_sum = 0  # sum to put in the scaled pixels in temporarily
    ker_size = round(len(kern) ** (1 / 2))  # finds the n by n of each matrix
    x = ker_size // 2  # kernel offset
    if (
        boundary_behavior not in ("zero", "extend", "wrap")
    ):
        return None
    for index in range(len(image["pixels"])):
        col_i = index % image["width"]  # finds col ex: 1 % 5 = 5, gives column 1
        row_i = index // image["width"]  # finds row ex: 6//5 = 1, gives row 1
        for number, element in enumerate(kern):
            col_k = number % ker_size  # col of kernel
            row_k = number // ker_size  # row of kernel
            pixel = get_pixel(
                image, row_i - x + row_k, col_i - x + col_k, boundary_behavior
            )
            pixel *= element
            scaled_sum += pixel  # adds each scaled pixel to temporary sum
        new_image["pixels"].append(scaled_sum)
        scaled_sum = 0
    return new_image


def round_and_clip_image(image):
    """
    Given a dictionary, ensure that the values in the "pixels" list are all
    integers in the range [0, 255].

    All values should be converted to integers using Python's `round` function.

    Any locations with values higher than 255 in the input should have value
    255 in the output; and any locations with values lower than 0 in the input
    should have value 0 in the output.
    """
    new_image = {
        "height": image["height"],
        "width": image["width"],
        "pixels": [0] * (image["height"] * image["width"]),
    }

    def make_smaller_or_larger(color):
        if color > 255:
            return 255
        elif color < 0:
            return 0
        return color

    def rounded(color):
        return round(color)

    new_image = apply_per_pixel(image, make_smaller_or_larger)
    new_image = apply_per_pixel(new_image, rounded)
    return new_image


# FILTERS


def blurred(image, kernel_size):
    """
    Return a new image representing the result of applying a box blur (with the
    given kernel size) to the given input image.

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.
    """
    # first, create a representation for the appropriate n-by-n kernel (you may
    # wish to define another helper function for this)

    # then compute the correlation of the input image with that kernel

    # and, finally, make sure that the output is a valid image (using the
    # helper function from above) before returning it.
    # Create a copy of the input image
    new_image = {
        "height": image["height"],
        "width": image["width"],
        "pixels": image["pixels"][:],
    }
    # Create a blur kernel
    template_blur = [1] * kernel_size**2  # template for 1
    blur = [
        value / kernel_size**2 for value in template_blur
    ]  # changes 1 into kernel
    # Apply the blur operation to the new image
    new_image = correlate(new_image, blur, "extend")
    return round_and_clip_image(new_image)


def sharpened(image, n):
    """
    returns a sharpened version of the image, which is
    2*each pixel of the image - the blurred pixels of the image(which are
    gotten by applying the blurred function)
    """
    new_image = {
        "height": image["height"],
        "width": image["width"],
        "pixels": [0] * (image["height"] * image["width"]),
    }
    blurred_image = blurred(image, n)
    new_image["pixels"] = [2 * pixel for pixel in image["pixels"]]
    for index in range(len(new_image["pixels"])):
        new_image["pixels"][index] -= blurred_image["pixels"][index]
    return round_and_clip_image(new_image)


def edges(image):
    """
    returns edge detector of image by applying
    sobel operator to it. These are both the given kernel1(k1) and
    kernel2(k2)
    """
    new_image = {
        "height": image["height"],
        "width": image["width"],
        "pixels": [0] * image["height"] * image["width"],
    }
    k1 = [-1, -2, -1, 0, 0, 0, 1, 2, 1]  # first kernel
    k2 = [-1, 0, 1, -2, 0, 2, -1, 0, 1]  # second kernel
    k1_image = correlate(image, k1, "extend")  # created O1
    k2_image = correlate(image, k2, "extend")  # created O2
    for i in range(len(new_image["pixels"])):  # i(index)
        # represents round((O1^2 + O2^2)^(1/2))
        new_pixel = math.sqrt(
            (k1_image["pixels"][i] ** 2) + (k2_image["pixels"][i] ** 2)
        )
        new_image["pixels"][i] = round(new_pixel)
    return round_and_clip_image(new_image)


# HELPER FUNCTIONS FOR LOADING AND SAVING IMAGES


def load_greyscale_image(filename):
    """
    Loads an image from the given file and returns a dictionary
    representing that image.  This also performs conversion to greyscale.

    Invoked as, for example:
       i = load_greyscale_image("test_images/cat.png")
    """
    with open(filename, "rb") as img_handle:
        img = Image.open(img_handle)
        img_data = img.getdata()
        if img.mode.startswith("RGB"):
            pixels = [
                round(0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2]) for p in img_data
            ]
        elif img.mode == "LA":
            pixels = [p[0] for p in img_data]
        elif img.mode == "L":
            pixels = list(img_data)
        else:
            raise ValueError(f"Unsupported image mode: {img.mode}")
        width, height = img.size
        return {"height": height, "width": width, "pixels": pixels}


def save_greyscale_image(image, filename, mode="PNG"):
    """
    Saves the given image to disk or to a file-like object.  If filename is
    given as a string, the file type will be inferred from the given name.  If
    filename is given as a file-like object, the file type will be determined
    by the "mode" parameter.
    """
    out = Image.new(mode="L", size=(image["width"], image["height"]))
    out.putdata(image["pixels"])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


if __name__ == "__main__":
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place for
    # generating images, etc.

    # inversed bluegill
    bluegill = load_greyscale_image("test_images/bluegill.png")
    save_greyscale_image((inverted(bluegill)), "bluegillInverted.png", mode="PNG")
    # correlated pigbird
    kernel = [0] * 169
    kernel[26] = 1
    pigbird = load_greyscale_image("test_images/pigbird.png")
    # extend
    save_greyscale_image(
        (correlate(pigbird, kernel, "extend")), "PigbirdExt.png", mode="PNG"
    )
    # wrap
    save_greyscale_image(
        (correlate(pigbird, kernel, "wrap")), "PigbirdWrap.png", mode="PNG"
    )
    # zero
    save_greyscale_image(
        (correlate(pigbird, kernel, "zero")), "PigbirdZero.png", mode="PNG"
    )
    # blurred cat
    cat = load_greyscale_image("test_images/cat.png")
    save_greyscale_image((blurred(cat, 13)), "BlurredCat.png", mode="PNG")
    # sharpened python
    python = load_greyscale_image("test_images/python.png")
    save_greyscale_image((sharpened(python, 11)), "SharpPython.png", mode="PNG")
    # edged construct

    construct = load_greyscale_image("test_images/construct.png")
    save_greyscale_image((edges(construct)), "EdgesConstruct.png", mode="PNG")
