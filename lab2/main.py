# Import necessary modules
from interval import Interval
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize

# Define the IntervalMatrix and IntervalVector classes
class IntervalMatrix:
  def __init__(self, intervals):
    self.intervals = np.array(intervals)

  def mid(self):
    return [[interval.mid() for interval in row] for row in self.intervals]

  def rad(self):
    return [[interval.rad() for interval in row] for row in self.intervals]

class IntervalVector:
  def __init__(self, intervals):
    self.intervals = np.array(intervals)

  def mid(self):
    return [interval.mid() for interval in self.intervals]

  def rad(self):
    return [interval.rad() for interval in self.intervals]

# Define the tolerance functional
def tol(x, A, b):
  values = []

  for i in range(A.intervals.shape[0]):
    value = b.intervals[i].rad() - (-np.dot(A.intervals[i], x) + b.intervals[i].mid()).abs()
    values.append(value)

  return min(values)

# Check non-emptiness of the tolerance set
def is_non_empty_tolerance_set(A, b, epsilon=0.0001):
  def target(x):
    return -tol(x, A, b)

  mid_A = np.array(A.mid())
  mid_b = np.array(b.mid())
  initial_guess, _, _, _ = np.linalg.lstsq(mid_A, mid_b, rcond=None)

  result = minimize(target, initial_guess, method='BFGS', options={'gtol': epsilon})

  max_tol = -result.fun
  print(result)
  return max_tol >= 0

# Perform b-correction
def b_correction(b, K):
  e = IntervalVector([Interval(-1, 1) for _ in range(len(b.intervals))])
  corrected_b = IntervalVector([Interval(b_i.mid() + K, b_i.mid() + K) for b_i in b.intervals])
  return corrected_b

# Perform A-correction
def a_correction(A, K):
  corrected_intervals = [[Interval(a_ij.mid() + K, a_ij.mid() + K) for a_ij in row] for row in A.intervals]
  return IntervalMatrix(corrected_intervals)

# Plotting functions
def plot_tol_functional(A, b):
  x = np.linspace(-1, 3, 21)
  y = np.linspace(0, 4, 21)
  xx, yy = np.meshgrid(x, y)
  zz = np.array([[0 if tol([x, y], A, b) < 0 else 1 for x, y in zip(x_row, y_row)] for x_row, y_row in zip(xx, yy)])

  plt.contourf(xx, yy, zz, levels=1, colors=['lightcoral', 'lightgreen'])
  plt.colorbar()
  plt.xlabel('x1')
  plt.ylabel('x2')
  plt.show()

if __name__ == '__main__':
  # A = IntervalMatrix([
  #   [Interval(0.65, 1.25), Interval(0.70, 1.3)],
  #   [Interval(0.75, 1.35), Interval(0.70, 1.3)]
  # ])
  # b = IntervalVector([Interval(2.75, 3.15), Interval(2.85, 3.25)])

  # A = IntervalMatrix([
  #   [Interval(0.65, 1.25), Interval(0.70, 1.3)],
  #   [Interval(0.75, 1.35), Interval(0.70, 1.3)],
  #   [Interval(0.8, 1.4), Interval(0.70, 1.3)],
  # ])
  # b = IntervalVector([
  #   Interval(2.75, 3.15),
  #   Interval(2.85, 3.25),
  #   Interval(2.90, 3.3),
  # ])

  A = IntervalMatrix([
    [Interval(0.65, 1.25), Interval(0.70, 1.3)],
    [Interval(0.75, 1.35), Interval(0.70, 1.3)],
    [Interval(0.8, 1.4), Interval(0.70, 1.3)],
    [Interval(-0.3, 0.3), Interval(0.70, 1.3)],
  ])
  b = IntervalVector([
    Interval(2.75, 3.15),
    Interval(2.85, 3.25),
    Interval(2.90, 3.3),
    Interval(1.8, 2.2),
  ])

  if is_non_empty_tolerance_set(A, b):
    print('The tolerance set is non-empty.')
  else:
    print('The tolerance set is empty. Performing corrections.')

  K = 0
  corrected_A = a_correction(A, K)
  corrected_b = b_correction(b, K)
  plot_tol_functional(A, b)
