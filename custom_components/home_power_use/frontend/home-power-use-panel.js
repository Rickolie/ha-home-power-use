/*
 * Home Power Use - Standby Power side panel.
 * Plain web component without build step or external dependencies.
 */

const DOMAIN = "home_power_use";

const TRANSLATIONS = {
  en: {
    title: "Standby Power",
    live_power: "Current power",
    new_measurement: "New measurement",
    device_name: "Device name",
    device_name_placeholder: "e.g. TV, Coffee machine, Game console",
    start: "Start measurement",
    add_manually: "Add without measuring",
    standby_watts: "Standby power (W)",
    add: "Add",
    howto:
      "Put the device in standby (not in use, but plugged in) and press start. The baseline is measured first. Then you will be asked to unplug the device or switch it off at the wall. Avoid switching other large appliances on or off during the measurement.",
    phase_baseline: "Measuring baseline – leave “{name}” in standby",
    phase_waiting_for_off: "Now unplug “{name}” or switch it off completely",
    phase_waiting_hint:
      "Press the button once the device is unplugged or switched off at the socket.",
    phase_settling: "Waiting for the power reading to settle…",
    phase_measuring_off: "Measuring with “{name}” switched off",
    phase_done: "Measurement of “{name}” finished",
    phase_error: "Measurement failed",
    device_is_off: "Device is off",
    cancel: "Cancel",
    close: "Close",
    remeasure_again: "Measure again",
    seconds_left: "{s} s left",
    baseline: "Baseline",
    off: "Off",
    samples: "{n} samples",
    result_standby: "Standby power",
    warn_negative:
      "Power went up while the device was off. Something else probably switched on – the value was set to 0 W. Try measuring again.",
    warn_noisy:
      "The difference is smaller than the fluctuation of your power reading (±{noise} W). The result may be inaccurate; try again when your home is quiet.",
    error_no_samples: "No valid readings from the power sensor.",
    summary_total: "Total standby power",
    summary_avoidable: "Avoidable standby power",
    summary_saved_kwh: "Yearly savings",
    summary_saved_cost: "Yearly cost savings",
    summary_total_year: "{kwh} kWh / {cost} per year in total",
    summary_devices: "{n} of {total} devices can be switched off",
    devices: "Devices",
    no_devices: "No devices measured yet. Start your first measurement above.",
    col_device: "Device",
    col_standby: "Standby",
    col_switch_off: "Can be switched off",
    col_hours: "Standby hours / day",
    col_year: "Per year",
    col_saved: "Saved per year",
    col_measured: "Measured",
    remeasure: "Measure again",
    delete: "Delete",
    confirm_delete: "Delete “{name}”?",
    manual: "manual",
    sensor: "Sensor: {sensor}",
    sensor_unavailable: "unavailable",
    settings: "Settings",
    price: "Price: {price} per kWh",
    durations: "Baseline {b} s · Off {o} s · Settle {s} s",
    not_loaded: "The Standby Power integration is not loaded.",
  },
  nl: {
    title: "Sluipverbruik",
    live_power: "Huidig vermogen",
    new_measurement: "Nieuwe meting",
    device_name: "Apparaatnaam",
    device_name_placeholder: "bijv. TV, Koffiezetapparaat, Spelcomputer",
    start: "Start meting",
    add_manually: "Toevoegen zonder meten",
    standby_watts: "Sluipverbruik (W)",
    add: "Toevoegen",
    howto:
      "Zet het apparaat in stand-by (niet in gebruik, wel aangesloten) en druk op start. Eerst wordt de basis gemeten. Daarna wordt gevraagd de stekker eruit te halen of het apparaat helemaal uit te zetten. Zet tijdens de meting geen andere grote apparaten aan of uit.",
    phase_baseline: "Basismeting – laat “{name}” in stand-by staan",
    phase_waiting_for_off: "Haal nu de stekker van “{name}” eruit of zet het helemaal uit",
    phase_waiting_hint:
      "Druk op de knop zodra de stekker eruit is of het apparaat bij het stopcontact is uitgezet.",
    phase_settling: "Even wachten tot de meting stabiel is…",
    phase_measuring_off: "Meten met “{name}” uitgeschakeld",
    phase_done: "Meting van “{name}” klaar",
    phase_error: "Meting mislukt",
    device_is_off: "Apparaat is uit",
    cancel: "Annuleren",
    close: "Sluiten",
    remeasure_again: "Opnieuw meten",
    seconds_left: "nog {s} s",
    baseline: "Basis",
    off: "Uit",
    samples: "{n} metingen",
    result_standby: "Sluipverbruik",
    warn_negative:
      "Het vermogen steeg terwijl het apparaat uit stond. Waarschijnlijk ging er iets anders aan – de waarde is op 0 W gezet. Probeer opnieuw te meten.",
    warn_noisy:
      "Het verschil is kleiner dan de schommeling van je meting (±{noise} W). Het resultaat kan onnauwkeurig zijn; probeer het opnieuw als het rustig is in huis.",
    error_no_samples: "Geen geldige waarden van de vermogenssensor.",
    summary_total: "Totaal sluipverbruik",
    summary_avoidable: "Vermijdbaar sluipverbruik",
    summary_saved_kwh: "Besparing per jaar",
    summary_saved_cost: "Kostenbesparing per jaar",
    summary_total_year: "{kwh} kWh / {cost} per jaar in totaal",
    summary_devices: "{n} van {total} apparaten kunnen uit",
    devices: "Apparaten",
    no_devices: "Nog geen apparaten gemeten. Start hierboven je eerste meting.",
    col_device: "Apparaat",
    col_standby: "Stand-by",
    col_switch_off: "Kan uit",
    col_hours: "Stand-by uren / dag",
    col_year: "Per jaar",
    col_saved: "Bespaard per jaar",
    col_measured: "Gemeten",
    remeasure: "Opnieuw meten",
    delete: "Verwijderen",
    confirm_delete: "“{name}” verwijderen?",
    manual: "handmatig",
    sensor: "Sensor: {sensor}",
    sensor_unavailable: "niet beschikbaar",
    settings: "Instellingen",
    price: "Prijs: {price} per kWh",
    durations: "Basis {b} s · Uit {o} s · Wachten {s} s",
    not_loaded: "De Sluipverbruik integratie is niet geladen.",
  },
};

