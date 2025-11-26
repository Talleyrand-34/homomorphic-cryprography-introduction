import random
import warnings
import numpy
from tfhe.boot_gates import NAND
from tfhe.keys import tfhe_key_pair, tfhe_parameters, tfhe_encrypt, tfhe_decrypt, empty_ciphertext

# Ignores overflow detected by Numpy in `lwe_key_switch_translate_from_array` method.
warnings.filterwarnings("ignore", "overflow encountered in scalar subtract")

# Seed the random number generator.
rng = numpy.random.RandomState(123)

size = 8

# Generate random integers (0 or 1) instead of booleans
bits1 = numpy.array([random.choice([0, 1]) for _ in range(size)])
bits2 = numpy.array([random.choice([0, 1]) for _ in range(size)])

# Compute expected result: NAND operation
# NAND: not (b1 and b2) -> converts to 1 if not both are 1, else 0
expected_bits = numpy.array([1 if not (b1 and b2) else 0 for b1, b2 in zip(bits1, bits2)])

print(f"Bits 1: {bits1}")
print(f"Bits 2: {bits2}")
print(f"Expected Bits (NAND): {expected_bits}")
print()

# Generate key pair
secret_key, cloud_key = tfhe_key_pair(rng)
print(f"Secret Key: {secret_key.lwe_key.key}")
print()

# Encrypt the integer arrays
ciphertext1 = tfhe_encrypt(rng, secret_key, bits1)
ciphertext2 = tfhe_encrypt(rng, secret_key, bits2)

print("Ciphertext #1 - A:")
print(ciphertext1.a)
print()
print("Ciphertext #1 - B:")
print(ciphertext1.b)
print()

# Get parameters and create result ciphertext
params = tfhe_parameters(cloud_key)
result = empty_ciphertext(params, ciphertext1.shape)

print("Result - A (before operation):")
print(result.a)
print()
print("Result - B (before operation):")
print(result.b)
print()

# Perform homomorphic NAND operation
NAND(cloud_key, result, ciphertext1, ciphertext2)

# Decrypt the result
answer_bits = tfhe_decrypt(secret_key, result)

print(f"Answer Bits: {answer_bits}")
print()

# Verify the result
assert (answer_bits == expected_bits).all(), "NAND operation failed!"
print("✓ NAND operation successful! All bits match expected results.")
