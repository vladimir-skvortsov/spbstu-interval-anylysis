import struct
import numpy as np

def read_bin_file_with_numpy(file_path):
  with open(file_path, 'rb') as f:
    header_data = f.read(256)
    side, mode, frame_count = struct.unpack('<BBH', header_data[:4])
    print(f"Side: {side}, Mode: {mode}, Frame Count: {frame_count}")

    frames = []
    point_dtype = np.dtype('<8H')

    for _ in range(frame_count):
      frame_header_data = f.read(16)
      stop_point, timestamp = struct.unpack('<HL', frame_header_data[:6])
      frame_data = np.frombuffer(f.read(1024 * 16), dtype=point_dtype)

      frames.append({
        'StopPoint': stop_point,
        'TimeStamp': timestamp,
        'Data': frame_data,
      })

    return {
      'FileHeader': {
        'Side': side,
        'Mode': mode,
        'FrameCount': frame_count,
      },
      'Frames': frames,
    }

if __name__ == '__main__':
  file_path = '-0.205_Ivl_side_a_fast_data.bin'
  data = read_bin_file_with_numpy(file_path)
  print(data)
