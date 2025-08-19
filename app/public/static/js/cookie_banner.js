const COOKIE_CONSENT_KEY = "cookie_consent";

function enableConsentedScripts() {
  const consent = JSON.parse(localStorage.getItem(COOKIE_CONSENT_KEY) || "{}");
  if (!consent.accepted) return;

  document.querySelectorAll('script[type="text/plain"]').forEach((script) => {
    const category = script.dataset.cookieCategory;
    if (consent.categories?.[category]) {
      const newScript = document.createElement("script");
      if (script.src) {
        newScript.src = script.src;
        newScript.async = script.async;
      } else {
        newScript.textContent = script.textContent;
      }
      document.head.appendChild(newScript);
    }
  });
}

function isAuthenticated() {
  return (
    document.cookie.includes("access_token=") ||
    document.cookie.includes("refresh_token=")
  );
}

function acceptCookies() {
  if (isAuthenticated()) {
    sendConsent("cookies", "1.0", true);
  }
  localStorage.setItem(
    COOKIE_CONSENT_KEY,
    JSON.stringify({
      accepted: true,
      categories: {
        necessary: true,
        analytics: true,
        ads: true,
      },
      date: new Date().toISOString(),
    })
  );
  hideBanner();

  enableConsentedScripts();
}

function rejectCookies() {
  if (isAuthenticated()) {
    sendConsent("cookies", "1.0", false);
  }
  localStorage.setItem(
    COOKIE_CONSENT_KEY,
    JSON.stringify({
      accepted: false,
      categories: {
        necessary: true,
        analytics: false,
        ads: false,
      },
      date: new Date().toISOString(),
    })
  );
  hideBanner();
  disableOptionalCookies();
}

function hideBanner() {
  document.getElementById("cookie-banner")?.classList.add("hidden");
  document.getElementById("cookie-overlay")?.classList.add("hidden");
  document.body.classList.remove("cookie-blocked");
  removeScrollListeners();
}

function closeBannerFromOverlay() {
  sendConsent("cookies", "1.0", false);
  hideBanner();
}

document.addEventListener("DOMContentLoaded", () => {
  const consentRaw = localStorage.getItem(COOKIE_CONSENT_KEY);
  const consent = consentRaw ? JSON.parse(consentRaw) : null;

  if (!consent) {
    document.body.classList.add("cookie-blocked");
    addScrollListeners();
  } else {
    hideBanner();
    if (!consent.accepted) {
      disableOptionalCookies();
    }
  }
});

function disableOptionalCookies() {
  deleteCookie("_ga");
  deleteCookie("_fbp");
}

function deleteCookie(name) {
  document.cookie =
    name + "=; Max-Age=0; path=/; domain=" + location.hostname + ";";
}

function addScrollListeners() {
  const events = ["wheel", "scroll", "touchmove"];
  events.forEach((evt) =>
    window.addEventListener(evt, highlightBannerOnce, { passive: true })
  );
}

function removeScrollListeners() {
  const events = ["wheel", "scroll", "touchmove"];
  events.forEach((evt) => window.removeEventListener(evt, highlightBannerOnce));
}

let bannerHighlighted = false;
function highlightBannerOnce() {
  if (bannerHighlighted) return;
  bannerHighlighted = true;

  const banner = document.getElementById("cookie-banner");
  if (banner) {
    banner.classList.add("cookie-banner-highlight");
    setTimeout(() => {
      banner.classList.remove("cookie-banner-highlight");
    }, 2000);
  }
}

document
  .getElementById("cookie-settings-btn")
  ?.addEventListener("click", () => {
    localStorage.removeItem("cookie_consent");
    document.getElementById("cookie-banner")?.classList.remove("hidden");
    document.getElementById("cookie-overlay")?.classList.remove("hidden");
    document.body.classList.add("cookie-blocked");
  });

function sendConsent(policyType, version, accepted = true) {
  fetch("/consents", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: new URLSearchParams({
      policy_type: policyType,
      version: version,
      accepted: accepted ? "true" : "false",
    }),
  }).catch((error) => {
    console.warn("Error al registrar consentimiento:", error);
  });
}