const ICON_PLUG =
  "M16,7V3H14V7H10V3H8V7H8C7,7 6,8 6,9V14.5L9.5,18V21H14.5V18L18,14.5V9C18,8 17,7 16,7Z";

const esc = (value) =>
  String(value ?? "").replace(
    /[&<>"']/g,
    (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]
  );

class HomePowerUsePanel extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._data = null;
    this._unsubPromise = null;
    this._built = false;
    this._devicesKey = null;
    this._devicesPending = false;
    this._error = null;
  }

  set hass(hass) {
    const first = !this._hass;
    this._hass = hass;
    if (!this._built) this._build();
    if (this._menuButton) this._menuButton.hass = hass;
    if (first || !this._unsubPromise) this._subscribe();
    this._renderLive();
  }

  get hass() {
    return this._hass;
  }

  set narrow(narrow) {
    this._narrow = narrow;
    if (this._menuButton) this._menuButton.narrow = narrow;
    this.toggleAttribute("narrow", !!narrow);
  }

  set panel(panel) {
    this._panel = panel;
  }

  connectedCallback() {
    if (this._hass && !this._unsubPromise) this._subscribe();
  }

  disconnectedCallback() {
    if (this._unsubPromise) {
      this._unsubPromise.then((unsub) => unsub()).catch(() => {});
      this._unsubPromise = null;
    }
  }

  /* ---------------------------------------------------------------- helpers */

  _t(key, vars = {}) {
    const lang = (this._hass?.locale?.language || this._hass?.language || "en").split("-")[0];
    const table = TRANSLATIONS[lang] || TRANSLATIONS.en;
    let text = table[key] ?? TRANSLATIONS.en[key] ?? key;
    for (const [k, v] of Object.entries(vars)) text = text.replaceAll(`{${k}}`, v);
    return text;
  }

  _locale() {
    return this._hass?.locale?.language || this._hass?.language || "en";
  }

  _num(value, digits = 1) {
    if (value === null || value === undefined || Number.isNaN(value)) return "–";
    return new Intl.NumberFormat(this._locale(), {
      minimumFractionDigits: digits,
      maximumFractionDigits: digits,
    }).format(value);
  }

  _money(value, digits = 2) {
    const currency = this._data?.settings?.currency || this._hass?.config?.currency || "EUR";
    try {
      return new Intl.NumberFormat(this._locale(), {
        style: "currency",
        currency,
        minimumFractionDigits: digits,
        maximumFractionDigits: digits,
      }).format(value || 0);
    } catch (e) {
      return `${this._num(value, digits)} ${currency}`;
    }
  }

  _date(iso) {
    if (!iso) return "";
    try {
      return new Intl.DateTimeFormat(this._locale(), { dateStyle: "medium" }).format(new Date(iso));
    } catch (e) {
      return iso.slice(0, 10);
    }
  }

  _ws(type, payload = {}) {
    return this._hass
      .callWS({ type: `${DOMAIN}/${type}`, ...payload })
      .catch((err) => {
        this._showToast(err?.message || String(err));
        throw err;
      });
  }

  _showToast(message) {
    this.dispatchEvent(
      new CustomEvent("hass-notification", {
        detail: { message },
        bubbles: true,
        composed: true,
      })
    );
  }

  _subscribe() {
    if (!this._hass?.connection) return;
    this._unsubPromise = this._hass.connection
      .subscribeMessage((data) => this._onData(data), { type: `${DOMAIN}/subscribe` })
      .catch((err) => {
        this._unsubPromise = null;
        this._error = err?.code === "unknown_command" || err?.code === "not_loaded"
          ? this._t("not_loaded")
          : err?.message || String(err);
        this._renderAll();
        return () => {};
      });
  }

  _onData(data) {
    this._data = data;
    this._error = null;
    this._renderAll();
  }

  /* ------------------------------------------------------------------ build */

  _build() {
    this._built = true;
    this.shadowRoot.innerHTML = `
      <style>${STYLE}</style>
      <div class="toolbar">
        <span class="menu"></span>
        <div class="main-title">${esc(this._t("title"))}</div>
        <div class="live" id="live"></div>
      </div>
      <div class="content">
        <div id="error" class="card error" hidden></div>
        <div class="summary" id="summary"></div>
        <div class="card" id="measure-card">
          <h2>${esc(this._t("new_measurement"))}</h2>
          <form id="start-form" autocomplete="off">
            <p class="hint">${esc(this._t("howto"))}</p>
            <label class="field">
              <span>${esc(this._t("device_name"))}</span>
              <input id="name" name="name" maxlength="100" required
                     placeholder="${esc(this._t("device_name_placeholder"))}">
            </label>
            <div class="actions">
              <button type="submit" class="primary" id="start-btn">${esc(this._t("start"))}</button>
              <button type="button" class="text" id="manual-toggle">${esc(this._t("add_manually"))}</button>
            </div>
            <div id="manual" class="manual" hidden>
              <label class="field small">
                <span>${esc(this._t("standby_watts"))}</span>
                <input id="manual-watts" type="number" min="0" step="0.1" inputmode="decimal">
              </label>
              <button type="button" id="manual-add">${esc(this._t("add"))}</button>
            </div>
          </form>
          <div id="status" hidden></div>
        </div>
        <div class="card">
          <h2>${esc(this._t("devices"))}</h2>
          <div id="devices"></div>
        </div>
        <div class="footer" id="footer"></div>
      </div>
    `;

    const root = this.shadowRoot;
    const menuButton = document.createElement("ha-menu-button");
    menuButton.hass = this._hass;
    menuButton.narrow = this._narrow;
    root.querySelector(".menu").appendChild(menuButton);
    this._menuButton = menuButton;

    root.getElementById("start-form").addEventListener("submit", (ev) => {
      ev.preventDefault();
      const name = root.getElementById("name").value.trim();
      if (!name) return;
      this._ws("measurement/start", { name }).then(() => {
        root.getElementById("name").value = "";
      });
    });

    root.getElementById("manual-toggle").addEventListener("click", () => {
      const manual = root.getElementById("manual");
      manual.hidden = !manual.hidden;
    });

    root.getElementById("manual-add").addEventListener("click", () => {
      const nameInput = root.getElementById("name");
      const wattsInput = root.getElementById("manual-watts");
      const name = nameInput.value.trim();
      if (!name) {
        nameInput.reportValidity();
        return;
      }
      const watts = parseFloat(wattsInput.value || "0");
      this._ws("device/add", { name, standby_power: Number.isFinite(watts) ? watts : 0 }).then(() => {
        nameInput.value = "";
        wattsInput.value = "";
        root.getElementById("manual").hidden = true;
      });
    });

    root.getElementById("status").addEventListener("click", (ev) => {
      const action = ev.target.closest("[data-action]")?.dataset.action;
      if (action === "device-off") this._ws("measurement/device_off");
      else if (action === "cancel") this._ws("measurement/cancel");
      else if (action === "again") {
        const m = this._data?.measurement;
        const deviceId = m?.result?.device_id || m?.device_id;
        if (deviceId) this._ws("measurement/start", { device_id: deviceId });
      }
    });

    const devices = root.getElementById("devices");
    devices.addEventListener("change", (ev) => this._onDeviceChange(ev));
    devices.addEventListener("click", (ev) => this._onDeviceClick(ev));
    devices.addEventListener("focusout", () => {
      // Apply updates that arrived while editing.
      setTimeout(() => {
        if (this._devicesPending && !this._isEditingDevices()) this._renderDevices(true);
      }, 0);
    });

    this._renderAll();
  }

  /* ------------------------------------------------------------- rendering */

  _renderAll() {
    if (!this._built) return;
    const errorEl = this.shadowRoot.getElementById("error");
    errorEl.hidden = !this._error;
    errorEl.textContent = this._error || "";
    this._renderLive();
    this._renderSummary();
    this._renderMeasurement();
    this._renderDevices();
    this._renderFooter();
  }

  _currentPower() {
    const sensor = this._data?.settings?.power_sensor;
    const state = sensor && this._hass?.states?.[sensor];
    if (!state || ["unknown", "unavailable"].includes(state.state)) return null;
    const value = parseFloat(state.state);
    if (!Number.isFinite(value)) return null;
    const unit = state.attributes?.unit_of_measurement;
    const factor = { kW: 1000, MW: 1e6, mW: 0.001 }[unit] ?? 1;
    return value * factor;
  }

  _renderLive() {
    if (!this._built || !this._data) return;
    const power = this._currentPower();
    const text =
      power === null ? this._t("sensor_unavailable") : `${this._num(power, power < 100 ? 1 : 0)} W`;
    const live = this.shadowRoot.getElementById("live");
    const html = `<span class="live-label">${esc(this._t("live_power"))}</span><span class="live-value">${esc(text)}</span>`;
    if (live.innerHTML !== html) live.innerHTML = html;
    const statusLive = this.shadowRoot.getElementById("status-live");
    if (statusLive) statusLive.textContent = text;
  }

  _renderSummary() {
    const el = this.shadowRoot.getElementById("summary");
    const t = this._data?.totals;
    if (!t) {
      el.innerHTML = "";
      return;
    }
    const tile = (label, value, sub = "", accent = false) => `
      <div class="tile ${accent ? "accent" : ""}">
        <div class="tile-label">${esc(label)}</div>
        <div class="tile-value">${esc(value)}</div>
        ${sub ? `<div class="tile-sub">${esc(sub)}</div>` : ""}
      </div>`;
    el.innerHTML =
      tile(
        this._t("summary_total"),
        `${this._num(t.total_standby_power)} W`,
        this._t("summary_total_year", {
          kwh: this._num(t.yearly_kwh_total, 0),
          cost: this._money(t.yearly_cost_total, 0),
        })
      ) +
      tile(
        this._t("summary_avoidable"),
        `${this._num(t.avoidable_standby_power)} W`,
        this._t("summary_devices", { n: t.switchable_count, total: t.device_count })
      ) +
      tile(this._t("summary_saved_kwh"), `${this._num(t.yearly_kwh_saved, 0)} kWh`, "", true) +
      tile(this._t("summary_saved_cost"), this._money(t.yearly_cost_saved), "", true);
  }

  _renderMeasurement() {
    const root = this.shadowRoot;
    const form = root.getElementById("start-form");
    const status = root.getElementById("status");
    const m = this._data?.measurement;
    const idle = !m || m.phase === "idle";
    form.hidden = !idle;
    status.hidden = idle;
    root.getElementById("start-btn").disabled = !this._data;
    if (idle) {
      status.innerHTML = "";
      return;
    }

    const name = esc(m.name || "");
    const titleKey = `phase_${m.phase}`;
    const title = esc(this._t(titleKey, { name: "\u0000" })).replace("\u0000", name);
    const progress =
      m.duration && m.remaining !== null
        ? Math.min(100, Math.max(0, ((m.duration - m.remaining) / m.duration) * 100))
        : null;
    const steps = ["baseline", "waiting_for_off", "measuring_off", "done"];
    const phaseIndex = m.phase === "settling" ? 2 : steps.indexOf(m.phase);

    let body = "";
    let buttons = "";
    if (["baseline", "settling", "measuring_off"].includes(m.phase)) {
      body = `
        <div class="progress"><div class="bar" style="width:${progress ?? 0}%"></div></div>
        <div class="row-between">
          <span>${esc(this._t("seconds_left", { s: m.remaining ?? 0 }))}</span>
          <span class="mono" id="status-live"></span>
        </div>`;
      buttons = `<button data-action="cancel">${esc(this._t("cancel"))}</button>`;
    } else if (m.phase === "waiting_for_off") {
      body = `
        <div class="unplug">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="${ICON_PLUG}"/></svg>
          <span>${esc(this._t("phase_waiting_hint"))}</span>
        </div>
        <div class="row-between"><span></span><span class="mono" id="status-live"></span></div>`;
      buttons = `
        <button class="primary big" data-action="device-off">${esc(this._t("device_is_off"))}</button>
        <button data-action="cancel">${esc(this._t("cancel"))}</button>`;
    } else if (m.phase === "done" && m.result) {
      const r = m.result;
      let warning = "";
      if (r.warning === "negative") warning = this._t("warn_negative");
      else if (r.warning === "noisy") warning = this._t("warn_noisy", { noise: this._num(r.noise) });
      body = `
        <div class="result">
          <div class="result-label">${esc(this._t("result_standby"))}</div>
          <div class="result-value">${esc(this._num(r.standby_power))} W</div>
        </div>
        ${warning ? `<div class="warning">${esc(warning)}</div>` : ""}`;
      buttons = `
        <button class="primary" data-action="cancel">${esc(this._t("close"))}</button>
        <button data-action="again">${esc(this._t("remeasure_again"))}</button>`;
    } else if (m.phase === "error") {
      body = `<div class="warning">${esc(
        m.error === "no_samples" ? this._t("error_no_samples") : m.error || ""
      )}</div>`;
      buttons = `<button class="primary" data-action="cancel">${esc(this._t("close"))}</button>`;
    }

    const readings =
      m.baseline_power !== null || m.off_power !== null
        ? `<div class="readings">
            <div><span>${esc(this._t("baseline"))}</span><b>${esc(this._num(m.baseline_power))} W</b>
              <small>${esc(this._t("samples", { n: m.baseline_samples }))}</small></div>
            <div><span>${esc(this._t("off"))}</span><b>${esc(this._num(m.off_power))} W</b>
              <small>${esc(this._t("samples", { n: m.off_samples }))}</small></div>
          </div>`
        : "";

    status.innerHTML = `
      <ol class="steps">
        ${steps
          .map(
            (_, i) =>
              `<li class="${i < phaseIndex ? "done" : i === phaseIndex ? "current" : ""}${
                m.phase === "error" ? " err" : ""
              }"></li>`
          )
          .join("")}
      </ol>
      <div class="status-title ${m.phase === "waiting_for_off" ? "attention" : ""}">${title}</div>
      ${body}
      ${readings}
      <div class="actions">${buttons}</div>
    `;
    this._renderLive();
  }

  _isEditingDevices() {
    const active = this.shadowRoot.activeElement;
    return !!active && this.shadowRoot.getElementById("devices").contains(active) && active.tagName === "INPUT" && active.type !== "checkbox";
  }

  _renderDevices(force = false) {
    const el = this.shadowRoot.getElementById("devices");
    const devices = this._data?.devices;
    const key = JSON.stringify([devices, this._data?.measurement?.phase, this._data?.settings?.currency]);
    if (!force && key === this._devicesKey) return;
    if (this._isEditingDevices()) {
      this._devicesPending = true;
      return;
    }
    this._devicesKey = key;
    this._devicesPending = false;

    if (!devices) {
      el.innerHTML = "";
      return;
    }
    if (!devices.length) {
      el.innerHTML = `<p class="empty">${esc(this._t("no_devices"))}</p>`;
      return;
    }
    const busy = ["baseline", "waiting_for_off", "settling", "measuring_off"].includes(
      this._data?.measurement?.phase
    );
    const rows = devices
      .map((d) => {
        const saved = d.can_switch_off;
        const measured = d.measured_at
          ? `${this._date(d.measured_at)}${
              d.noise !== null && d.noise !== undefined ? ` · ±${this._num(d.noise)} W` : ""
            }`
          : this._t("manual");
        const warn = d.warning
          ? `<span class="warn-dot" title="${esc(
              d.warning === "negative" ? this._t("warn_negative") : this._t("warn_noisy", { noise: this._num(d.noise) })
            )}">!</span>`
          : "";
        return `
        <tr data-id="${esc(d.id)}" class="${saved ? "switchable" : ""}">
          <td class="name" data-label="${esc(this._t("col_device"))}">
            <input class="inline" data-field="name" value="${esc(d.name)}" maxlength="100" aria-label="${esc(this._t("col_device"))}">
            <div class="measured">${esc(measured)} ${warn}</div>
          </td>
          <td class="num" data-label="${esc(this._t("col_standby"))}">
            <span class="with-unit"><input class="inline num" type="number" min="0" step="0.1" data-field="standby_power" value="${esc(d.standby_power)}" aria-label="${esc(this._t("col_standby"))}"> W</span>
          </td>
          <td class="center" data-label="${esc(this._t("col_switch_off"))}">
            <label class="switch">
              <input type="checkbox" data-field="can_switch_off" ${saved ? "checked" : ""} aria-label="${esc(this._t("col_switch_off"))}">
              <span class="slider"></span>
            </label>
          </td>
          <td class="num" data-label="${esc(this._t("col_hours"))}">
            <span class="with-unit"><input class="inline num short" type="number" min="0" max="24" step="0.5" data-field="standby_hours" value="${esc(d.standby_hours)}" aria-label="${esc(this._t("col_hours"))}"> h</span>
          </td>
          <td class="num" data-label="${esc(this._t("col_year"))}">
            ${esc(this._num(d.yearly_kwh, 1))} kWh<br><small>${esc(this._money(d.yearly_cost))}</small>
          </td>
          <td class="num saved-cell" data-label="${esc(this._t("col_saved"))}">
            ${
              saved
                ? `<b>${esc(this._num(d.yearly_kwh, 1))} kWh</b><br><small>${esc(this._money(d.yearly_cost))}</small>`
                : "–"
            }
          </td>
          <td class="row-actions">
            <button class="icon" data-action="remeasure" title="${esc(this._t("remeasure"))}" ${busy ? "disabled" : ""}>
              <svg viewBox="0 0 24 24"><path d="M17.65,6.35C16.2,4.9 14.21,4 12,4A8,8 0 0,0 4,12A8,8 0 0,0 12,20C15.73,20 18.84,17.45 19.73,14H17.65C16.83,16.33 14.61,18 12,18A6,6 0 0,1 6,12A6,6 0 0,1 12,6C13.66,6 15.14,6.69 16.22,7.78L13,11H20V4L17.65,6.35Z"/></svg>
            </button>
            <button class="icon danger" data-action="delete" title="${esc(this._t("delete"))}">
              <svg viewBox="0 0 24 24"><path d="M19,4H15.5L14.5,3H9.5L8.5,4H5V6H19M6,19A2,2 0 0,0 8,21H16A2,2 0 0,0 18,19V7H6V19Z"/></svg>
            </button>
          </td>
        </tr>`;
      })
      .join("");

    el.innerHTML = `
      <div class="table-wrap">
        <table>
          <thead><tr>
            <th>${esc(this._t("col_device"))}</th>
            <th class="num">${esc(this._t("col_standby"))}</th>
            <th class="center">${esc(this._t("col_switch_off"))}</th>
            <th class="num">${esc(this._t("col_hours"))}</th>
            <th class="num">${esc(this._t("col_year"))}</th>
            <th class="num">${esc(this._t("col_saved"))}</th>
            <th></th>
          </tr></thead>
          <tbody>${rows}</tbody>
        </table>
      </div>`;
  }

  _onDeviceChange(ev) {
    const input = ev.target;
    const field = input.dataset?.field;
    const id = input.closest("tr")?.dataset.id;
    if (!field || !id) return;
    let value;
    if (field === "can_switch_off") value = input.checked;
    else if (field === "name") {
      value = input.value.trim();
      if (!value) {
        this._renderDevices(true);
        return;
      }
    } else {
      value = parseFloat(input.value);
      if (!Number.isFinite(value) || value < 0 || (field === "standby_hours" && value > 24)) {
        this._renderDevices(true);
        return;
      }
    }
    this._ws("device/update", { device_id: id, [field]: value }).catch(() => this._renderDevices(true));
  }

  _onDeviceClick(ev) {
    const button = ev.target.closest("button[data-action]");
    const id = button?.closest("tr")?.dataset.id;
    if (!button || !id) return;
    const device = this._data?.devices?.find((d) => d.id === id);
    if (button.dataset.action === "delete") {
      if (confirm(this._t("confirm_delete", { name: device?.name ?? "" }))) {
        this._ws("device/delete", { device_id: id });
      }
    } else if (button.dataset.action === "remeasure") {
      this._ws("measurement/start", { device_id: id }).then(() =>
        this.shadowRoot.getElementById("measure-card").scrollIntoView({ behavior: "smooth", block: "start" })
      );
    }
  }

  _renderFooter() {
    const el = this.shadowRoot.getElementById("footer");
    const s = this._data?.settings;
    if (!s) {
      el.innerHTML = "";
      return;
    }
    const sensorName = this._hass?.states?.[s.power_sensor]?.attributes?.friendly_name || s.power_sensor;
    el.innerHTML = `
      <span>${esc(this._t("sensor", { sensor: sensorName }))}</span>
      <span>${esc(this._t("price", { price: this._money(s.energy_price, 3) }))}</span>
      <span>${esc(this._t("durations", { b: s.baseline_seconds, o: s.off_seconds, s: s.settle_seconds }))}</span>
      <a href="/config/integrations/integration/${DOMAIN}">${esc(this._t("settings"))}</a>`;
  }
}

