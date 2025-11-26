"""
TFHE Client-Server Programs
Split into two separate programs that communicate over a network.

Usage:
1. Run server.py first: python server.py
2. Run client.py: python client.py
"""


# ============================================================================
# CLIENT.PY - Save this as client.py
# ============================================================================

import socket
import pickle
import random
import warnings
import numpy
from tfhe.keys import tfhe_key_pair, tfhe_encrypt, tfhe_decrypt

warnings.filterwarnings("ignore", "overflow encountered in scalar subtract")

HOST = '127.0.0.1'
PORT = 65432

def main():
    print("=" * 60)
    print("TFHE CLIENT - Encrypted Computation")
    print("=" * 60)
    
    # Initialize random number generator
    rng = numpy.random.RandomState(123)
    size = 8
    
    # Generate key pair
    print("\\nCLIENT: Generating key pair...")
    secret_key, cloud_key = tfhe_key_pair(rng)
    print("CLIENT: Key pair generated")
    
    # Generate random data
    bits1 = numpy.array([random.choice([0, 1]) for _ in range(size)])
    bits2 = numpy.array([random.choice([0, 1]) for _ in range(size)])
    
    print(f"\\nCLIENT: Generated data")
    print(f"  Bits 1: {bits1}")
    print(f"  Bits 2: {bits2}")
    
    # Compute expected result
    expected_bits = numpy.array([1 if not (b1 and b2) else 0 
                                  for b1, b2 in zip(bits1, bits2)])
    print(f"  Expected NAND: {expected_bits}")
    
    # Encrypt data
    print(f"\\nCLIENT: Encrypting data...")
    ciphertext1 = tfhe_encrypt(rng, secret_key, bits1)
    ciphertext2 = tfhe_encrypt(rng, secret_key, bits2)
    print(f"CLIENT: Data encrypted (shapes: {ciphertext1.shape}, {ciphertext2.shape})")
    
    # Prepare data to send
    data_to_send = {
        'cloud_key': cloud_key,
        'ciphertext1': ciphertext1,
        'ciphertext2': ciphertext2
    }
    
    serialized_data = pickle.dumps(data_to_send)
    data_size = len(serialized_data)
    
    print(f"\\nCLIENT: Connecting to server at {HOST}:{PORT}")
    
    # Connect to server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print(f"CLIENT: Connected to server")
        
        # Send data size first, then data
        print(f"CLIENT: Sending {data_size} bytes to server...")
        s.sendall(data_size.to_bytes(8, byteorder='big'))
        s.sendall(serialized_data)
        print("CLIENT: Data sent successfully")
        
        # Receive result size
        print(f"\\nCLIENT: Waiting for server response...")
        result_size = int.from_bytes(s.recv(8), byteorder='big')
        print(f"CLIENT: Expecting {result_size} bytes")
        
        # Receive result
        result_data = b''
        while len(result_data) < result_size:
            packet = s.recv(4096)
            if not packet:
                break
            result_data += packet
        
        print(f"CLIENT: Received {len(result_data)} bytes")
    
    # Deserialize result
    result_ciphertext = pickle.loads(result_data)
    print("CLIENT: Deserialized encrypted result")
    
    # Decrypt result
    print(f"\\nCLIENT: Decrypting result...")
    answer_bits = tfhe_decrypt(secret_key, result_ciphertext)
    
    print(f"\\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"  Answer Bits:   {answer_bits}")
    print(f"  Expected Bits: {expected_bits}")
    
    # Verify
    if (answer_bits == expected_bits).all():
        print(f"\\n✓ SUCCESS: Server computation is correct!")
        print(f"  All {size} bits match expected NAND results")
    else:
        print(f"\\n✗ FAILURE: Server computation is incorrect!")
        mismatches = numpy.sum(answer_bits != expected_bits)
        print(f"  {mismatches} out of {size} bits don't match")
    
    print("=" * 60)

if __name__ == "__main__":
    main()

# ============================================================================
# INSTRUCTIONS
# ============================================================================

INSTRUCTIONS = '''
=============================================================================
SETUP INSTRUCTIONS
=============================================================================

1. Save the server code:
   Create a file named "server.py" and copy the SERVER_CODE section above

2. Save the client code:
   Create a file named "client.py" and copy the CLIENT_CODE section above

3. Run the server first:
   python server.py
   
   The server will start listening on port 65432

4. In a separate terminal, run the client:
   python client.py
   
   The client will:
   - Generate and encrypt data
   - Send encrypted data to server
   - Receive encrypted result
   - Decrypt and verify the result

5. The server can handle multiple client connections sequentially

=============================================================================
'''

# print("=" * 80)
# print("TFHE CLIENT-SERVER SPLIT PROGRAMS")
# print("=" * 80)
# print("\nThis artifact contains TWO separate programs:")
# print("1. SERVER_CODE - Copy to server.py")
# print("2. CLIENT_CODE - Copy to client.py")
# print("\n" + INSTRUCTIONS)
# print("\n--- SERVER CODE (save as server.py) ---")
# print(SERVER_CODE)
# print("\n--- CLIENT CODE (save as client.py) ---")
# print(CLIENT_CODE)
