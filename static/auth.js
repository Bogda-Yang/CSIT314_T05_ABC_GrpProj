const body = document.body;
const messageNode = document.querySelector("#auth-message");
const sendCodeButton = document.querySelector("#send-code-button");
const sendResetCodeButton = document.querySelector("#send-reset-code-button");
const loginSubmitButton = document.querySelector("#login-submit-button");
const registerSubmitButton = document.querySelector("#register-submit-button");
const forgotSubmitButton = document.querySelector("#forgot-submit-button");
const resetSubmitButton = document.querySelector("#reset-submit-button");
const tabButtons = document.querySelectorAll("[data-switch]");

const formsByMode = {
  login: document.querySelector("#login-form"),
  register: document.querySelector("#register-form"),
  forgot: document.querySelector("#forgot-form"),
  reset: document.querySelector("#reset-form"),
};

const fields = {
  loginEmail: document.querySelector("#login-email"),
  loginPassword: document.querySelector("#login-password"),
  registerUsername: document.querySelector("#register-username"),
  registerEmail: document.querySelector("#register-email"),
  registerPassword: document.querySelector("#register-password"),
  registerCode: document.querySelector("#register-code"),
  forgotEmail: document.querySelector("#forgot-email"),
  forgotCode: document.querySelector("#forgot-code"),
  resetEmail: document.querySelector("#reset-email"),
  resetCode: document.querySelector("#reset-code"),
  resetPassword: document.querySelector("#reset-password"),
};

let debugStep = "";

// 认证页提示信息
function setMessage(text, type = "") {
  messageNode.textContent = text;
  messageNode.className = `auth-message ${type}`.trim();
}

// 记录 BCE 边界层步骤
function setDebugStep(step) {
  debugStep = step;
}

// 统一格式化错误信息
function getErrorMessage(error) {
  if (error instanceof Error) {
    return error.name && error.message ? `${error.name}: ${error.message}` : error.message;
  }

  if (typeof error === "string") {
    return error;
  }

  return "Unknown error";
}

// 捕获未处理前端异常
window.addEventListener("error", (event) => {
  const detail = [event.message, event.filename, event.lineno].filter(Boolean).join(" @ ");
  setMessage(`Frontend error at ${debugStep || "unknown step"}: ${detail || "Unknown error"}`, "error");
});

// 捕获未处理异步异常
window.addEventListener("unhandledrejection", (event) => {
  setMessage(
    `Unhandled error at ${debugStep || "unknown step"}: ${getErrorMessage(event.reason)}`,
    "error"
  );
});

// 切换认证界面
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
}

// 校验密码规则：至少 6 位，且同时包含字母和数字
function validatePasswordPolicy(password) {
  if (password.length < 6) {
    return "Password must be at least 6 characters.";
  }

  const hasLetter = /[A-Za-z]/.test(password);
  const hasDigit = /\d/.test(password);
  if (!hasLetter || !hasDigit) {
    return "Password must contain both letters and numbers.";
  }

  return "";
}

