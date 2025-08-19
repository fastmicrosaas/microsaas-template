function downloadPDF() {
  window.print();
}

document.body.addEventListener("htmx:afterRequest", () => {
  // Le damos un pequeño delay para asegurar que la cookie nueva esté lista
  setTimeout(() => {
    const csrfToken = getCookie("csrf_token");
    if (csrfToken) {
      window.currentCsrfToken = csrfToken;
    }
  }, 50);
});

document.body.addEventListener("htmx:configRequest", (event) => {
  const csrfToken = window.currentCsrfToken || getCookie("csrf_token");

  if (csrfToken) {
    event.detail.headers["x-csrf-token"] = csrfToken;
  }
});

function getCookie(name) {
  const match = document.cookie.match(new RegExp("(^| )" + name + "=([^;]+)"));

  if (match) return match[2];
}
