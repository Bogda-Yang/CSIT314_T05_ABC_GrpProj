const body = document.body;
const loginForm = document.querySelector("#login-form");
const registerForm = document.querySelector("#register-form");
const forgotForm = document.querySelector("#forgot-form");
const resetForm = document.querySelector("#reset-form");
const messageNode = document.querySelector("#auth-message");
const sendCodeButton = document.querySelector("#send-code-button");
const sendResetCodeButton = document.querySelector("#send-reset-code-button");
const tabButtons = document.querySelectorAll("[data-switch]");
const formsByMode = {
  login: loginForm,
  register: registerForm,
  forgot: forgotForm,
  reset: resetForm,
};

// 切换认证页提示信息
function setMessage(text, type = "") {
  messageNode.textContent = text;
  messageNode.className = `auth-message ${type}`.trim();
}

// 切换登录、注册、忘记密码界面
function switchMode(mode) {
  body.dataset.mode = mode;
  Object.entries(formsByMode).forEach(([key, form]) => {
    form?.classList.toggle("is-hidden", key !== mode);
  });

  document.querySelectorAll(".auth-tab").forEach((button) => {
    const isLoginGroup = ["login", "forgot", "reset"].includes(mode);
    button.classList.toggle(
      "is-active",
      button.dataset.switch === "register" ? mode === "register" : isLoginGroup
    );
  });

  setMessage("");
  const url = new URL(window.location.href);
  url.searchParams.set("mode", mode);
  window.history.replaceState({}, "", url);
}

// 统一发送认证相关请求
async function postJson(url, payload) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  const data = await response.json();
  if (!response.ok) {
    let message = "Request failed.";

    if (typeof data.detail === "string") {
      message = data.detail;
    } else if (Array.isArray(data.detail) && data.detail.length > 0) {
      message = data.detail
        .map((item) => item.msg || item.message)
        .filter(Boolean)
        .join("; ");
    } else if (typeof data.message === "string") {
      message = data.message;
    }

    throw new Error(message);
  }
  return data;
}

// 验证码按钮倒计时
function startCooldown(button, seconds) {
  let remaining = seconds;
  button.disabled = true;
  button.textContent = `Retry in ${remaining}s`;

  const timer = window.setInterval(() => {
    remaining -= 1;
    if (remaining <= 0) {
      window.clearInterval(timer);
      button.disabled = false;
      button.textContent = "Send Code";
      return;
    }
    button.textContent = `Retry in ${remaining}s`;
  }, 1000);
}

// 切换认证标签页
tabButtons.forEach((button) => {
  button.addEventListener("click", () => switchMode(button.dataset.switch));
});

// 发送注册验证码
sendCodeButton?.addEventListener("click", async () => {
  const email = registerForm.elements.email.value.trim();
  if (!email) {
    setMessage("Enter your email before requesting a verification code.", "error");
    return;
  }

  try {
    setMessage("Sending verification code...");
    await postJson("/api/auth/send-code", { email });
    setMessage("Verification code sent. Check your inbox.", "success");
    startCooldown(sendCodeButton, 60);
  } catch (error) {
    setMessage(error.message, "error");
  }
});

// 发送重置密码验证码
sendResetCodeButton?.addEventListener("click", async () => {
  const email = forgotForm.elements.email.value.trim();
  if (!email) {
    setMessage("Enter your email before requesting a reset code.", "error");
    return;
  }

  try {
    setMessage("Sending password reset code...");
    await postJson("/api/auth/send-reset-code", { email });
    setMessage("Password reset code sent. Check your inbox.", "success");
    startCooldown(sendResetCodeButton, 60);
  } catch (error) {
    setMessage(error.message, "error");
  }
});

// 登录账号
loginForm?.addEventListener("submit", async (event) => {
  event.preventDefault();

  const payload = {
    email: loginForm.elements.email.value.trim(),
    password: loginForm.elements.password.value,
  };

  try {
    setMessage("Logging in...");
    const result = await postJson("/api/auth/login", payload);
    setMessage(result.message, "success");
    window.location.href = result.redirect || "/";
  } catch (error) {
    setMessage("The email or password you entered is incorrect.", "error");
  }
});

// 注册账号
registerForm?.addEventListener("submit", async (event) => {
  event.preventDefault();

  const payload = {
    username: registerForm.elements.username.value.trim(),
    email: registerForm.elements.email.value.trim(),
    password: registerForm.elements.password.value,
    code: registerForm.elements.code.value.trim(),
  };

  try {
    setMessage("Creating your account...");
    const result = await postJson("/api/auth/register", payload);
    setMessage(result.message, "success");
    window.location.href = result.redirect || "/";
  } catch (error) {
    setMessage(error.message, "error");
  }
});

// 校验重置密码验证码
forgotForm?.addEventListener("submit", async (event) => {
  event.preventDefault();

  const payload = {
    email: forgotForm.elements.email.value.trim(),
    code: forgotForm.elements.code.value.trim(),
  };

  try {
    setMessage("Verifying reset code...");
    const result = await postJson("/api/auth/verify-reset-code", payload);
    resetForm.elements.email.value = payload.email;
    resetForm.elements.code.value = payload.code;
    switchMode(result.next_mode || "reset");
    setMessage(result.message, "success");
  } catch (error) {
    setMessage(error.message, "error");
  }
});

// 重置密码
resetForm?.addEventListener("submit", async (event) => {
  event.preventDefault();

  const payload = {
    email: resetForm.elements.email.value.trim(),
    code: resetForm.elements.code.value.trim(),
    password: resetForm.elements.password.value,
  };

  try {
    setMessage("Updating password...");
    const result = await postJson("/api/auth/reset-password", payload);
    setMessage(result.message, "success");
    window.location.href = result.redirect || "/auth?mode=login";
  } catch (error) {
    setMessage(error.message, "error");
  }
});
