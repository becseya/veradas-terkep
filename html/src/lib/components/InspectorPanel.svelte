<script>
  import { getMonday, getNDaysFromDate, toISODate } from '../utils/date.js';

  export let location = null;
  export let visible = false;

  const dayLabels = ['H', 'K', 'Sze', 'Cs', 'P', 'Szo', 'V'];

  function closePanel() {
    location = null;
  }

  function calendarDays(appointments) {
    const today = new Date();
    const currentMonday = getMonday(today);
    const todayStr = toISODate(today);

    return Array.from({ length: 28 }, (_, index) => {
      const date = getNDaysFromDate(currentMonday, index);
      const dateKey = toISODate(date);
      const appointment = appointments[dateKey];

      return {
        date,
        isToday: dateKey === todayStr,
        appointment
      };
    });
  }

  $: days = location ? calendarDays(location.appointments) : [];
</script>

{#if visible && location}
  <section class="panel panel-inspector">
    <button class="close-btn" on:click={closePanel} aria-label="Bezárás">
      <i class="fa-solid fa-xmark"></i>
    </button>

    <h2>{location.name}</h2>
    <p class="address">
      <i class="fa-solid fa-location-dot"></i>
      {location.address}
    </p>

    <div class="calendar-grid">
      {#each dayLabels as label}
        <div class="calendar-header">{label}</div>
      {/each}

      {#each days as day}
        <div class:has-appointment={Boolean(day.appointment)} class:current={day.isToday} class="calendar-day">
          <span>{day.date.getDate()}</span>
          <span class="hours">{day.appointment?.start ?? ''}</span>
          <span class="hours">{day.appointment?.end ?? ''}</span>
        </div>
      {/each}
    </div>
  </section>
{/if}
