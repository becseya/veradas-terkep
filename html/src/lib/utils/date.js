export function getMonday(date) {
  const next = new Date(date);
  const day = next.getDay();
  const diff = next.getDate() - day + (day === 0 ? -6 : 1);
  return new Date(next.setDate(diff));
}

export function getNDaysFromDate(date, n) {
  const next = new Date(date);
  next.setDate(next.getDate() + n);
  return next;
}

export function toISODate(date) {
  return String(date.toISOString().split('T')[0]);
}

export function getDatesForRange(range) {
  const today = new Date();
  const todayStr = toISODate(today);
  const currentMonday = getMonday(today);

  if (range === 'today') {
    return [todayStr];
  }

  if (range === 'next_workday') {
    const next = new Date(today);
    next.setDate(next.getDate() + 1);
    while (next.getDay() === 0 || next.getDay() === 6) {
      next.setDate(next.getDate() + 1);
    }
    return [toISODate(next)];
  }

  if (range === 'this_week') {
    return Array.from({ length: 7 }, (_, i) => toISODate(getNDaysFromDate(currentMonday, i)));
  }

  if (range === 'next_week') {
    const nextMonday = getNDaysFromDate(currentMonday, 7);
    return Array.from({ length: 7 }, (_, i) => toISODate(getNDaysFromDate(nextMonday, i)));
  }

  return null;
}
