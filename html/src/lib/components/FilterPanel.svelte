<script>
  export let filters;
  export let collapsed = false;

  const dayLabels = [
    { label: 'H', value: 0 },
    { label: 'K', value: 1 },
    { label: 'Sze', value: 2 },
    { label: 'Cs', value: 3 },
    { label: 'P', value: 4 },
    { label: 'Szo', value: 5 },
    { label: 'V', value: 6 }
  ];

  const intervalLabels = [
    { label: 'Reggel (8-10)', value: 'morning' },
    { label: 'Délelőtt (10-13)', value: 'beforeLunch' },
    { label: 'Délután (13-17)', value: 'afterLunch' },
    { label: 'Este (17-19)', value: 'evening' }
  ];

  function updateDateRange(event) {
    filters = { ...filters, dateRange: event.currentTarget.value };
  }

  function toggleDay(dayValue) {
    const hasDay = filters.days.includes(dayValue);
    const nextDays = hasDay
      ? filters.days.filter((day) => day !== dayValue)
      : [...filters.days, dayValue];
    filters = { ...filters, days: nextDays };
  }

  function toggleInterval(intervalValue) {
    const hasInterval = filters.intervals.includes(intervalValue);
    const nextIntervals = hasInterval
      ? filters.intervals.filter((interval) => interval !== intervalValue)
      : [...filters.intervals, intervalValue];
    filters = { ...filters, intervals: nextIntervals };
  }

  function togglePanel() {
    collapsed = !collapsed;
  }

 function handleKeydown(event) {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      togglePanel();
    }
  }
</script>

<section class="panel panel-filters">
  <header class="panel-header"
    role="button"
    tabindex="0"
    on:click={togglePanel}
    on:keydown={handleKeydown}
  >
    <h3>Szűrők</h3>
    <button
      type="button"
      class:collapsed
      class="toggle-btn"
      aria-label="Szűrők lenyitása/felcsukása"
    >
      <i class="fa-solid fa-chevron-down"></i>
    </button>
  </header>

  {#if !collapsed}
    <div class="panel-body">
      <div class="filter-group">
        <label class="filter-title" for="filter-date-range">Dátum</label>
        <select id="filter-date-range" value={filters.dateRange} on:change={updateDateRange}>
          <option value="anytime">Bármikor</option>
          <option value="today">Ma</option>
          <option value="next_workday">Következő munkanap</option>
          <option value="this_week">A héten</option>
          <option value="next_week">Következő héten</option>
        </select>
      </div>

      <div class="filter-group">
        <span class="filter-title">Napok</span>
        <div class="day-filters">
          {#each dayLabels as day}
            <label class="day-filter">
              <input
                type="checkbox"
                checked={filters.days.includes(day.value)}
                on:change={() => toggleDay(day.value)}
              />
              <span>{day.label}</span>
            </label>
          {/each}
        </div>
      </div>

      <div class="filter-group">
        <span class="filter-title">Időszakok</span>
        <div class="interval-filters">
          {#each intervalLabels as interval}
            <label class="interval-filter">
              <input
                type="checkbox"
                checked={filters.intervals.includes(interval.value)}
                on:change={() => toggleInterval(interval.value)}
              />
              <span>{interval.label}</span>
            </label>
          {/each}
        </div>
      </div>
    </div>
  {/if}
</section>
