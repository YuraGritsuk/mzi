from codecs import getdecoder, getencoder


def strxor(a, b):
    return bytes(a_i ^ b_i for a_i, b_i in zip(bytearray(a), bytearray(b)))


_hexdecoder = getdecoder("hex")
_hexencoder = getencoder("hex")


def hexdec(data):
    return _hexdecoder(data)[0]


def hexenc(data):
    return _hexencoder(data)[0].decode("utf-8")


def bytes2long(raw):
    return int(hexenc(raw), 16)


def long2bytes(n):
    res = hex(int(n))[2:]
    s = hexdec(res)
    return s.rjust(Curve.SIZE, b'\x00')


def modinvert(a, n):
    if a < 0:
        # k^-1 = p - (-k)^-1 mod p
        return n - modinvert(-a, n)
    t, newt = 0, 1
    r, newr = n, a
    while newr:
        quotinent = r // newr
        t, newt = newt, t - quotinent * newt
        r, newr = newr, r - quotinent * newr
    if r > 1:
        return -1
    if t < 0:
        t += n
    return t


class Curve(object):
    SIZE = 32

    def __init__(self, p, a, b):
        self.p = bytes2long(p)
        self.a = bytes2long(a)
        self.b = bytes2long(b)

    def _pos(self, v):
        if v < 0:
            return v + self.p
        return v

    def _add(self, p1x, p1y, p2x, p2y):
        if p1x == p2x and p1y == p2y:
            # double
            t = ((3 * p1x * p1x + self.a) * modinvert(2 * p1y, self.p)) % self.p
        else:
            tx = self._pos(p2x - p1x) % self.p
            ty = self._pos(p2y - p1y) % self.p
            t = (ty * modinvert(tx, self.p)) % self.p
        tx = self._pos(t * t - p1x - p2x) % self.p
        ty = self._pos(t * (p1x - tx) - p1y) % self.p
        return tx, ty

    def scalar_multiply(self, degree, point):
        x, y = point
        tx, ty = x, y
        degree -= 1
        if not degree:
            raise ValueError("Bad degree value")

        while degree:
            if degree & 1:
                tx, ty = self._add(tx, ty, x, y)
            degree = degree >> 1
            x, y = self._add(x, y, x, y)
        return tx, ty
