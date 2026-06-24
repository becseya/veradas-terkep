import { getDatesForRange } from './date.js';

export const DEFAULT_FILTERS = {
  dateRange: 'anytime',
  days: [0, 1, 2, 3, 4, 5, 6],
  intervals: ['morning', 'beforeLunch', 'afterLunch', 'evening']
};

export function filterLocations(locations, settings) {
  const dateRangeDates = getDatesForRange(settings.dateRange);

  return locations.filter((location) => {
    return Object.entries(location.appointments).some(([dateStr, appointment]) => {
      if (dateRangeDates && !dateRangeDates.includes(dateStr)) {
        return false;
      }

      const dayMatch = settings.days.includes(appointment.dayOfWeek);
      const intervalMatch = appointment.intervals.some((interval) => settings.intervals.includes(interval));

      return dayMatch && intervalMatch;
    });
  });
}
