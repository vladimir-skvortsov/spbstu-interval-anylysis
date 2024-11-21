import math
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
import intvalpy as ip

def is_tolerance_set_empty(A, b):
  max_tol = ip.linear.Tol.maximize(A, b)
  return max_tol[1] < 0, max_tol[0]

def b_correction(b, k):
  e = ip.Interval([[-k, k] for i in range(len(b))])
  return b + e

def find_b_correction_min_K(A, b, eps=10e-3, max_iterations=1000):
  prev_k = 0
  cur_k = 0
  iteration = 0
  corrected_b = b
  is_empty, _ = is_tolerance_set_empty(A, corrected_b)

  while is_empty and iteration <= max_iterations:
    prev_k = cur_k
    cur_k = math.exp(iteration)
    corrected_b = b_correction(b, cur_k)
    is_empty, _ = is_tolerance_set_empty(A, corrected_b)
    iteration += 1

  if is_empty:
    raise Exception('Could not find K for b-correction')

  iteration = 0

  while abs(prev_k - cur_k) > eps and iteration <= max_iterations:
    mid_k = (prev_k + cur_k) / 2

    corrected_b = b_correction(b, mid_k)
    is_empty, _ = is_tolerance_set_empty(A, corrected_b)

    if is_empty:
      prev_k = mid_k
    else:
      cur_k = mid_k

    iteration += 1

  corrected_b = b_correction(b, cur_k)

  return corrected_b, cur_k, iteration

def A_correction(A):
  max_tol = ip.linear.Tol.maximize(A, b)
  lower_bound = abs(max_tol[1]) / (abs(max_tol[0][0]) + abs(max_tol[0][1]))

  rad_A = ip.rad(A)
  upper_bound = rad_A[0][0]

  for a_i in rad_A:
    for a_ij in a_i:
      if a_ij < upper_bound:
        upper_bound = a_ij

  e = (lower_bound + upper_bound) / 2
  corrected_A = []

  for i in range(len(A)):
    A_i = []

    for j in range(len(A[0])):
      A_i.append([A[i][j]._a + e, A[i][j]._b - e])

    corrected_A.append(A_i)

  print(lower_bound, upper_bound)

  return ip.Interval(corrected_A)

def draw_tol(A, b):
  max_tol = ip.linear.Tol.maximize(A, b)

  grid_min, grid_max = max_tol[0][0] - 2, max_tol[0][0] + 2
  x_1_, x_2_ = np.mgrid[grid_min:grid_max:100j, grid_min:grid_max:100j]
  list_x_1 = np.linspace(grid_min, grid_max, 100)
  list_x_2 = np.linspace(grid_min, grid_max, 100)

  list_tol = np.zeros((100, 100))
  for idx_x1, x1 in enumerate(list_x_1):
    for idx_x2, x2 in enumerate(list_x_2):
      x = [x1, x2]
      tol_values = []
      for i in range(len(b)):
        sum_ = sum(A[i][j] * x[j] for j in range(len(x)))
        rad_b, mid_b = ip.rad(b[i]), ip.mid(b[i])
        tol = rad_b - ip.mag(mid_b - sum_)
        tol_values.append(tol)
      list_tol[idx_x1, idx_x2] = min(tol_values)

  fig = plt.figure()
  ax = fig.add_subplot(111, projection='3d')
  ax.plot_surface(x_1_, x_2_, list_tol, cmap="Greys")
  ax.scatter(*max_tol[0], max_tol[1], color='red', s=50)

  plt.show()

def plot_tol_functional(A, b, solution):
  x = np.linspace(float(solution[0]) - 2, float(solution[0]) + 2, 91)
  y = np.linspace(float(solution[1]) -2, float(solution[1]) + 2, 91)
  xx, yy = np.meshgrid(x, y)
  zz = np.array([[1 if ip.linear.Tol.value(A, b, [x, y]) >= 0 else 0 for x, y in zip(x_row, y_row)] for x_row, y_row in zip(xx, yy)])

  plt.contourf(xx, yy, zz, levels=1, colors=['lightcoral', 'lightgreen'])
  plt.colorbar()
  plt.xlabel('x1')
  plt.ylabel('x2')
  plt.show()

if __name__ == '__main__':
  # A = ip.Interval([
  #   [[3, 6], [-5, 2]],
  #   [[-5, 7], [-3, -1]]
  # ])
  # b = ip.Interval([
  #   [-2, 2],
  #   [-1, 1],
  # ])
  # A = ip.Interval([
  #   [[2, 5], [1, 2]],
  #   [[-7, -5], [6, 7]]
  # ])
  # b = ip.Interval([
  #   [3, 4],
  #   [7, 8],
  # ])

  # A = ip.Interval([
  #   [[0.65, 1.25], [0.70, 1.3]],
  #   [[0.75, 1.35], [0.70, 1.3]]
  # ])
  # b = ip.Interval([
  #   [2.75, 3.15],
  #   [2.85, 3.25],
  # ])

  # A = ip.Interval([
  #   [[0.65, 1.25], [0.70, 1.3]],
  #   [[0.75, 1.35], [0.70, 1.3]],
  #   [[0.8, 1.4], [0.70, 1.3]],
  # ])
  # b = ip.Interval([
  #   [2.75, 3.15],
  #   [2.85, 3.25],
  #   [2.90, 3.3],
  # ])

  A = ip.Interval([
    [[0.65, 1.25], [0.70, 1.3]],
    [[0.75, 1.35], [0.70, 1.3]],
    [[0.8, 1.4], [0.70, 1.3]],
    [[-0.3, 0.3], [0.70, 1.3]],
  ])
  b = ip.Interval([
    [2.75, 3.15],
    [2.85, 3.25],
    [2.90, 3.3],
    [1.8, 2.2],
  ])

  is_empty, solution = is_tolerance_set_empty(A, b)

  if is_empty:
    print('The tolerance set is empty. Performing corrections.')

    corrected_b, k, iteration = find_b_correction_min_K(A, b, 10e-3)
    b = corrected_b
    print(f'b-correction minimum k is {k} ({iteration} iterations)')

    # A = A_correction(A)
  else:
    print('The tolerance set is non-empty.')

  plot_tol_functional(A, b, solution)
  draw_tol(A, b)
