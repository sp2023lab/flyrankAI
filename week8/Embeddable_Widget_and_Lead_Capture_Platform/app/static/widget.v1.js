(() => {
  "use strict";

  const script = document.currentScript;
  if (!script || !script.src) {
    console.error("FlyRank widget: could not locate the embed script element.");
    return;
  }

  const scriptUrl = new URL(script.src, window.location.href);
  const widgetId = scriptUrl.searchParams.get("id") || script.dataset.widgetId;
  if (!widgetId) {
    console.error("FlyRank widget: missing widget id. Use ?id=<public-widget-id>.");
    return;
  }

  const apiBase = scriptUrl.origin;
  const host = document.createElement("div");
  host.className = "flyrank-widget-host";
  host.dataset.widgetId = widgetId;
  script.insertAdjacentElement("afterend", host);

  const root = host.attachShadow ? host.attachShadow({ mode: "open" }) : host;

  const styles = document.createElement("style");
  styles.textContent = `
    :host { display: block; margin-top: 24px; }
    * { box-sizing: border-box; }
    .card {
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: #172033;
      border: 1px solid #dfe4ef;
      border-radius: 16px;
      padding: 22px;
      background: #ffffff;
    }
    h3 { margin: 0 0 8px; font-size: 1.3rem; }
    .description { margin: 0 0 18px; color: #667085; line-height: 1.5; }
    .field { margin: 0 0 15px; }
    label { display: block; margin-bottom: 6px; font-size: .92rem; font-weight: 700; }
    .required { color: #b42318; }
    input, textarea {
      display: block;
      width: 100%;
      border: 1px solid #cfd6e4;
      border-radius: 10px;
      padding: 10px 12px;
      background: #fff;
      color: #172033;
      font: inherit;
      outline: none;
      transition: border-color .15s ease, box-shadow .15s ease;
    }
    input:focus, textarea:focus {
      border-color: #5c6ac4;
      box-shadow: 0 0 0 3px rgba(92, 106, 196, .14);
    }
    textarea { min-height: 110px; resize: vertical; }
    button {
      border: 0;
      border-radius: 10px;
      padding: 10px 16px;
      background: #2639a8;
      color: #fff;
      font: inherit;
      font-weight: 800;
      cursor: pointer;
    }
    button:hover { filter: brightness(.96); }
    button:disabled { opacity: .58; cursor: wait; }
    .status { min-height: 1.4em; margin: 12px 0 0; font-size: .92rem; }
    .status.success { color: #067647; }
    .status.error { color: #b42318; }
    .loading { color: #667085; }
    .honeypot {
      position: absolute !important;
      left: -10000px !important;
      width: 1px !important;
      height: 1px !important;
      opacity: 0 !important;
      pointer-events: none !important;
    }
  `;
  root.appendChild(styles);

  const card = document.createElement("section");
  card.className = "card";
  card.setAttribute("aria-label", "FlyRank contact widget");

  const loading = document.createElement("p");
  loading.className = "loading";
  loading.textContent = "Loading contact form…";
  card.appendChild(loading);
  root.appendChild(card);

  function randomIdempotencyKey() {
    if (window.crypto && typeof window.crypto.randomUUID === "function") {
      return window.crypto.randomUUID();
    }
    // RFC-4122-shaped fallback for older demo browsers.
    return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (ch) => {
      const r = Math.floor(Math.random() * 16);
      const value = ch === "x" ? r : (r & 0x3) | 0x8;
      return value.toString(16);
    });
  }

  function statusMessage(element, message, kind = "") {
    element.className = `status ${kind}`.trim();
    element.textContent = message;
  }

  function createField(field) {
    const wrapper = document.createElement("div");
    wrapper.className = "field";

    const id = `flyrank-${widgetId}-${field.name}`;
    const label = document.createElement("label");
    label.htmlFor = id;
    label.textContent = field.label || field.name;

    if (field.required) {
      const required = document.createElement("span");
      required.className = "required";
      required.textContent = " *";
      required.setAttribute("aria-hidden", "true");
      label.appendChild(required);
    }

    const control = field.type === "textarea"
      ? document.createElement("textarea")
      : document.createElement("input");

    control.id = id;
    control.name = field.name;
    control.required = Boolean(field.required);
    control.maxLength = Number(field.max_length || 2000);

    if (field.type !== "textarea") {
      control.type = field.type === "email" ? "email" : "text";
      if (control.type === "email") control.autocomplete = "email";
      if (field.name.toLowerCase().includes("name")) control.autocomplete = "name";
    }

    wrapper.append(label, control);
    return wrapper;
  }

  async function loadWidget() {
    try {
      const response = await fetch(
        `${apiBase}/public/v1/widgets/${encodeURIComponent(widgetId)}/config`,
        { method: "GET", mode: "cors", credentials: "omit" },
      );

      if (!response.ok) {
        throw new Error(`Widget configuration request returned ${response.status}.`);
      }

      const config = await response.json();
      card.replaceChildren();

      const title = document.createElement("h3");
      title.textContent = config.title || "Contact us";
      card.appendChild(title);

      if (config.description) {
        const description = document.createElement("p");
        description.className = "description";
        description.textContent = config.description;
        card.appendChild(description);
      }

      const form = document.createElement("form");
      form.noValidate = false;

      for (const field of config.fields || []) {
        form.appendChild(createField(field));
      }

      // Honeypot: real users never interact with this field. Bots that fill it are silently dropped.
      const honeypot = document.createElement("input");
      honeypot.className = "honeypot";
      honeypot.type = "text";
      honeypot.name = "_website";
      honeypot.tabIndex = -1;
      honeypot.autocomplete = "off";
      honeypot.setAttribute("aria-hidden", "true");
      form.appendChild(honeypot);

      const submit = document.createElement("button");
      submit.type = "submit";
      submit.textContent = config.button_text || "Submit";

      const status = document.createElement("p");
      status.className = "status";
      status.setAttribute("role", "status");
      status.setAttribute("aria-live", "polite");

      form.append(submit, status);
      card.appendChild(form);

      // Keep the key after a network/server failure so retrying this same attempt cannot duplicate a row.
      let pendingIdempotencyKey = null;

      form.addEventListener("submit", async (event) => {
        event.preventDefault();
        if (!form.reportValidity()) return;

        pendingIdempotencyKey ||= randomIdempotencyKey();
        submit.disabled = true;
        statusMessage(status, "Submitting…");

        const fields = {};
        for (const field of config.fields || []) {
          const control = form.elements.namedItem(field.name);
          if (control) fields[field.name] = control.value;
        }

        try {
          const response = await fetch(
            `${apiBase}/public/v1/widgets/${encodeURIComponent(widgetId)}/submissions`,
            {
              method: "POST",
              mode: "cors",
              credentials: "omit",
              headers: {
                "Content-Type": "application/json",
                "Idempotency-Key": pendingIdempotencyKey,
              },
              body: JSON.stringify({ fields, _website: honeypot.value }),
            },
          );

          const body = await response.json().catch(() => ({}));

          if (!response.ok) {
            const retryAfter = response.headers.get("Retry-After");
            let message = body?.error?.message || `Submission failed (${response.status}).`;
            if (response.status === 429 && retryAfter) {
              message = `Too many submissions. Please try again in ${retryAfter} seconds.`;
            }
            throw new Error(message);
          }

          pendingIdempotencyKey = null;
          form.reset();
          statusMessage(status, "Thanks — your submission was received.", "success");
        } catch (error) {
          console.warn("FlyRank widget submission failed", error);
          statusMessage(status, error?.message || "Could not submit right now. Please try again.", "error");
        } finally {
          submit.disabled = false;
        }
      });
    } catch (error) {
      console.warn("FlyRank widget failed to load", error);
      card.replaceChildren();
      const message = document.createElement("p");
      message.className = "status error";
      message.setAttribute("role", "alert");
      message.textContent = "This contact form is temporarily unavailable.";
      card.appendChild(message);
    }
  }

  loadWidget();
})();