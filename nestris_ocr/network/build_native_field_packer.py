import numpy as np


from numba.pycc import CC

cc = CC("native_fieldpacker")
cc.verbose = True


@cc.export("prePackField", "uint8[:](uint8[:,:])")
def prePackField(data):
    result = np.zeros((50,), dtype=np.uint8)
    index = 0
    currentByte = 0
    four_byte_counter = 0
    for y in range(20):
        for x in range(10):
            currentByte += data[y, x]
            four_byte_counter += 1
            if four_byte_counter == 4:
                result[index] = currentByte
                four_byte_counter = 0
                currentByte = 0
                index += 1
            currentByte = currentByte << 2

    return result


if __name__ == "__main__":
    cc.compile()
