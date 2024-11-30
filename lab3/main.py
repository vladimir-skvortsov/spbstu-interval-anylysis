import struct
import numpy as np
from scipy.stats import mode

def read_bin_file_with_numpy(file_path):
  with open(file_path, 'rb') as f:
    header_data = f.read(256)
    side, mode, frame_count = struct.unpack('<BBH', header_data[:4])

    frames = []
    point_dtype = np.dtype('<8H')

    for _ in range(frame_count):
      frame_header_data = f.read(16)
      stop_point, timestamp = struct.unpack('<HL', frame_header_data[:6])
      frame_data = np.frombuffer(f.read(1024 * 16), dtype=point_dtype)
      frames.append(frame_data)

    return np.concatenate(frames)

def convert_to_voltage(data):
  return data / 16384.0 - 0.5

def estimate_constants(x, y):
  a_estimates = y - x

  mode_result = mode(a_estimates, axis=None)
  count = np.atleast_1d(mode_result.count)

  if count.size > 0 and count[0] > 0:
    a_mode = mode_result.mode
  else:
    a_mode = np.nan

  def jaccard_index(a, x, y):
    intersection = np.sum((x + a) == y)
    union = len(x) + len(y) - intersection
    return intersection / union if union > 0 else 0

  a_best = a_mode
  jaccard_a = jaccard_index(a_best, x, y)

  return a_best, jaccard_a

x_data = read_bin_file_with_numpy('-0.205_Ivl_side_a_fast_data.bin')
y_data = read_bin_file_with_numpy('0.225_ Ivl_side_a_fast_data.bin')

x_voltage = convert_to_voltage(x_data)
y_voltage = convert_to_voltage(y_data)

a_best, jaccard_a = estimate_constants(x_voltage, y_voltage)

print(f"Estimated a: {a_best}")
print(f"Jaccard index for a: {jaccard_a}")
