function setupRecaptchaForm(
  formId,
  recaptchaAction,
  tokenInputId,
  extraValidation
) {
  const form = document.getElementById(formId);

  if (!form) return;

  form.addEventListener("submit", function (e) {
    if (extraValidation && !extraValidation()) {
      e.preventDefault();
      return;
    }

    e.preventDefault();

    executeRecaptcha(recaptchaAction, function (token) {
      const tokenInput = document.getElementById(tokenInputId);
      if (tokenInput) {
        tokenInput.value = token;
      }
      form.submit();
    });
  });
}

function validateRegisterPasswords() {
  const password = document.getElementById("password");
  const confirmPassword = document.getElementById("confirm_password");
  const errorText = document.getElementById("password-error");

  if (password.value !== confirmPassword.value) {
    errorText.classList.remove("hidden");
    return false;
  } else {
    errorText.classList.add("hidden");
    return true;
  }
}

function showContactLoader() {
  const loader = document.getElementById("contact-loader");
  if (loader) {
    loader.classList.remove("hidden");
  }
  return true;
}
setupRecaptchaForm("login-form", "login", "g_recaptcha_response");
setupRecaptchaForm(
  "register-form",
  "register",
  "g_recaptcha_response_register",
  validateRegisterPasswords
);
setupRecaptchaForm(
  "contact-form",
  "contact",
  "g_recaptcha_response_contact",
  showContactLoader
);