// 发送 JSON 请求
async function postJson(url, payload) {
  setDebugStep(`postJson -> ${url}`);
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  const data = await response.json();
  if (!response.ok) {
    if (typeof data.detail === "string") {
      throw new Error(data.detail);
    }
    if (Array.isArray(data.detail) && data.detail.length > 0) {
      throw new Error(
        data.detail
          .map((item) => item.msg || item.message)
          .filter(Boolean)
          .join("; ")
      );
    }
    throw new Error(typeof data.message === "string" ? data.message : "Request failed.");
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

// 登录账号
async function handleLogin() {
  try {
    setDebugStep("LoginPage -> EnterEmail");
    const payload = {
      email: fields.loginEmail?.value.trim() || "",
      password: fields.loginPassword?.value || "",
    };

    if (!payload.email || !payload.password) {
      setMessage("Enter both your email and password.", "error");
      return;
    }

    setMessage("Logging in...");
    const result = await postJson("/api/auth/login", payload);
    setMessage(result.message, "success");
    window.location.href = result.redirect || "/";
  } catch (error) {
    const message =
      error instanceof Error && error.message === "Invalid email or password."
        ? "The email or password you entered is incorrect."
        : getErrorMessage(error);
    setMessage(message, "error");
  }
}

// 注册账号
async function handleRegister() {
  try {
    let payload;

    try {
      setDebugStep("RegisterPage -> ReadUsername");
      const username = fields.registerUsername?.value.trim() || "";

      setDebugStep("RegisterPage -> ReadEmail");
      const email = fields.registerEmail?.value.trim() || "";

      setDebugStep("RegisterPage -> ReadPassword");
      const password = fields.registerPassword?.value || "";

      setDebugStep("RegisterPage -> ReadCode");
      const code = fields.registerCode?.value.trim() || "";

      payload = { username, email, password, code };
    } catch (error) {
      throw new Error(`Register field read failed at ${debugStep}: ${getErrorMessage(error)}`);
    }

    try {
      setDebugStep("RegisterPage -> ValidateRequiredFields");
      if (!payload.username || !payload.email || !payload.password || !payload.code) {
        setMessage("Complete all registration fields before submitting.", "error");
        return;
      }

      setDebugStep("RegisterPage -> ValidatePasswordPolicy");
      const passwordError = validatePasswordPolicy(payload.password);
      if (passwordError) {
        setMessage(passwordError, "error");
        return;
      }
    } catch (error) {
      throw new Error(`Register validation failed at ${debugStep}: ${getErrorMessage(error)}`);
    }

    setDebugStep("RegisterPage -> SubmitRegisterRequest");
    setMessage("Creating your account...");
    const result = await postJson("/api/auth/register", payload);

    try {
      setDebugStep("RegisterPage -> HandleRegisterResponse");
      setMessage(result.message, "success");
      if (result.redirect) {
        setDebugStep("RegisterPage -> RedirectAfterRegister");
        window.location.href = result.redirect;
      }
    } catch (error) {
      throw new Error(`Register response handling failed at ${debugStep}: ${getErrorMessage(error)}`);
    }
  } catch (error) {
    setMessage(getErrorMessage(error), "error");
  }
}

// 发送注册验证码
async function handleSendCode() {
  try {
    const email = fields.registerEmail?.value.trim() || "";
    if (!email) {
      setMessage("Enter your email before requesting a verification code.", "error");
      return;
    }

    setMessage("Sending verification code...");
    await postJson("/api/auth/send-code", { email });
    setMessage("Verification code sent. Check your inbox.", "success");
    startCooldown(sendCodeButton, 60);
  } catch (error) {
    setMessage(getErrorMessage(error), "error");
  }
}

// 发送重置密码验证码
async function handleSendResetCode() {
  try {
    const email = fields.forgotEmail?.value.trim() || "";
    if (!email) {
      setMessage("Enter your email before requesting a reset code.", "error");
      return;
    }

    setMessage("Sending password reset code...");
    await postJson("/api/auth/send-reset-code", { email });
    setMessage("Password reset code sent. Check your inbox.", "success");
    startCooldown(sendResetCodeButton, 60);
  } catch (error) {
    setMessage(getErrorMessage(error), "error");
  }
}

// 校验重置密码验证码
async function handleForgotPasswordVerification() {
  try {
    setDebugStep("ForgotPasswordPage -> EnterEmailAndCode");
    const payload = {
      email: fields.forgotEmail?.value.trim() || "",
      code: fields.forgotCode?.value.trim() || "",
    };

    if (!payload.email || !payload.code) {
      setMessage("Enter both your email and reset code.", "error");
      return;
    }

    setMessage("Verifying reset code...");
    const result = await postJson("/api/auth/verify-reset-code", payload);
    if (fields.resetEmail) {
      fields.resetEmail.value = payload.email;
    }
    if (fields.resetCode) {
      fields.resetCode.value = payload.code;
    }
    switchMode(result.next_mode || "reset");
    setMessage(result.message, "success");
  } catch (error) {
    setMessage(getErrorMessage(error), "error");
  }
}

// 重置密码
async function handleResetPassword() {
  try {
    setDebugStep("ForgotPasswordPage -> EnterResetPassword");
    const payload = {
      email: fields.resetEmail?.value.trim() || "",
      code: fields.resetCode?.value.trim() || "",
      password: fields.resetPassword?.value || "",
    };

    if (!payload.email || !payload.code || !payload.password) {
      setMessage("Complete all reset password fields before submitting.", "error");
      return;
    }

    const passwordError = validatePasswordPolicy(payload.password);
    if (passwordError) {
      setMessage(passwordError, "error");
      return;
    }

    setMessage("Updating password...");
    const result = await postJson("/api/auth/reset-password", payload);
    setMessage(result.message, "success");
    window.location.href = result.redirect || "/auth?mode=login";
  } catch (error) {
    setMessage(getErrorMessage(error), "error");
  }
}

tabButtons.forEach((button) => {
  button.addEventListener("click", () => switchMode(button.dataset.switch));
});

loginSubmitButton?.addEventListener("click", handleLogin);
registerSubmitButton?.addEventListener("click", handleRegister);
sendCodeButton?.addEventListener("click", handleSendCode);
sendResetCodeButton?.addEventListener("click", handleSendResetCode);
forgotSubmitButton?.addEventListener("click", handleForgotPasswordVerification);
resetSubmitButton?.addEventListener("click", handleResetPassword);

// 支持回车触发当前界面提交
document.addEventListener("keydown", (event) => {
  if (event.key !== "Enter") {
    return;
  }

  const activeMode = body.dataset.mode;
  if (activeMode === "login") {
    event.preventDefault();
    handleLogin();
  } else if (activeMode === "register") {
    event.preventDefault();
    handleRegister();
  } else if (activeMode === "forgot") {
    event.preventDefault();
    handleForgotPasswordVerification();
  } else if (activeMode === "reset") {
    event.preventDefault();
    handleResetPassword();
  }
});
