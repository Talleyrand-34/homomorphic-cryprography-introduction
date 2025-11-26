"""
TFHE Client-Server Programs
Split into two separate programs that communicate over a network.

Usage:
1. Run server.py first: python server.py
2. Run client.py: python client.py
"""

# ============================================================================
# SERVER.PY - Save this as server.py
# ============================================================================

import socket
import pickle
import warnings
from tfhe.boot_gates import NAND
from tfhe.keys import tfhe_parameters, empty_ciphertext

warnings.filterwarnings("ignore", "overflow encountered in scalar subtract")

HOST = '127.0.0.1'
PORT = 65432

def compute_nand(cloud_key, ciphertext1, ciphertext2):
    """Perform NAND operation on encrypted data"""
    print(f"\\nSERVER: Computing NAND on encrypted data")
    print(f"  Input 1 shape: {ciphertext1.shape}")
    print(f"  Input 2 shape: {ciphertext2.shape}")
    
    params = tfhe_parameters(cloud_key)
    result = empty_ciphertext(params, ciphertext1.shape)
    
    NAND(cloud_key, result, ciphertext1, ciphertext2)
    
    print(f"  Result shape: {result.shape}")
    print(f"SERVER: Computation complete")
    
    return result

def main():
    print("=" * 60)
    print("TFHE SERVER - Homomorphic NAND Computation")
    print("=" * 60)
    print(f"\\nSERVER: Starting server on {HOST}:{PORT}")
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print(f"SERVER: Listening for connections...")
        
        while True:
            conn, addr = s.accept()
            with conn:
                print(f"\\nSERVER: Client connected from {addr}")
                
                # Receive data size first
                data_size = int.from_bytes(conn.recv(8), byteorder='big')
                print(f"SERVER: Expecting {data_size} bytes of data")
                
                # Receive all data
                data = b''
                while len(data) < data_size:
                    packet = conn.recv(4096)
                    if not packet:
                        break
                    data += packet
                
                print(f"SERVER: Received {len(data)} bytes")
                
                # Deserialize data
                received = pickle.loads(data)
                cloud_key = received['cloud_key']
                ciphertext1 = received['ciphertext1']
                ciphertext2 = received['ciphertext2']
                
                print("SERVER: Deserialized encrypted data and cloud key")
                
                # Compute NAND
                result = compute_nand(cloud_key, ciphertext1, ciphertext2)
                
                # Serialize result
                result_data = pickle.dumps(result)
                result_size = len(result_data)
                
                print(f"SERVER: Sending {result_size} bytes back to client")
                
                # Send result size first, then data
                conn.sendall(result_size.to_bytes(8, byteorder='big'))
                conn.sendall(result_data)
                
                print("SERVER: Result sent successfully")
                print(f"SERVER: Connection with {addr} closed")
                print("\\nSERVER: Ready for next connection...")

if __name__ == "__main__":
    main()

