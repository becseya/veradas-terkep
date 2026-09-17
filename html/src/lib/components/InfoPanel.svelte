<script>
  let isInfoOpen = false;

  const buildVersion = typeof __APP_BUILD_VERSION__ !== 'undefined' ? __APP_BUILD_VERSION__ : 'dev';
  const scrapedAt = typeof DATE_SCRAPED_AT !== 'undefined' ? new Date(DATE_SCRAPED_AT).toLocaleDateString() : '-';
</script>

<button
  class="info-fab"
  type="button"
  aria-label="Build info"
  aria-expanded={isInfoOpen}
  on:click={() => (isInfoOpen = !isInfoOpen)}
>
  <i class="fa-solid fa-circle-info" aria-hidden="true"></i>
</button>

{#if isInfoOpen}
  <section class="info-card" aria-label="Build info panel">
    <h3>Info</h3>
    <table>
      <tbody>
        <tr>
          <th scope="row">Adatbázis frissítve</th>
          <td>{scrapedAt}</td>
        </tr>
        <tr>
          <th scope="row">Verzió</th>
          <td>{buildVersion}</td>
        </tr>
        <tr>
          <th scope="row">Kapcsolat</th>
          <td><a href="mailto:662k69fg0@mozmail.com">662k69fg0@mozmail.com</a></td>
        </tr>
      </tbody>
    </table>
  </section>
{/if}

<style>
  .info-fab {
    position: absolute;
    top: 14px;
    right: 14px;
    z-index: 1200;
    width: 40px;
    height: 40px;
    border: 1px solid #c4d0dc;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.95);
    color: var(--text-main);
    box-shadow: 0 8px 20px rgba(14, 23, 33, 0.14);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
  }

  .info-fab:hover {
    background: #fff;
  }

  .info-card {
    position: absolute;
    top: 62px;
    right: 14px;
    z-index: 1190;
    width: min(360px, calc(100vw - 28px));
    border-radius: 14px;
    border: 1px solid var(--panel-border);
    background: rgba(255, 255, 255, 0.96);
    backdrop-filter: blur(7px);
    box-shadow: var(--shadow);
    padding: 12px 14px;
  }

  .info-card h3 {
    margin: 0 0 10px;
    font-size: 0.95rem;
    font-family: 'Space Grotesk', sans-serif;
  }

  .info-card table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.82rem;
  }

  .info-card th,
  .info-card td {
    text-align: left;
    border-top: 1px solid #e3e9f0;
    padding: 8px 0;
    vertical-align: top;
  }

  .info-card th {
    width: 45%;
    color: var(--text-muted);
    font-weight: 600;
  }

  .info-card td {
    color: var(--text-main);
    font-weight: 500;
    overflow-wrap: anywhere;
  }

  @media (max-width: 768px) {
    .info-fab {
      top: 10px;
      right: 10px;
      width: 38px;
      height: 38px;
    }

    .info-card {
      top: 56px;
      right: 10px;
      width: min(330px, calc(100vw - 20px));
    }
  }
</style>