const STYLE = `
  :host {
    display: block;
    min-height: 100vh;
    background: var(--primary-background-color, #fafafa);
    color: var(--primary-text-color, #212121);
    font-family: var(--paper-font-body1_-_font-family, Roboto, "Noto Sans", sans-serif);
    --hpu-accent: var(--success-color, #43a047);
    --hpu-radius: var(--ha-card-border-radius, 12px);
  }
  * { box-sizing: border-box; }
  [hidden] { display: none !important; }
  .toolbar {
    display: flex; align-items: center; gap: 8px;
    height: var(--header-height, 56px); padding: 0 16px 0 4px;
    background: var(--app-header-background-color, var(--primary-color));
    color: var(--app-header-text-color, var(--text-primary-color, #fff));
    border-bottom: var(--app-header-border-bottom, none);
    position: sticky; top: 0; z-index: 2;
  }
  .main-title { flex: 1; font-size: 20px; font-weight: 400; margin-left: 12px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  :host(:not([narrow])) .menu { display: none; }
  :host(:not([narrow])) .main-title { margin-left: 20px; }
  .live { display: flex; flex-direction: column; align-items: flex-end; line-height: 1.15; }
  .live-label { font-size: 11px; opacity: 0.8; text-transform: uppercase; letter-spacing: 0.04em; }
  .live-value { font-size: 16px; font-variant-numeric: tabular-nums; }
  .content { max-width: 1100px; margin: 0 auto; padding: 16px; display: flex; flex-direction: column; gap: 16px; }
  .card {
    background: var(--ha-card-background, var(--card-background-color, #fff));
    border-radius: var(--hpu-radius);
    box-shadow: var(--ha-card-box-shadow, none);
    border: 1px solid var(--ha-card-border-color, var(--divider-color, #e0e0e0));
    padding: 16px;
  }
  .card.error { color: var(--error-color, #db4437); border-color: var(--error-color, #db4437); }
  h2 { margin: 0 0 12px; font-size: 18px; font-weight: 500; }
  .hint { margin: 0 0 16px; color: var(--secondary-text-color); line-height: 1.5; }
  .summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; }
  .tile {
    background: var(--ha-card-background, var(--card-background-color, #fff));
    border: 1px solid var(--ha-card-border-color, var(--divider-color, #e0e0e0));
    border-radius: var(--hpu-radius); padding: 14px 16px;
  }
  .tile-label { font-size: 13px; color: var(--secondary-text-color); }
  .tile-value { font-size: 28px; font-weight: 500; margin-top: 4px; font-variant-numeric: tabular-nums; }
  .tile-sub { font-size: 12px; color: var(--secondary-text-color); margin-top: 4px; }
  .tile.accent .tile-value { color: var(--hpu-accent); }
  .field { display: flex; flex-direction: column; gap: 6px; font-size: 13px; color: var(--secondary-text-color); }
  .field.small { max-width: 200px; }
  input {
    font: inherit; font-size: 16px; color: var(--primary-text-color);
    background: var(--input-fill-color, var(--secondary-background-color, #f5f5f5));
    border: 1px solid var(--input-idle-line-color, var(--divider-color, #ccc));
    border-radius: 8px; padding: 10px 12px; width: 100%; min-width: 0;
  }
  input:focus { outline: 2px solid var(--primary-color); outline-offset: -1px; }
  .actions { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 16px; align-items: center; }
  .manual { display: flex; gap: 8px; align-items: flex-end; margin-top: 12px; flex-wrap: wrap; }
  button {
    font: inherit; font-size: 14px; font-weight: 500; cursor: pointer;
    border-radius: 20px; padding: 9px 18px; min-height: 40px;
    border: 1px solid var(--divider-color, #ccc);
    background: transparent; color: var(--primary-color);
  }
  button:hover:not(:disabled) { background: rgba(var(--rgb-primary-color, 3, 169, 244), 0.08); }
  button:disabled { opacity: 0.45; cursor: default; }
  button.primary { background: var(--primary-color); color: var(--text-primary-color, #fff); border-color: transparent; }
  button.primary:hover:not(:disabled) { filter: brightness(1.08); background: var(--primary-color); }
  button.big { font-size: 16px; padding: 12px 28px; min-height: 48px; }
  button.text { border-color: transparent; }
  button.icon { padding: 6px; min-height: 36px; width: 36px; border-color: transparent; color: var(--secondary-text-color); }
  button.icon svg { width: 20px; height: 20px; fill: currentColor; display: block; }
  button.icon.danger:hover { color: var(--error-color, #db4437); }
  .steps { display: flex; gap: 6px; list-style: none; margin: 0 0 14px; padding: 0; }
  .steps li { flex: 1; height: 4px; border-radius: 2px; background: var(--divider-color, #e0e0e0); }
  .steps li.done { background: var(--primary-color); }
  .steps li.current { background: var(--primary-color); opacity: 0.55; }
  .steps li.err { background: var(--error-color, #db4437); }
  .status-title { font-size: 18px; font-weight: 500; margin-bottom: 12px; }
  .status-title.attention { color: var(--warning-color, #ffa600); }
  .progress { height: 8px; border-radius: 4px; background: var(--divider-color, #e0e0e0); overflow: hidden; }
  .progress .bar { height: 100%; background: var(--primary-color); transition: width 0.9s linear; }
  .row-between { display: flex; justify-content: space-between; margin-top: 8px; color: var(--secondary-text-color); font-size: 14px; }
  .mono { font-variant-numeric: tabular-nums; }
  .unplug { display: flex; gap: 12px; align-items: center; color: var(--secondary-text-color); line-height: 1.5; }
  .unplug svg { width: 40px; height: 40px; flex: none; fill: var(--warning-color, #ffa600); }
  .readings { display: flex; gap: 24px; margin-top: 14px; flex-wrap: wrap; }
  .readings div { display: flex; flex-direction: column; }
  .readings span, .readings small { color: var(--secondary-text-color); font-size: 12px; }
  .readings b { font-size: 18px; font-weight: 500; font-variant-numeric: tabular-nums; }
  .result-label { color: var(--secondary-text-color); font-size: 13px; }
  .result-value { font-size: 40px; font-weight: 500; color: var(--hpu-accent); font-variant-numeric: tabular-nums; }
  .warning {
    margin-top: 12px; padding: 10px 12px; border-radius: 8px; line-height: 1.45;
    background: rgba(var(--rgb-warning-color, 255, 166, 0), 0.15); color: var(--primary-text-color);
  }
  .empty { color: var(--secondary-text-color); margin: 4px 0; }
  .table-wrap { overflow-x: auto; margin: 0 -16px; padding: 0 16px; }
  table { width: 100%; border-collapse: collapse; font-size: 14px; }
  th { text-align: left; font-weight: 500; font-size: 12px; color: var(--secondary-text-color); padding: 8px 6px; border-bottom: 1px solid var(--divider-color, #e0e0e0); white-space: nowrap; }
  td { padding: 8px 6px; border-bottom: 1px solid var(--divider-color, #e0e0e0); vertical-align: middle; }
  tbody tr:last-child td { border-bottom: none; }
  th.num, td.num { text-align: right; white-space: nowrap; }
  th.center, td.center { text-align: center; }
  td small { color: var(--secondary-text-color); }
  td.name { min-width: 160px; }
  .measured { font-size: 12px; color: var(--secondary-text-color); padding: 2px 8px 0; }
  tr.switchable .saved-cell b { color: var(--hpu-accent); }
  input.inline { background: transparent; border-color: transparent; padding: 6px 8px; font-size: 14px; }
  input.inline:hover { border-color: var(--divider-color, #ccc); }
  input.inline.num { width: 80px; text-align: right; }
  input.inline.short { width: 64px; }
  .with-unit { display: inline-flex; align-items: center; gap: 2px; }
  .row-actions { white-space: nowrap; text-align: right; }
  .warn-dot {
    display: inline-flex; align-items: center; justify-content: center; width: 16px; height: 16px;
    border-radius: 50%; background: var(--warning-color, #ffa600); color: #000; font-size: 11px; font-weight: 700; cursor: help;
  }
  .switch { position: relative; display: inline-block; width: 40px; height: 22px; vertical-align: middle; }
  .switch input { opacity: 0; width: 0; height: 0; position: absolute; }
  .slider { position: absolute; inset: 0; cursor: pointer; border-radius: 11px; background: var(--switch-unchecked-track-color, #9e9e9e); transition: 0.2s; }
  .slider::before { content: ""; position: absolute; width: 16px; height: 16px; left: 3px; top: 3px; border-radius: 50%; background: var(--switch-unchecked-button-color, #fff); transition: 0.2s; }
  .switch input:checked + .slider { background: var(--switch-checked-track-color, var(--hpu-accent)); }
  .switch input:checked + .slider::before { transform: translateX(18px); background: var(--switch-checked-button-color, #fff); }
  .switch input:focus-visible + .slider { outline: 2px solid var(--primary-color); outline-offset: 2px; }
  .footer { display: flex; flex-wrap: wrap; gap: 6px 18px; color: var(--secondary-text-color); font-size: 13px; padding: 0 4px 24px; }
  .footer a { color: var(--primary-color); }

  @media (max-width: 720px) {
    .content { padding: 12px; gap: 12px; }
    .tile-value { font-size: 22px; }
    .table-wrap { margin: 0; padding: 0; overflow: visible; }
    table, tbody, tr, td { display: block; width: 100%; }
    thead { display: none; }
    tr { border-bottom: 1px solid var(--divider-color, #e0e0e0); padding: 8px 0; display: grid; grid-template-columns: 1fr 1fr; }
    tbody tr:last-child { border-bottom: none; }
    td { border: none; padding: 4px 0; text-align: left !important; }
    td.name { grid-column: 1 / -1; }
    td[data-label]:not(.name)::before { content: attr(data-label); display: block; font-size: 11px; color: var(--secondary-text-color); }
    td.row-actions { grid-column: 1 / -1; text-align: right !important; }
    input.inline.num { text-align: left; padding-left: 0; width: 64px; }
  }
`;

if (!customElements.get("home-power-use-panel")) {
  customElements.define("home-power-use-panel", HomePowerUsePanel);
}
