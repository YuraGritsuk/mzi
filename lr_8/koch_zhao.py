import numpy as np
from skimage import io
from skimage.util import view_as_blocks
from scipy.fftpack import dct, idct
from matplotlib import pyplot as plt

u1, v1 = 4, 5
u2, v2 = 5, 4
N = 8
P = 25


def double_to_byte(arr):
    return np.uint8(np.round(np.clip(arr, 0, 255), 0))


def increment_abs(x):
    return x + 1 if x >= 0 else x - 1


def decrement_abs(x):
    if np.abs(x) <= 1:
        return 0
    else:
        return x - 1 if x >= 0 else x + 1


def abs_diff_coeffs(transform):
    return abs(transform[u1, v1]) - abs(transform[u2, v2])


def valid_coeffs(transform, bit, threshold):
    difference = abs_diff_coeffs(transform)
    if (bit == 0) and (difference > threshold):
        return True
    elif (bit == 1) and (difference < -threshold):
        return True
    else:
        return False


def change_coeffs(transform, bit):
    coefs = transform.copy()
    if bit == 0:
        coefs[u1, v1] = increment_abs(coefs[u1, v1])
        coefs[u2, v2] = decrement_abs(coefs[u2, v2])
    elif bit == 1:
        coefs[u1, v1] = decrement_abs(coefs[u1, v1])
        coefs[u2, v2] = increment_abs(coefs[u2, v2])
    return coefs


def embed_bit(block, bit):
    patch = block.copy()
    coefs = dct(dct(patch, axis=0, norm='ortho'), axis=1, norm='ortho')
    while not valid_coeffs(coefs, bit, P) or (bit != retrieve_bit(patch)):
        coefs = change_coeffs(coefs, bit)
        patch = double_to_byte(idct(idct(coefs, axis=0, norm='ortho'), axis=1, norm='ortho'))
    return patch


def embed_message(orig, msg):
    changed = orig.copy()
    blue = changed[:, :, 2]
    blocks = view_as_blocks(blue, block_shape=(N, N))
    h = blocks.shape[1]
    for index, bit in enumerate(msg):
        i = index // h
        j = index % h
        block = blocks[i, j]
        blue[i * N: (i + 1) * N, j * N: (j + 1) * N] = embed_bit(block, bit)
    changed[:, :, 2] = blue
    return changed


def retrieve_bit(block):
    transform = dct(dct(block, axis=0), axis=1)
    return 0 if abs_diff_coeffs(transform) > 0 else 1


def retrieve_message(img, length):
    blocks = view_as_blocks(img[:, :, 2], block_shape=(N, N))
    h = blocks.shape[1]
    return [retrieve_bit(blocks[index//h, index%h]) for index in range(length)]


def to_bits(s):
    result = []
    for c in s:
        bits = bin(ord(c))[2:]
        result.extend(map(int, bits.rjust(8, '0')))
    return result


def from_bits(bits):
    chars = []
    for i in range(len(bits) // 8):
        byte_char = bits[i * 8:(i + 1) * 8]
        int_char = int(''.join(map(str, byte_char)), 2)
        chars.append(chr(int_char))
    return ''.join(chars)


if __name__ == '__main__':
    original = io.imread('pic.jpeg')
    test_message = to_bits("Hello")

    changed = embed_message(original, test_message)
    mes = retrieve_message(changed, len(test_message))

    print(from_bits(mes))
    io.imshow(np.hstack((original, changed)))
    plt.show()
