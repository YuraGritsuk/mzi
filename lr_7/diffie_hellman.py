from .utils import Curve, hexdec

CURVE_PARAMS = (
    hexdec("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFD97"),
    hexdec("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFD94"),
    hexdec("00000000000000000000000000000000000000000000000000000000000000a6"),
)


def diffie_hellman(d_a, d_b, G):
    curve = Curve(*CURVE_PARAMS)

    q_a = curve.scalar_multiply(d_a, G)
    q_b = curve.scalar_multiply(d_b, G)

    x_k_a, _ = curve.scalar_multiply(d_a, q_b)
    x_k_b, _ = curve.scalar_multiply(d_b, q_a)
    assert x_k_a == x_k_b

    return x_k_a


if __name__ == '__main__':
    d_a = 123123
    d_b = 432123
    G = (123123, 12312311)
    print(f"Shared private key: {diffie_hellman(d_a, d_b, G)}")
