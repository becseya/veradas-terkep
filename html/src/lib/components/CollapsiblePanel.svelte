<script>
  export let title = '';
  export let collapsed = false;
  export let sectionClass = '';
  export let headerClass = '';
  export let bodyClass = '';
  export let toggleLabel = '';

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

<section class={`panel ${sectionClass}`.trim()}>
  <header
    class={`panel-header ${headerClass}`.trim()}
    role="button"
    tabindex="0"
    on:click={togglePanel}
    on:keydown={handleKeydown}
  >
    <h3>{title}</h3>
    <button
      type="button"
      class:collapsed
      class="toggle-btn"
      aria-label={toggleLabel || `${title} lenyitása/felcsukása`}
    >
      <i class="fa-solid fa-chevron-down"></i>
    </button>
  </header>

  {#if !collapsed}
    <div class={`panel-body ${bodyClass}`.trim()}>
      <slot />
    </div>
  {/if}
</section>