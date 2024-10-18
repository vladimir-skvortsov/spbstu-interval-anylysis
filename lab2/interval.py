class Interval:
  def __init__(self, start, end):
    self.start = start
    self.end = end

  def __repr__(self):
    return f"[{self.start}, {self.end}]"

  def __str__(self):
    return self.__repr__()

  def __eq__(self, other):
    return self.start == other.start and self.end == other.end

  def __hash__(self):
    return hash((self.start, self.end))

  def __contains__(self, item):
    return self.start <= item <= self.end

  def __len__(self):
    return self.end - self.start

  def __add__(self, other):
    if isinstance(other, Interval):
      return Interval(self.start + other.start, self.end + other.end)
    if isinstance(other, (int, float)):
      return Interval(self.start + other, self.end + other)
    return NotImplemented

  def __sub__(self, other):
    return Interval(self.start - other.end, self.end - other.start)

  def __mul__(self, other):
    if isinstance(other, Interval):
      multiplications = (
        self.start * other.start,
        self.start * other.end,
        self.end * other.start,
        self.end * other.end,
      )
      return Interval(min(multiplications), max(multiplications))
    elif isinstance(other, (int, float)):
      if other >= 0:
        return Interval(self.start * other, self.end * other)
      else:
        return Interval(self.end * other, self.start * other)
    return NotImplemented

  def __truediv__(self, other):
    if 0 in other:
      raise ZeroDivisionError
    return self * Interval(1 / other.start, 1 / other.end)

  def __neg__(self):
    return Interval(-self.end, -self.start)

  def mid(self):
    return (self.start + self.end) / 2

  def wid(self):
    return self.end - self.start

  def rad(self):
    return self.wid() / 2

  def abs(self):
    return max(abs(self.start), abs(self.end))
