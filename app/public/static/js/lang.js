let currentLang = "es";

async function setLanguage(lang) {
  currentLang = lang;
  const response = await fetch(`/static/lang/${lang}.json`);
  const data = await response.json();

  // Actualizar texto
  document.querySelectorAll("[data-translate]").forEach((el) => {
    const keys = el.getAttribute("data-translate").split(".");
    let text = data;
    keys.forEach((k) => (text = text[k]));
    if (text) el.textContent = text;
  });

  // Actualizar placeholders
  document.querySelectorAll("[data-placeholder]").forEach((el) => {
    const keys = el.getAttribute("data-placeholder").split(".");
    let placeholder = data;
    keys.forEach((k) => (placeholder = placeholder[k]));
    if (placeholder) el.placeholder = placeholder;
  });

  // Cambiar etiqueta de idioma
  if (document.getElementById("lang-label")) {
    document.getElementById("lang-label").textContent =
      lang === "es" ? "ES" : "EN";
  }
}

function toggleLanguage() {
  setLanguage(currentLang === "es" ? "en" : "es");
}

setLanguage("es");